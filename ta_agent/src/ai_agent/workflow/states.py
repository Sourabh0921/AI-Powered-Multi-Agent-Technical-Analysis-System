# workflow/states.py
"""
State definitions for workflow execution
"""
from typing import TypedDict, Annotated, Sequence, Dict, Any
import pandas as pd
import operator


class AnalysisState(TypedDict):
    """State object for the analysis workflow"""
    ticker: str
    market_data: pd.DataFrame
    technical_analysis: str
    technical_structured: Dict[str, Any]
    fundamental_context: str
    fundamentals_structured: Dict[str, Any]
    risk_assessment: str
    risk_structured: Dict[str, Any]
    final_recommendation: str
    recommendation_structured: Dict[str, Any]
    messages: Annotated[Sequence[str], operator.add]


class WorkflowConfig(TypedDict):
    """Configuration for workflow execution"""
    include_fundamentals: bool
    include_risk: bool
    data_period: str
    structured_output: bool
