# workflow/ta_workflow.py
"""
Main LangGraph workflow orchestrator for technical analysis
"""
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from typing import Dict, Any
import logging

from ...core.config import settings
from .states import AnalysisState
from .data_fetcher import MarketDataFetcher
from .nodes import TechnicalAnalysisNode, RiskAssessmentNode, RecommendationNode

logger = logging.getLogger(__name__)


class TAWorkflow:
    """
    LangGraph workflow for comprehensive technical analysis
    
    This orchestrates a 5-step analysis pipeline:
    1. Fetch market data
    2. Fetch fundamental context
    3. Technical analysis (with LLM)
    4. Risk assessment (with LLM)
    5. Final recommendation (with LLM)
    
    Usage:
        workflow = TAWorkflow()
        result = workflow.analyze('AAPL')
        print(result['final_recommendation'])
    """
    
    def __init__(self, data_period: str = '6mo'):
        """
        Initialize workflow
        
        Args:
            data_period: Historical data period (e.g., '6mo', '1y')
        """
        # Initialize LLM
        self.llm = ChatGroq(
            model=settings.DEFAULT_LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            groq_api_key=settings.GROQ_API_KEY
        )
        
        # Initialize components
        self.data_fetcher = MarketDataFetcher(period=data_period)
        self.technical_node = TechnicalAnalysisNode(self.llm)
        self.risk_node = RiskAssessmentNode(self.llm)
        self.recommendation_node = RecommendationNode(self.llm)
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        
        logger.info(f"TAWorkflow initialized with model: {settings.DEFAULT_LLM_MODEL}")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the analysis workflow graph
        
        Returns:
            Compiled StateGraph workflow
        """
        workflow = StateGraph(AnalysisState)
        
        # Add nodes
        workflow.add_node("fetch_data", self._fetch_data_node)
        workflow.add_node("fundamental_context", self._fundamental_context_node)
        workflow.add_node("technical_analysis", self.technical_node.process)
        workflow.add_node("risk_assessment", self.risk_node.process)
        workflow.add_node("generate_recommendation", self.recommendation_node.process)
        
        # Define edges (execution order)
        workflow.set_entry_point("fetch_data")
        workflow.add_edge("fetch_data", "fundamental_context")
        workflow.add_edge("fundamental_context", "technical_analysis")
        workflow.add_edge("technical_analysis", "risk_assessment")
        workflow.add_edge("risk_assessment", "generate_recommendation")
        workflow.add_edge("generate_recommendation", END)
        
        return workflow.compile()
    
    def _fetch_data_node(self, state: AnalysisState) -> AnalysisState:
        """
        Node: Fetch and prepare market data
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with market data
        """
        ticker = state['ticker']
        
        try:
            df = self.data_fetcher.fetch_price_data(ticker)
            state['market_data'] = df
            state['messages'].append(f"✓ Fetched data for {ticker}")
            logger.info(f"Data fetched successfully for {ticker}")
        except Exception as e:
            state['messages'].append(f"✗ Data fetch failed for {ticker}: {e}")
            logger.error(f"Data fetch failed for {ticker}: {e}")
            raise
        
        return state
    
    def _fundamental_context_node(self, state: AnalysisState) -> AnalysisState:
        """
        Node: Fetch lightweight fundamental context
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with fundamental context
        """
        ticker = state['ticker']
        
        try:
            fundamentals = self.data_fetcher.fetch_fundamentals(ticker)
            state['fundamentals_structured'] = fundamentals
            state['fundamental_context'] = self.data_fetcher.format_fundamentals(fundamentals)
            state['messages'].append("✓ Fundamentals context fetched")
            logger.info(f"Fundamentals fetched for {ticker}")
        except Exception as e:
            state['fundamentals_structured'] = {}
            state['fundamental_context'] = "N/A"
            state['messages'].append(f"! Fundamentals fetch failed: {e}")
            logger.warning(f"Fundamentals fetch failed for {ticker}: {e}")
        
        return state
    
    def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Run the complete analysis workflow
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'RELIANCE.NS')
            
        Returns:
            Dictionary with complete analysis results including:
            - ticker: Input ticker
            - market_data: DataFrame with price data
            - technical_analysis: Human-readable technical analysis
            - technical_structured: Structured technical data (JSON)
            - fundamental_context: Fundamental context string
            - fundamentals_structured: Structured fundamental data
            - risk_assessment: Human-readable risk assessment
            - risk_structured: Structured risk data (JSON)
            - final_recommendation: Human-readable recommendation
            - recommendation_structured: Structured recommendation (JSON)
            - messages: List of workflow execution messages
            
        Example:
            >>> workflow = TAWorkflow()
            >>> result = workflow.analyze('AAPL')
            >>> print(result['final_recommendation'])
            >>> print(result['recommendation_structured']['action'])  # BUY/SELL/HOLD
        """
        initial_state = {
            'ticker': ticker,
            'market_data': None,
            'technical_analysis': '',
            'technical_structured': {},
            'fundamental_context': '',
            'fundamentals_structured': {},
            'risk_assessment': '',
            'risk_structured': {},
            'final_recommendation': '',
            'recommendation_structured': {},
            'messages': []
        }
        
        logger.info(f"Starting workflow analysis for {ticker}")
        result = self.workflow.invoke(initial_state)
        logger.info(f"Workflow analysis complete for {ticker}")
        
        return result


if __name__ == '__main__':
    # Example usage
    workflow = TAWorkflow()
    result = workflow.analyze('AAPL')
    print(result['final_recommendation'])
