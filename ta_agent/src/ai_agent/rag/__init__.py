# rag/__init__.py
"""
RAG (Retrieval-Augmented Generation) Package
Modular implementation for document-based question answering
"""

from .rag_engine import RAGEngine
from .document_types import DocumentType

__all__ = ["RAGEngine", "DocumentType"]
