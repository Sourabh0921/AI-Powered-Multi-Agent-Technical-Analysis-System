# workflow/rag_analyzer.py
"""
RAG-based analyzer for pattern recognition
"""
from typing import List
import pandas as pd
import os
import logging

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from ...core.config import settings

logger = logging.getLogger(__name__)


class RAGAnalyzer:
    """
    RAG-based analyzer that can query historical patterns
    
    This class uses vector similarity search to find historical
    market patterns similar to current conditions and generates
    insights based on those patterns.
    
    Usage:
        analyzer = RAGAnalyzer()
        similar = analyzer.find_similar_patterns("RSI 70, MACD positive")
        analysis = analyzer.analyze_with_context(df, "AAPL")
    """
    
    def __init__(self):
        """Initialize RAG analyzer with embeddings and LLM"""
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Initialize LLM
        self.llm = ChatGroq(
            model=getattr(settings, 'DEFAULT_LLM_MODEL', "llama-3.1-70b-versatile"),
            temperature=0.3,
            groq_api_key=settings.GROQ_API_KEY,
        )
        
        # Vector store (to be populated with historical patterns)
        self.vectorstore = None
        
        logger.info("RAGAnalyzer initialized")
    
    def find_similar_patterns(self, current_pattern: str) -> List[str]:
        """
        Find similar historical patterns using RAG
        
        Args:
            current_pattern: Description of current market pattern
            
        Returns:
            List of similar historical pattern descriptions
        """
        if not self.vectorstore:
            logger.warning("Vector store not initialized, returning empty list")
            return []
        
        try:
            docs = self.vectorstore.similarity_search(current_pattern, k=3)
            patterns = [doc.page_content for doc in docs]
            logger.info(f"Found {len(patterns)} similar patterns")
            return patterns
        except Exception as e:
            logger.error(f"Pattern search failed: {e}")
            return []
    
    def analyze_with_context(self, df: pd.DataFrame, ticker: str) -> str:
        """
        Analyze using historical pattern context
        
        Args:
            df: Market data DataFrame
            ticker: Stock ticker symbol
            
        Returns:
            Analysis with historical context
        """
        try:
            latest = df.iloc[-1]
            
            # Build current pattern description
            pattern_desc = self._build_pattern_description(latest)
            
            # Find similar patterns
            similar_patterns = self.find_similar_patterns(pattern_desc)
            
            # Build context string
            context_str = "\n".join(similar_patterns) if similar_patterns else "None found"
            
            # Generate analysis with LLM
            messages = [
                SystemMessage(content="You are an expert at pattern recognition in markets."),
                HumanMessage(content=f"""Current pattern for {ticker}:
{pattern_desc}

Similar historical patterns:
{context_str}

What insights can you draw from these patterns?""")
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Analysis with context failed: {e}")
            return f"Analysis failed: {str(e)}"
    
    def _build_pattern_description(self, latest: pd.Series) -> str:
        """
        Build pattern description from latest data
        
        Args:
            latest: Latest row of market data
            
        Returns:
            Pattern description string
        """
        rsi = latest.get('rsi', latest.get('RSI', 0))
        macd = latest.get('macd', latest.get('MACD', 0))
        
        macd_direction = 'positive' if macd > 0 else 'negative'
        
        return f"RSI {rsi:.0f}, MACD {macd_direction}"
    
    def initialize_vectorstore(self, documents: List[str]):
        """
        Initialize vector store with historical pattern documents
        
        Args:
            documents: List of historical pattern descriptions
        """
        try:
            from langchain_community.vectorstores import Chroma
            from langchain_core.documents import Document
            
            docs = [Document(page_content=doc) for doc in documents]
            self.vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings
            )
            logger.info(f"Vector store initialized with {len(documents)} documents")
        except Exception as e:
            logger.error(f"Vector store initialization failed: {e}")
            self.vectorstore = None
