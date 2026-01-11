# workflow/nodes/recommendation_node.py
"""
Final recommendation node for workflow
"""
import json
from typing import Dict, Any, Tuple
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import logging

from ..states import AnalysisState
from ..prompts import WorkflowPrompts

logger = logging.getLogger(__name__)


class RecommendationNode:
    """Node for generating final recommendation using LLM"""
    
    def __init__(self, llm: ChatGroq):
        """
        Initialize recommendation node
        
        Args:
            llm: ChatGroq LLM instance
        """
        self.llm = llm
        self.prompts = WorkflowPrompts()
    
    def process(self, state: AnalysisState) -> AnalysisState:
        """
        Generate final recommendation
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with final recommendation
        """
        # Build prompt
        fundamentals_str = state.get('fundamental_context', 'N/A')
        prompt = self.prompts.get_recommendation_prompt(
            ticker=state['ticker'],
            technical_summary=state['technical_analysis'],
            risk_summary=state['risk_assessment'],
            fundamentals=fundamentals_str
        )
        
        # Get LLM response
        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATION_SYSTEM),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        text = response.content or ""
        
        # Parse response
        summary, structured = self._parse_response(text)
        
        # Update state
        state['final_recommendation'] = summary
        state['recommendation_structured'] = structured
        state['messages'].append("✓ Final recommendation generated")
        
        logger.info(f"Final recommendation complete for {state['ticker']}")
        return state
    
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
