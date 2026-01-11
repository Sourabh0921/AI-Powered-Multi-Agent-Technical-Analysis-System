# rag/answer_generator.py
"""
Answer generation using LLM with retrieved context
Generates comprehensive, cited answers from documents
"""
from typing import List, Dict
import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from .prompts import RAGPrompts

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """
    Generates answers using LLM and retrieved documents
    Provides comprehensive, well-cited responses
    """
    
    def __init__(self, llm):
        """
        Initialize answer generator
        
        Args:
            llm: Language model for generation
        """
        self.llm = llm
        logger.info("AnswerGenerator initialized")
    
    def generate_answer(
        self,
        question: str,
        documents: List[Document],
        query_info: Dict
    ) -> str:
        """
        Generate comprehensive answer from documents
        
        Args:
            question: User question
            documents: Retrieved documents
            query_info: Query classification info
            
        Returns:
            Generated answer with citations
        """
        # Build context from documents
        context = self._build_context(documents)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages(
            RAGPrompts.get_answer_generator_prompt()
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            logger.info("Generating answer from retrieved documents...")
            answer = chain.invoke({
                "context": context,
                "question": question,
                "query_type": query_info.get("query_type", "document_search"),
                "intent": query_info.get("intent", "general query"),
                "requires_market_data": query_info.get("requires_market_data", False)
            })
            
            logger.info("Answer generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return f"I encountered an error while generating the answer: {str(e)}"
    
    def generate_hybrid_answer(
        self,
        question: str,
        rag_answer: str,
        ticker: str,
        market_data: Dict
    ) -> str:
        """
        Generate integrated answer combining documents and market data
        
        Args:
            question: User question
            rag_answer: Answer from document RAG
            ticker: Stock ticker
            market_data: Market data dictionary
            
        Returns:
            Integrated answer
        """
        prompt = ChatPromptTemplate.from_messages(
            RAGPrompts.get_hybrid_integration_prompt()
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            logger.info("Generating hybrid answer with market context...")
            answer = chain.invoke({
                "rag_answer": rag_answer,
                "ticker": ticker or "Not specified",
                "market_data": json.dumps(market_data, indent=2) if market_data else "Not provided",
                "question": question
            })
            
            logger.info("Hybrid answer generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Hybrid answer generation failed: {e}")
            return rag_answer  # Fallback to RAG answer
    
    def _build_context(self, documents: List[Document]) -> str:
        """
        Build context string from retrieved documents
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, doc in enumerate(documents):
            # Extract metadata
            doc_type = doc.metadata.get('doc_type', 'unknown')
            source = doc.metadata.get('original_filename') or doc.metadata.get('source', 'unknown')
            ticker = doc.metadata.get('ticker', '')
            
            # Build header
            header = f"[Source {i+1} - {doc_type.replace('_', ' ').title()}"
            if ticker:
                header += f" - {ticker}"
            header += f"]"
            
            # Add to context
            context_parts.append(f"{header}:\n{doc.page_content}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def format_sources(
        self,
        documents: List[Document],
        scores: List[float]
    ) -> List[Dict]:
        """
        Format retrieved documents as source citations
        
        Args:
            documents: Retrieved documents
            scores: Relevance scores
            
        Returns:
            List of formatted source dicts
        """
        sources = []
        
        for doc, score in zip(documents, scores):
            sources.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
                "doc_type": doc.metadata.get("doc_type", "unknown"),
                "source": doc.metadata.get("source", "unknown"),
                "ticker": doc.metadata.get("ticker", None),
                "chunk_index": doc.metadata.get("chunk_index", 0)
            })
        
        return sources
