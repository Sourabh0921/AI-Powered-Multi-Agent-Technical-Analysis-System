"""
Integrated RAG Agent
Unified agent combining document RAG with technical analysis
"""
from typing import Dict, Any, Optional, List
import pandas as pd

from ..rag.rag_engine import RAGEngine
from ..analyzers import LLMMarketAnalyzer
from ..agents import AutonomousTAAgent
from .query_processor import QueryProcessor
from .synthesis_engine import SynthesisEngine
from .chat_handler import ChatHandler
from ...core.logging import logger


class IntegratedRAGAgent:
    """
    Unified agent combining document RAG with technical analysis
    
    Features:
    - Document ingestion and querying
    - Technical analysis integration
    - Unified query interface
    - Conversational chat with memory
    - Multi-source synthesis
    
    Usage:
        agent = IntegratedRAGAgent()
        
        # Upload document
        agent.ingest_document("annual_report.pdf", {"ticker": "AAPL"})
        
        # Query with both document and market context
        result = agent.query(
            "What are the risks mentioned in the report and how does current price action look?",
            ticker="AAPL"
        )
    """
    
    def __init__(self, rag_storage_path: str = "./data/rag_storage"):
        """
        Initialize integrated RAG agent
        
        Args:
            rag_storage_path: Path to RAG storage directory
        """
        # Initialize core components
        self.rag_engine = RAGEngine(storage_path=rag_storage_path)
        self.market_analyzer = LLMMarketAnalyzer()
        self.autonomous_agent = AutonomousTAAgent()
        
        # Initialize modular components
        self.query_processor = QueryProcessor(self.rag_engine)
        self.synthesis_engine = SynthesisEngine(self.rag_engine)
        self.chat_handler = ChatHandler()
        
        logger.info("✅ Integrated RAG Agent initialized")
    
    def ingest_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest document into RAG system
        
        Args:
            file_path: Path to document
            metadata: Optional metadata (ticker, date, etc.)
            doc_type: Document type classification
        
        Returns:
            Ingestion result
        """
        logger.info(f"📄 Ingesting document: {file_path}")
        
        # Add doc_type to metadata if provided
        if metadata is None:
            metadata = {}
        if doc_type:
            metadata["doc_type"] = doc_type
            
        return self.rag_engine.ingest_document(file_path, metadata)
    
    def query(
        self,
        question: str,
        ticker: Optional[str] = None,
        include_technical_analysis: bool = True,
        period: str = "3mo"
    ) -> Dict[str, Any]:
        """
        Unified query interface combining documents and market data
        
        Args:
            question: User question
            ticker: Stock ticker (optional)
            include_technical_analysis: Include technical analysis
            period: Data period for technical analysis
        
        Returns:
            Comprehensive answer with sources
        """
        logger.info(f"🔍 Processing query: {question[:100]}...")
        
        result = {
            "question": question,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        # Extract tickers from query or use provided ticker
        tickers = self.query_processor.extract_tickers(question, ticker)
        
        # Get document-based insights
        rag_result = self.query_processor.get_document_insights(question)
        result["document_insights"] = {
            "answer": rag_result["answer"],
            "sources": rag_result["sources"],
            "retrieved_count": rag_result.get("retrieved_count", 0)
        }
        
        # Get technical analysis if tickers available
        technical_analyses = {}
        if tickers and include_technical_analysis:
            technical_analyses = self._fetch_technical_analyses(tickers, period)
        
        if technical_analyses:
            result["technical_analysis"] = technical_analyses
        
        # Generate integrated synthesis
        synthesis = self.synthesis_engine.generate_integrated_answer(
            question=question,
            rag_answer=rag_result["answer"],
            technical_data=technical_analyses if technical_analyses else None,
            sources=rag_result["sources"]
        )
        
        result["integrated_answer"] = synthesis
        result["query_classification"] = self.query_processor.classify_query(question)
        
        return result
    
    def _fetch_technical_analyses(
        self,
        tickers: List[str],
        period: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch technical analysis for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            period: Data period
            
        Returns:
            Dictionary mapping tickers to their technical analysis
        """
        technical_analyses = {}
        
        for ticker in tickers:
            try:
                # Fetch market data
                df = self.query_processor.fetch_technical_data(ticker, period)
                
                if df is None:
                    technical_analyses[ticker] = {
                        "error": "No market data available"
                    }
                    continue
                
                # Get LLM analysis
                technical_analysis = self.market_analyzer.analyze_market_data(df, ticker)
                
                # Get technical indicators
                indicators = self.query_processor.analyze_technical_indicators(df)
                
                technical_analyses[ticker] = {
                    "analysis": technical_analysis,
                    **indicators
                }
                
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                technical_analyses[ticker] = {
                    "error": f"Failed to fetch technical data: {str(e)}"
                }
        
        return technical_analyses
    
    def chat(
        self,
        message: str,
        ticker: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Conversational interface with memory
        
        Args:
            message: User message
            ticker: Optional ticker context
            conversation_history: Previous messages
        
        Returns:
            Response with answer and updated history
        """
        logger.info("💬 Processing chat message...")
        
        # Get response using query method
        result = self.query(message, ticker=ticker)
        
        # Process with chat handler to update history
        result = self.chat_handler.process_message(
            message=message,
            response=result,
            conversation_history=conversation_history
        )
        
        return result
    
    def get_document_list(self) -> List[Dict[str, Any]]:
        """List all ingested documents"""
        return self.rag_engine.list_documents()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.rag_engine.get_statistics()
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document"""
        return self.rag_engine.delete_document(doc_id)
    
    def get_conversation_summary(
        self,
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """
        Get summary of conversation
        
        Args:
            conversation_history: Conversation history
            
        Returns:
            Conversation statistics
        """
        return self.chat_handler.get_conversation_summary(conversation_history)
    
    def clear_conversation(self) -> Dict[str, str]:
        """Clear conversation history"""
        return self.chat_handler.clear_history()
