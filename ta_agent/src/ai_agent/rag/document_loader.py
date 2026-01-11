# rag/document_loader.py
"""
Document loading utilities for different file formats
Handles PDF, DOCX, TXT, and Markdown files
"""
from typing import List
from pathlib import Path
import logging

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Handles loading documents from various file formats
    Supports: PDF, DOCX, TXT, MD
    """
    
    # Supported file extensions and their loaders
    LOADERS = {
        '.pdf': PyPDFLoader,
        '.docx': Docx2txtLoader,
        '.txt': TextLoader,
        '.md': UnstructuredMarkdownLoader,
    }
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of supported file extensions"""
        return list(cls.LOADERS.keys())
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Check if file type is supported"""
        extension = Path(file_path).suffix.lower()
        return extension in cls.LOADERS
    
    @classmethod
    def load_document(cls, file_path: str) -> List[Document]:
        """
        Load document from file path
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
        """
        file_path = Path(file_path)
        
        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        extension = file_path.suffix.lower()
        loader_class = cls.LOADERS.get(extension)
        
        # Validate file type
        if not loader_class:
            supported = ', '.join(cls.LOADERS.keys())
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {supported}"
            )
        
        # Load document
        try:
            logger.info(f"Loading document: {file_path}")
            loader = loader_class(str(file_path))
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} pages/sections")
            return documents
        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            raise
    
    @classmethod
    def get_file_info(cls, file_path: str) -> dict:
        """
        Get information about a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict with file information
        """
        file_path = Path(file_path)
        
        return {
            "name": file_path.name,
            "extension": file_path.suffix.lower(),
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
            "supported": cls.is_supported(str(file_path)),
            "exists": file_path.exists()
        }
