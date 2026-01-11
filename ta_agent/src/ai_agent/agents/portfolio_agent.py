# agents/portfolio_agent.py
"""
Portfolio Analysis Agent
Specialized agent for portfolio-level analysis with multi-market support
"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Optional, Dict, List
from datetime import datetime
import logging

from ...core.config import settings
from .ta_agent import AutonomousTAAgent
from .market_info import MarketDetector
from .utils import WeightValidator
from .prompts import AgentPrompts

logger = logging.getLogger(__name__)


class PortfolioAnalysisAgent:
    """
    Portfolio Analysis Agent
    
    Capabilities:
    - Portfolio-level analysis with multi-market support
    - Diversification assessment across different markets and currencies
    - Risk-adjusted return analysis
    - Rebalancing recommendations
    - Currency risk evaluation
    
    Usage:
        agent = PortfolioAnalysisAgent()
        result = agent.analyze_portfolio(
            tickers=['AAPL', 'RELIANCE.NS', 'MSFT'],
            weights={'AAPL': 0.4, 'RELIANCE.NS': 0.3, 'MSFT': 0.3},
            base_currency='USD'
        )
    """
    
    def __init__(self, model: str = "openai/gpt-oss-120b", temperature: float = 0.3):
        """
        Initialize Portfolio Agent
        
        Args:
            model: LLM model to use
            temperature: LLM temperature (lower for more consistent analysis)
        """
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=settings.GROQ_API_KEY
        )
        self.ta_agent = AutonomousTAAgent(temperature=0.5)
        self.market_detector = MarketDetector()
        self.weight_validator = WeightValidator()
        
        logger.info(f"PortfolioAnalysisAgent initialized with model: {model}")
    
    def analyze_portfolio(
        self, 
        tickers: List[str], 
        weights: Optional[Dict[str, float]] = None,
        base_currency: str = "USD"
    ) -> str:
        """
        Analyze an entire portfolio with multi-market and multi-currency support
        
        Args:
            tickers: List of ticker symbols (can be from different markets)
            weights: Optional dict of ticker -> weight (0-1), must sum to 1.0
            base_currency: Base currency for portfolio (USD, INR, EUR, etc.)
            
        Returns:
            Comprehensive portfolio analysis
        """
        logger.info(f"Analyzing portfolio with {len(tickers)} holdings, base currency: {base_currency}")
        
        # Handle weights
        if weights is None:
            weights = self.weight_validator.create_equal_weights(tickers)
        else:
            # Validate and normalize weights
            if not self.weight_validator.validate_weights(weights):
                logger.warning("Weights don't sum to 1.0, normalizing...")
                weights = self.weight_validator.normalize_weights(weights)
        
        # Get market distribution
        market_distribution = self.market_detector.get_market_distribution(tickers, weights)
        
        # Build portfolio summary
        portfolio_summary = self._build_portfolio_summary(
            tickers, weights, market_distribution, base_currency
        )
        
        # Get individual analyses
        logger.info("Analyzing individual holdings...")
        analyses = self.ta_agent.batch_analyze(tickers, analysis_type="comprehensive")
        
        # Add individual analyses to summary
        portfolio_summary += self._format_individual_analyses(tickers, weights, analyses)
        
        # Get portfolio-level synthesis
        logger.info("Generating portfolio-level synthesis...")
        portfolio_query = AgentPrompts.get_portfolio_query(portfolio_summary, base_currency)
        
        messages = [
            SystemMessage(content=AgentPrompts.get_portfolio_system_prompt()),
            HumanMessage(content=portfolio_query)
        ]
        
        response = self.llm.invoke(messages)
        
        logger.info("Portfolio analysis complete")
        return response.content
    
    def _build_portfolio_summary(
        self,
        tickers: List[str],
        weights: Dict[str, float],
        market_distribution: Dict[str, float],
        base_currency: str
    ) -> str:
        """Build portfolio summary header"""
        summary = f"""PORTFOLIO COMPOSITION:

Total Holdings: {len(tickers)}
Base Currency: {base_currency}
Markets: {', '.join(market_distribution.keys())}

