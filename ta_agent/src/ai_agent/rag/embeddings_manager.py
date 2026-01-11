# rag/embeddings_manager.py
"""
Embeddings management using Google Generative AI
Handles embedding creation and configuration
"""
import logging
from typing import Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """
    Manages embeddings using Google Generative AI
    Provides high-quality embeddings for semantic search
    """
    
    # Default model
    DEFAULT_MODEL = "models/text-embedding-004"
    
    def __init__(self, google_api_key: Optional[str] = None):
        """
        Initialize embeddings manager
        
        Args:
            google_api_key: Google API key (optional if set in environment)
        """
        self.api_key = google_api_key
        self.model_name = self.DEFAULT_MODEL
        self.embeddings = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Google AI embeddings"""
        try:
            logger.info(f"Initializing Google AI Embeddings: {self.model_name}")
            
            if self.api_key:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=self.model_name,
                    google_api_key=self.api_key
                )
            else:
                # Will use GOOGLE_API_KEY from environment
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=self.model_name
                )
            
            logger.info("Google AI Embeddings initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def get_embeddings(self):
        """Get the embeddings instance"""
        return self.embeddings
    
    def get_model_info(self) -> dict:
        """
        Get information about the embeddings model
        
        Returns:
            Dict with model information
        """
        return {
            "provider": "Google Generative AI",
            "model": self.model_name,
            "description": "High-quality text embeddings for semantic search",
            "dimensions": "Variable (depends on model)",
            "api_based": True
        }
    
    def embed_query(self, text: str) -> list:
        """
        Embed a single query text
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Failed to embed query: {e}")
            raise
    
    def embed_documents(self, texts: list) -> list:
        """
        Embed multiple documents
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"Failed to embed documents: {e}")
            raise
