# rag/document_types.py
"""
Document type classifications for RAG system
"""
from enum import Enum


class DocumentType:
    """Document type classification constants"""
    FINANCIAL_REPORT = "financial_report"
    RESEARCH_PAPER = "research_paper"
    TRADING_STRATEGY = "trading_strategy"
    MARKET_NEWS = "market_news"
    PERSONAL_NOTES = "personal_notes"
    GENERAL = "general"
    
    @classmethod
    def get_all_types(cls) -> list:
        """Get all available document types"""
        return [
            cls.FINANCIAL_REPORT,
            cls.RESEARCH_PAPER,
            cls.TRADING_STRATEGY,
            cls.MARKET_NEWS,
            cls.PERSONAL_NOTES,
            cls.GENERAL
        ]
    
    @classmethod
    def get_description(cls, doc_type: str) -> str:
        """Get description for a document type"""
        descriptions = {
            cls.FINANCIAL_REPORT: "Annual reports, quarterly earnings, SEC filings, financial statements",
            cls.RESEARCH_PAPER: "Academic papers, market research, industry analysis, whitepapers",
            cls.TRADING_STRATEGY: "Trading plans, strategy documents, backtests, algorithmic strategies",
            cls.MARKET_NEWS: "News articles, market commentary, press releases, market updates",
            cls.PERSONAL_NOTES: "Trading journals, personal observations, notes, ideas",
            cls.GENERAL: "Any other document type"
        }
        return descriptions.get(doc_type, "Unknown document type")
