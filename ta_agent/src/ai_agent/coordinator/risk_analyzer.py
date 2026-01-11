"""
Risk Assessment Module
Analyzes volatility, drawdown, and other risk metrics
"""
from typing import Dict
import pandas as pd

from .constants import RISK_THRESHOLDS
from ...core.logging import logger


class RiskAnalyzer:
    """
    Risk Assessment Engine
    
    Analyzes:
    - Volatility (annualized standard deviation)
    - Maximum Drawdown
    - Beta (market correlation)
    - Risk scoring
    """
    
    def __init__(self):
        self.thresholds = RISK_THRESHOLDS
    
    def analyze(self, ticker: str, df: pd.DataFrame) -> Dict:
        """
        Perform comprehensive risk assessment
        
        Args:
            ticker: Stock ticker symbol
            df: DataFrame with OHLCV data
            
        Returns:
            Risk analysis result dictionary
        """
        logger.info(f"⚠️  Assessing risk metrics for {ticker}")
        
        # Calculate returns
        returns = df['close'].pct_change().dropna()
        
        # Calculate risk metrics
        volatility = self._calculate_volatility(returns)
        max_drawdown = self._calculate_max_drawdown(returns)
        beta = self._calculate_beta(returns)
        
        # Calculate risk score (0-100, higher = more risky)
        risk_score = self._calculate_risk_score(volatility, max_drawdown, beta)
        
        # Normalize to -1 to +1 (inverted, as higher risk = negative)
        normalized_score = 1 - (risk_score / 100)
        
        # Determine risk level
        risk_level = self._classify_risk_level(risk_score)
        
        return {
            'score': normalized_score,
            'risk_level': risk_level,
            'volatility': round(volatility, 2),
            'max_drawdown': round(max_drawdown, 2),
            'beta': round(beta, 2),
            'risk_score': risk_score,
            'recommendation': self._get_recommendation(risk_score)
        }
    
    def _calculate_volatility(self, returns: pd.Series) -> float:
        """Calculate annualized volatility (standard deviation)"""
        return returns.std() * (252 ** 0.5) * 100
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown percentage"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min() * 100
    
    def _calculate_beta(self, returns: pd.Series) -> float:
        """
        Calculate beta (market correlation)
        
        Note: In production, fetch SPY data for accurate beta.
        Using placeholder for now.
        """
        # TODO: Implement actual beta calculation with market index
        return 1.0  # Placeholder
    
    def _calculate_risk_score(self, volatility: float, max_drawdown: float, beta: float) -> float:
        """
        Calculate overall risk score (0-100)
        
        Higher score = higher risk
        """
        risk_score = 0
        
        # Volatility component (max 40 points)
        if volatility > self.thresholds['volatility']['high']:
            risk_score += 40
        elif volatility > self.thresholds['volatility']['moderate']:
            risk_score += 25
        elif volatility > self.thresholds['volatility']['low']:
            risk_score += 10
        
        # Drawdown component (max 30 points)
        if max_drawdown < self.thresholds['drawdown']['severe']:
            risk_score += 30
        elif max_drawdown < self.thresholds['drawdown']['high']:
            risk_score += 20
        elif max_drawdown < self.thresholds['drawdown']['moderate']:
            risk_score += 10
        
        # Beta component (max 20 points)
        if beta > self.thresholds['beta']['very_high']:
            risk_score += 20
        elif beta > self.thresholds['beta']['high']:
            risk_score += 10
        
        return min(100, risk_score)
    
    def _classify_risk_level(self, risk_score: float) -> str:
        """Classify risk score into risk level"""
        if risk_score < self.thresholds['score_levels']['low']:
            return "Low"
        elif risk_score < self.thresholds['score_levels']['moderate']:
            return "Moderate"
        else:
            return "High"
    
    def _get_recommendation(self, risk_score: float) -> str:
        """Get recommendation based on risk score"""
        if risk_score < 40:
            return 'Safe'
        elif risk_score < 70:
            return 'Caution'
        else:
            return 'High Risk'
