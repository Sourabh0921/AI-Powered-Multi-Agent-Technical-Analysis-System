# workflow/nodes/risk_node.py
"""
Risk assessment node for workflow
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


class RiskAssessmentNode:
    """Node for risk assessment using LLM"""
    
    def __init__(self, llm: ChatGroq):
        """
        Initialize risk assessment node
        
        Args:
            llm: ChatGroq LLM instance
        """
        self.llm = llm
        self.prompts = WorkflowPrompts()
    
    def process(self, state: AnalysisState) -> AnalysisState:
        """
        Assess risk for the ticker
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with risk assessment results
        """
        df = state['market_data']
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(df)
        
        # Build prompt
        prompt = self.prompts.get_risk_prompt(
            ticker=state['ticker'],
            volatility_20d=risk_metrics['volatility_20d'],
            max_drawdown=risk_metrics['max_drawdown_60d'],
            atr_14=risk_metrics['atr_14'] if not math.isnan(risk_metrics['atr_14']) else 'N/A',
            technical_summary=state['technical_analysis']
        )
        
        # Get LLM response
        messages = [
            SystemMessage(content=self.prompts.RISK_SYSTEM),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        text = response.content or ""
        
        # Parse response
        summary, structured = self._parse_response(text)
        
        # Update state
        state['risk_assessment'] = summary
        state['risk_structured'] = structured
        state['messages'].append("✓ Risk assessment complete")
        
        logger.info(f"Risk assessment complete for {state['ticker']}")
        return state
    
    def _calculate_risk_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate risk metrics from market data
        
        Args:
            df: Market data DataFrame
            
        Returns:
            Dictionary of risk metrics
        """
        def col(series_name: str) -> pd.Series:
            """Get column with case-insensitive matching"""
            return df.get(series_name) or df.get(series_name.title()) or pd.Series(dtype=float)
        
        # Get price series
        close = col('close')
        if close.empty and 'Close' in df.columns:
            close = df['Close']
        
        # Calculate volatility (20-day)
        vol_20d = float('nan')
        if len(close) >= 21:
            vol_20d = float(close.pct_change().tail(20).std() * 100)
        
        # Calculate max drawdown (60-day)
        max_drawdown = float('nan')
        window_60 = close.tail(60) if len(close) >= 60 else close
        if not window_60.empty:
            max_drawdown = float((window_60.max() - window_60.min()) / (window_60.max() + 1e-9) * 100)
        
        # Calculate ATR(14)
        atr_14 = self._calculate_atr(df)
        
        return {
            'volatility_20d': vol_20d if not math.isnan(vol_20d) else 0.0,
            'max_drawdown_60d': max_drawdown if not math.isnan(max_drawdown) else 0.0,
            'atr_14': atr_14
        }
    
    def _calculate_atr(self, df: pd.DataFrame) -> float:
        """
        Calculate Average True Range (14-period)
        
        Args:
            df: Market data DataFrame
            
        Returns:
            ATR value
        """
        try:
            high = df.get('high') or df.get('High')
            low = df.get('low') or df.get('Low')
            close = df.get('close') or df.get('Close')
            
            if all(not s.empty for s in [high, low, close]) and len(close) >= 15:
                prev_close = close.shift(1)
                
                # True Range = max(H-L, |H-Cp|, |L-Cp|)
                tr = pd.concat([
                    (high - low).abs(),
                    (high - prev_close).abs(),
                    (low - prev_close).abs()
                ], axis=1).max(axis=1)
                
                atr = float(tr.rolling(14).mean().iloc[-1])
                return atr
        except Exception as e:
            logger.warning(f"ATR calculation failed: {e}")
        
        return float('nan')
    
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
            # Find last JSON block
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
