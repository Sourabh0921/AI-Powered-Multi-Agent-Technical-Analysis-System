# rag/query_processor.py
"""
Query processing and classification
Analyzes user queries and extracts intent
"""
from typing import Dict, Any
import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .prompts import RAGPrompts

logger = logging.getLogger(__name__)


class QueryProcessor:
    """
    Processes and classifies user queries
    Extracts intent, tickers, and required data sources
    """
    
    def __init__(self, llm):
        """
        Initialize query processor
        
        Args:
            llm: Language model for classification
        """
        self.llm = llm
        logger.info("QueryProcessor initialized")
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify query and extract intent
        
        Args:
            query: User query text
            
        Returns:
            Dict with classification results
        """
        prompt = ChatPromptTemplate.from_messages(
            RAGPrompts.get_query_classifier_prompt()
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            logger.info(f"Classifying query: {query[:100]}...")
            result = chain.invoke({"query": query})
            classification = json.loads(result)
            logger.info(f"Query type: {classification.get('query_type')}")
            return classification
            
        except json.JSONDecodeError as e:
            logger.warning(f"Query classification JSON parse error: {e}")
            return self._get_default_classification(query)
            
        except Exception as e:
            logger.error(f"Query classification failed: {e}")
            return self._get_default_classification(query)
    
    def _get_default_classification(self, query: str) -> Dict[str, Any]:
        """
        Get default classification when LLM fails
        
        Args:
            query: User query
            
        Returns:
            Default classification dict
        """
        return {
            "query_type": "document_search",
            "requires_documents": True,
            "requires_market_data": False,
            "tickers": [],
            "time_frame": None,
            "intent": query
        }
    
    def extract_tickers(self, query: str) -> list:
        """
        Extract stock tickers from query
        
        Args:
            query: User query
            
        Returns:
            List of ticker symbols
        """
        classification = self.classify_query(query)
        return classification.get("tickers", [])
    
    def requires_market_data(self, query: str) -> bool:
        """
        Check if query requires market data
        
        Args:
            query: User query
            
        Returns:
            True if market data is needed
        """
        classification = self.classify_query(query)
        return classification.get("requires_market_data", False)
    
    def get_query_intent(self, query: str) -> str:
        """
        Get the intent of the query
        
        Args:
            query: User query
            
        Returns:
            Intent description
        """
        classification = self.classify_query(query)
        return classification.get("intent", query)
