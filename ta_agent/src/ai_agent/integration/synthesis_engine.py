"""
Synthesis Engine Module
Combines document insights with technical analysis
"""
from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..rag.rag_engine import RAGEngine
from ...core.logging import logger


# Synthesis prompt
SYNTHESIS_SYSTEM_PROMPT = """You are a comprehensive financial analyst combining document analysis with real-time market data.

Your task:
1. Synthesize insights from documents AND technical analysis
2. Identify agreements or conflicts between sources
3. Provide actionable recommendations
4. Cite sources appropriately
5. Highlight key risks and opportunities
6. Be concise yet thorough

Format your response as:
## Summary
[Brief overview]

## Key Insights
- [Insight 1]
- [Insight 2]

## Technical Outlook
[If technical data available]

## Recommendation
[Actionable advice]

## Risk Factors
[Key risks to watch]"""

SYNTHESIS_USER_TEMPLATE = """Based on the following information:

{context}

Question: {question}

Provide a comprehensive integrated analysis."""


class SynthesisEngine:
    """
    Synthesizes document insights with technical analysis
    
    Combines:
    - RAG-based document insights
    - Technical analysis data
    - Market context
    - Source citations
    """
    
    def __init__(self, rag_engine: RAGEngine):
        """
        Initialize synthesis engine
        
        Args:
            rag_engine: RAG engine instance for LLM access
        """
        self.rag_engine = rag_engine
        self.llm = rag_engine.llm
    
    def generate_integrated_answer(
        self,
        question: str,
        rag_answer: str,
        technical_data: Optional[Dict[str, Any]] = None,
        sources: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate synthesized answer combining all available information
        
        Args:
            question: Original user question
            rag_answer: Answer from document RAG
            technical_data: Technical analysis data (optional)
            sources: Source documents (optional)
            
        Returns:
            Comprehensive integrated answer
        """
        logger.info("🔄 Synthesizing document + technical insights...")
        
        # Build context
        context_parts = [f"Document Insights:\n{rag_answer}"]
        
        # Add technical analysis if available
        if technical_data:
            tech_context = self._format_technical_context(technical_data)
            context_parts.append(tech_context)
        
        # Add source citations
        if sources:
            source_context = self._format_source_context(sources)
            context_parts.append(source_context)
        
        full_context = "\n".join(context_parts)
        
        # Generate synthesis using LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYNTHESIS_SYSTEM_PROMPT),
            ("human", SYNTHESIS_USER_TEMPLATE)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        synthesis = chain.invoke({
            "context": full_context,
            "question": question
        })
        
        return synthesis
    
    def _format_technical_context(self, technical_data: Dict[str, Any]) -> str:
        """
        Format technical analysis data for context
        
        Args:
            technical_data: Dictionary of technical analysis by ticker
            
        Returns:
            Formatted technical context string
        """
        tech_context = "\n\nTechnical Analysis:\n"
        
        for ticker, data in technical_data.items():
            if "error" in data:
                tech_context += f"\n{ticker}: Data unavailable - {data['error']}\n"
                continue
            
            tech_context += f"\n{ticker}:\n"
            
            # Price info
            if "current_price" in data:
                tech_context += f"  Current Price: ${data['current_price']:.2f}\n"
            
            # Indicators
            if "rsi" in data:
                tech_context += f"  RSI: {data['rsi']:.2f}\n"
            if "macd" in data:
                tech_context += f"  MACD: {data['macd']:.4f}\n"
            if "signal" in data:
                tech_context += f"  Signal: {data['signal']}\n"
            
            # Full analysis if available
            if "analysis" in data:
                analysis_preview = data['analysis'][:500]
                tech_context += f"  Analysis: {analysis_preview}...\n"
        
        return tech_context
    
    def _format_source_context(self, sources: List[Dict]) -> str:
        """
        Format source document information for context
        
        Args:
            sources: List of source documents
            
        Returns:
            Formatted source context string
        """
        if not sources:
            return ""
        
        source_context = "\n\nSource Documents:\n"
        
        for i, source in enumerate(sources[:3], 1):
            metadata = source.get('metadata', {})
            doc_type = source.get('doc_type', 'Unknown')
            source_name = metadata.get('source', 'Unknown')
            
            source_context += f"{i}. {source_name} ({doc_type})\n"
            
            # Add relevant metadata
            if 'ticker' in metadata:
                source_context += f"   Ticker: {metadata['ticker']}\n"
            if 'date' in metadata:
                source_context += f"   Date: {metadata['date']}\n"
        
        return source_context
    
    def create_summary(
        self,
        question: str,
        integrated_answer: str,
        technical_data: Optional[Dict] = None,
        sources: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Create a structured summary of the analysis
        
        Args:
            question: Original question
            integrated_answer: Synthesized answer
            technical_data: Technical analysis data
            sources: Source documents
            
        Returns:
            Structured summary dictionary
        """
        summary = {
            "question": question,
            "answer": integrated_answer,
            "data_sources": {
                "documents": len(sources) if sources else 0,
                "technical": list(technical_data.keys()) if technical_data else []
            }
        }
        
        # Extract key points from answer (simple heuristic)
        if "## Key Insights" in integrated_answer:
            insights_section = integrated_answer.split("## Key Insights")[1].split("##")[0]
            insights = [line.strip("- ").strip() for line in insights_section.split("\n") if line.strip().startswith("-")]
            summary["key_insights"] = insights[:5]  # Top 5
        
        # Extract recommendation if present
        if "## Recommendation" in integrated_answer:
            rec_section = integrated_answer.split("## Recommendation")[1].split("##")[0]
            summary["recommendation"] = rec_section.strip()
        
        return summary
