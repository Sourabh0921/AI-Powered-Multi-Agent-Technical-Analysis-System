# rag/vector_store.py
"""
Vector store management using FAISS
Handles document storage, retrieval, and similarity search
"""
from typing import List, Optional, Tuple
from pathlib import Path
import logging

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages FAISS vector store operations
    Handles document storage and similarity search
    """
    
    def __init__(self, storage_path: Path, embeddings):
        """
        Initialize vector store manager
        
        Args:
            storage_path: Path to store FAISS index
            embeddings: Embeddings instance
        """
        self.storage_path = storage_path / "faiss_index"
        self.embeddings = embeddings
        self.store = None
        
        logger.info(f"VectorStoreManager initialized: {self.storage_path}")
    
    def load_or_create(self) -> bool:
        """
        Load existing FAISS index or prepare for new one
        
        Returns:
            True if index was loaded, False if needs to be created
        """
        try:
            if self.storage_path.exists():
                logger.info("Loading existing FAISS index...")
                self.store = FAISS.load_local(
                    str(self.storage_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("FAISS index loaded successfully")
                return True
            else:
                logger.info("FAISS index will be created on first document ingestion")
                self.store = None
                return False
        except Exception as e:
            logger.warning(f"Could not load FAISS index: {e}. Will create new index.")
            self.store = None
            return False
    
    def create_index(self, documents: List[Document]) -> bool:
        """
        Create new FAISS index from documents
        
        Args:
            documents: List of documents to index
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Creating new FAISS index with {len(documents)} documents...")
            self.store = FAISS.from_documents(documents, self.embeddings)
            logger.info("FAISS index created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to existing index
        
        Args:
            documents: List of documents to add
            
        Returns:
            True if successful
        """
        try:
            if self.store is None:
                # Create new index if doesn't exist
                return self.create_index(documents)
            
            logger.info(f"Adding {len(documents)} documents to FAISS index...")
            self.store.add_documents(documents)
            logger.info("Documents added successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def save(self) -> bool:
        """
        Save FAISS index to disk
        
        Returns:
            True if successful
        """
        try:
            if self.store is None:
                logger.warning("No FAISS store to save")
                return False
            
            logger.info(f"Saving FAISS index to: {self.storage_path}")
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.store.save_local(str(self.storage_path))
            logger.info("FAISS index saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 5
    ) -> List[Document]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        if self.store is None:
            logger.warning("No FAISS store available for search")
            return []
        
        try:
            return self.store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with relevance scores
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum relevance score
            
        Returns:
            List of (document, score) tuples
        """
        if self.store is None:
            logger.warning("No FAISS store available for search")
            return []
        
        try:
            results = self.store.similarity_search_with_score(query, k=k)
            
            # Filter by score threshold if specified
            if score_threshold > 0:
                results = [
                    (doc, score) for doc, score in results
                    if score >= score_threshold
                ]
            
            return results
        except Exception as e:
            logger.error(f"Similarity search with score failed: {e}")
            raise
    
    def exists(self) -> bool:
        """Check if vector store exists"""
        return self.store is not None
    
    def get_stats(self) -> dict:
        """
        Get vector store statistics
        
        Returns:
            Dict with statistics
        """
        return {
            "exists": self.exists(),
            "storage_path": str(self.storage_path),
            "index_exists_on_disk": self.storage_path.exists()
        }
