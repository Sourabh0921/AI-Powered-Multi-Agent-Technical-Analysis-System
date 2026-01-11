# workflow/nodes/technical_node.py
"""
Technical analysis node for workflow
"""
import pandas as pd
import json
import math
from typing import Dict, Any, Tuple
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import logging

from ..states import AnalysisState
from ..prompts import WorkflowPrompts

logger = logging.getLogger(__name__)


class TechnicalAnalysisNode:
    """Node for technical analysis using LLM"""
    
    def __init__(self, llm: ChatGroq):
        """
        Initialize technical analysis node
        
        Args:
            llm: ChatGroq LLM instance
        """
        self.llm = llm
        self.prompts = WorkflowPrompts()
    
    def process(self, state: AnalysisState) -> AnalysisState:
        """
        Perform technical analysis
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with technical analysis results
        """
        df = state['market_data']
        latest = df.iloc[-1]
        
        # Extract metrics
        metrics = self._extract_metrics(df, latest)
        
        # Build prompt
        fundamentals_str = state.get('fundamental_context', 'N/A')
        prompt = self.prompts.get_technical_prompt(
            ticker=state['ticker'],
            price=metrics['price'],
            rsi=metrics['rsi'],
            macd=metrics['macd'],
            signal=metrics['signal'],
            trend_20d=metrics['trend_20d'],
            fundamentals=fundamentals_str
        )
        
        # Get LLM response
        messages = [
            SystemMessage(content=self.prompts.TECHNICAL_SYSTEM),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        text = response.content or ""
        
        # Parse response
        summary, structured = self._parse_response(text)
        
        # Update state
        state['technical_analysis'] = summary
        state['technical_structured'] = structured
        state['messages'].append("✓ Technical analysis complete")
        
        logger.info(f"Technical analysis complete for {state['ticker']}")
        return state
    
    def _extract_metrics(self, df: pd.DataFrame, latest: pd.Series) -> Dict[str, Any]:
        """
        Extract technical metrics from dataframe
        
        Args:
            df: Market data DataFrame
            latest: Latest row of data
            
        Returns:
            Dictionary of technical metrics
        """
        def get_col(name: str) -> pd.Series:
            """Get column with case-insensitive matching"""
            return df[name] if name in df.columns else df.get(name.title(), pd.Series(dtype=float))
        
        # Get close price
        close = get_col('close') if 'close' in df.columns or 'Close' in df.columns else df.iloc[:, -1]
        price = float(close.iloc[-1]) if not math.isnan(float(close.iloc[-1])) else float(latest.get('close', latest.get('Close', 0)))
        
        # Get indicators
        rsi_val = float(latest.get('rsi', latest.get('RSI', 0)) or 0)
        macd_val = float(latest.get('macd', latest.get('MACD', 0)) or 0)
        signal_val = str(latest.get('signal', latest.get('Signal', '')))
        
        # Calculate 20-day trend
        trend_20d = float('nan')
        if len(close) >= 20:
            trend_20d = close.tail(20).pct_change().sum() * 100
        
        return {
            'price': price,
            'rsi': rsi_val,
            'macd': macd_val,
            'signal': signal_val,
            'trend_20d': trend_20d if not math.isnan(trend_20d) else 0.0
        }
    
    def _parse_response(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse LLM response into summary and structured data
        
        Args:
            text: Raw LLM response text
            
        Returns:
            Tuple of (summary_text, structured_dict)
        """
        summary = text
        structured: Dict[str, Any] = {}
        
        try:
            # Find last JSON block in the text
            start = text.rfind('{')
            end = text.rfind('}')
            
            if start != -1 and end != -1 and end > start:
                json_str = text[start:end+1]
                structured = json.loads(json_str)
                summary = text[:start].strip()
        except Exception as e:
            logger.warning(f"Failed to parse structured output: {e}")
            structured = {}
        
        return summary.strip() or text, structured