MARKET ALLOCATION:
"""
        for market, allocation in market_distribution.items():
            summary += f"- {market}: {allocation*100:.1f}%\n"
        
        summary += "\n\nINDIVIDUAL HOLDING ANALYSIS:\n"
        summary += "="*80 + "\n\n"
        
        return summary
    
    def _format_individual_analyses(
        self,
        tickers: List[str],
        weights: Dict[str, float],
        analyses: Dict[str, Dict]
    ) -> str:
        """Format individual stock analyses"""
        formatted = ""
        
        for ticker in tickers:
            weight_pct = weights.get(ticker, 0) * 100
            analysis_data = analyses.get(ticker, {})
            
            if "error" in analysis_data:
                formatted += f"**{ticker}** ({weight_pct:.1f}% weight):\n"
                formatted += f"Error: {analysis_data['error']}\n\n"
            else:
                market = analysis_data.get('market', 'Unknown')
                currency = analysis_data.get('currency', 'Unknown')
                analysis = analysis_data.get('analysis', 'No analysis available')
                
                formatted += f"**{ticker}** ({weight_pct:.1f}% weight | {market} | {currency}):\n"
                formatted += analysis + "\n\n"
                formatted += "-"*80 + "\n\n"
        
        return formatted
    
    def get_diversification_score(
        self,
        tickers: List[str],
        weights: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Calculate diversification score for portfolio
        
        Args:
            tickers: List of tickers
            weights: Portfolio weights
            
        Returns:
            Dictionary with diversification metrics
        """
        market_distribution = self.market_detector.get_market_distribution(tickers, weights)
        
        # Calculate concentration (Herfindahl index)
        herfindahl = sum(w**2 for w in weights.values())
        
        # Calculate market concentration
        market_concentration = sum(w**2 for w in market_distribution.values())
        
        # Diversification score (0-100, higher is better)
        diversification_score = (1 - herfindahl) * 100
        market_diversification_score = (1 - market_concentration) * 100
        
        return {
            "diversification_score": round(diversification_score, 2),
            "market_diversification_score": round(market_diversification_score, 2),
            "concentration_risk": "High" if herfindahl > 0.3 else "Medium" if herfindahl > 0.2 else "Low",
            "num_holdings": len(tickers),
            "num_markets": len(market_distribution),
            "market_distribution": market_distribution
        }
    
    def suggest_rebalancing(
        self,
        tickers: List[str],
        current_weights: Dict[str, float],
        target_allocation: Optional[Dict[str, float]] = None
    ) -> Dict[str, any]:
        """
        Suggest portfolio rebalancing
        
        Args:
            tickers: List of tickers
            current_weights: Current portfolio weights
            target_allocation: Optional target allocation
            
        Returns:
            Rebalancing recommendations
        """
        if target_allocation is None:
            # Default: equal weight
            target_allocation = self.weight_validator.create_equal_weights(tickers)
        
        # Calculate differences
        rebalancing_needed = {}
        for ticker in tickers:
            current = current_weights.get(ticker, 0)
            target = target_allocation.get(ticker, 0)
            diff = target - current
            
            if abs(diff) > 0.01:  # Threshold of 1%
                rebalancing_needed[ticker] = {
                    "current": round(current * 100, 2),
                    "target": round(target * 100, 2),
                    "adjustment": round(diff * 100, 2),
                    "action": "BUY" if diff > 0 else "SELL"
                }
        
        return {
            "needs_rebalancing": len(rebalancing_needed) > 0,
            "adjustments": rebalancing_needed,
            "total_adjustments": len(rebalancing_needed)
        }
    
    def analyze_currency_risk(
        self,
        tickers: List[str],
        weights: Dict[str, float],
        base_currency: str
    ) -> Dict[str, any]:
        """
        Analyze currency exposure and risk
        
        Args:
            tickers: List of tickers
            weights: Portfolio weights
            base_currency: Base currency
            
        Returns:
            Currency risk analysis
        """
        currency_exposure = {}
        
        for ticker in tickers:
            currency = self.market_detector.get_currency(ticker)
            weight = weights.get(ticker, 0)
            currency_exposure[currency] = currency_exposure.get(currency, 0) + weight
        
        # Calculate currency concentration
        max_currency_exposure = max(currency_exposure.values())
        
        risk_level = "High" if max_currency_exposure > 0.7 else \
                    "Medium" if max_currency_exposure > 0.5 else "Low"
        
        return {
            "base_currency": base_currency,
            "currency_exposure": {
                curr: round(exp * 100, 2) 
                for curr, exp in currency_exposure.items()
            },
            "currency_risk_level": risk_level,
            "num_currencies": len(currency_exposure),
            "needs_hedging": max_currency_exposure > 0.7 and base_currency not in currency_exposure
        }
