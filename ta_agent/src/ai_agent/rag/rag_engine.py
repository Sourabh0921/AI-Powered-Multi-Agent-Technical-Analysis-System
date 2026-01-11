# rag/rag_engine.py
"""
RAG Engine - Main orchestrator for Retrieval-Augmented Generation
Coordinates all RAG components: loading, processing, storage, and querying
"""
from typing import List, Dict, Optional, Any
from pathlib import Path
import os
import logging
from datetime import datetime

from langchain_groq import ChatGroq
from dotenv import load_dotenv

from .document_loader import DocumentLoader
from .document_processor import DocumentProcessor
from .embeddings_manager import EmbeddingsManager
from .vector_store import VectorStoreManager
from .query_processor import QueryProcessor
from .answer_generator import AnswerGenerator
from .document_types import DocumentType

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Main RAG Engine coordinating all components
    
    Architecture:
    - DocumentLoader: Loads files (PDF, DOCX, TXT, MD)
    - DocumentProcessor: Chunks, classifies, adds metadata
    - EmbeddingsManager: Creates embeddings with Google AI
    - VectorStoreManager: Stores and retrieves with FAISS
    - QueryProcessor: Classifies queries and extracts intent
    - AnswerGenerator: Generates comprehensive answers
    
    Usage:
        engine = RAGEngine()
        engine.ingest_document("report.pdf", ticker="AAPL")
        result = engine.query("What was the revenue?")
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        google_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None
    ):
        """
        Initialize RAG Engine with all components
        
        Args:
            storage_path: Path to store FAISS index
            google_api_key: Google API key for embeddings
            groq_api_key: Groq API key for LLM
        """
        # Load environment variables
        load_dotenv()
        
        # Set API keys
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        # Set storage path
        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent.parent / "data" / "rag_storage"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing RAG Engine at: {self.storage_path}")
        
        # Initialize LLM
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            groq_api_key=self.groq_api_key,
            temperature=0.1
        )
        
        # Initialize all components
        self.embeddings_manager = EmbeddingsManager(self.google_api_key)
        self.vector_store = VectorStoreManager(
            self.storage_path,
            self.embeddings_manager.get_embeddings()
        )
        self.document_processor = DocumentProcessor(
            self.llm,
            chunk_size=1000,
            chunk_overlap=200
        )
        self.query_processor = QueryProcessor(self.llm)
        self.answer_generator = AnswerGenerator(self.llm)
        
        # Load existing index
        self.vector_store.load_or_create()
        
        # Track ingested documents
        self.document_registry = {}
        self._load_document_registry()
        
        logger.info("RAG Engine initialized successfully")
    
    def ingest_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest a document into the RAG system
        
        Process:
        1. Load document from file
        2. Classify document type
        3. Split into chunks
        4. Create embeddings
        5. Store in vector database
        
        Args:
            file_path: Path to document file
            metadata: Additional metadata (ticker, doc_type, description, tags)
            
        Returns:
            Dict with ingestion status and document info
        """
        try:
            logger.info(f"Starting document ingestion: {file_path}")
            start_time = datetime.now()
            
            # Step 1: Load document
            documents = DocumentLoader.load_document(file_path)
            full_content = self.document_processor.combine_document_pages(documents)
            
            # Step 2: Generate hash for deduplication
            doc_hash = self.document_processor.generate_document_hash(full_content)
            
            # Check for duplicates
            if doc_hash in self.document_registry:
                logger.warning(f"Document already exists: {doc_hash}")
                return {
                    "status": "duplicate",
                    "doc_id": doc_hash,
                    "message": "Document already ingested"
                }
            
            # Step 3: Classify document type
            provided_doc_type = metadata.get("doc_type") if metadata else None
            if provided_doc_type:
                doc_type = provided_doc_type
                logger.info(f"Using provided document type: {doc_type}")
            else:
                doc_type = self.document_processor.classify_document_type(full_content)
            
            # Step 4: Split into chunks
            chunks = self.document_processor.split_documents(documents)
            
            # Step 5: Prepare metadata
            base_metadata = self.document_processor.prepare_document_metadata(
                file_path=file_path,
                doc_type=doc_type,
                doc_hash=doc_hash,
                chunk_count=len(chunks),
                additional_metadata=metadata
            )
            
            # Add filename to metadata
            base_metadata["original_filename"] = Path(file_path).name
            
            # Step 6: Add metadata to chunks
            chunks = self.document_processor.add_metadata_to_chunks(chunks, base_metadata)
            
            # Step 7: Store in vector database
            self.vector_store.add_documents(chunks)
            self.vector_store.save()
            
            # Step 8: Register document
            self.document_registry[doc_hash] = {
                "doc_id": doc_hash,
                "filename": Path(file_path).name,
                "doc_type": doc_type,
                "chunks": len(chunks),
                "ingestion_date": base_metadata["ingestion_date"],
                "metadata": metadata or {}
            }
            self._save_document_registry()
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Document ingestion complete: {doc_hash} ({duration:.2f}s)")
            
            return {
                "status": "success",
                "doc_id": doc_hash,
                "filename": Path(file_path).name,
                "doc_type": doc_type,
                "chunks": len(chunks),
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def query(
        self,
        question: str,
        k: int = 5,
        score_threshold: float = 0.0,
        doc_type_filter: Optional[str] = None,
        ticker_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Process:
        1. Classify query intent
        2. Search vector store
        3. Generate comprehensive answer
        4. Return answer with sources
        
        Args:
            question: User question
            k: Number of documents to retrieve
            score_threshold: Minimum relevance score
            doc_type_filter: Filter by document type
            ticker_filter: Filter by ticker symbol
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            logger.info(f"Processing query: {question[:100]}...")
            start_time = datetime.now()
            
            # Step 1: Classify query
            query_info = self.query_processor.classify_query(question)
            
            # Step 2: Search vector store
            results = self.vector_store.similarity_search_with_score(
                question,
                k=k,
                score_threshold=score_threshold
            )
            
            if not results:
                return {
                    "answer": "I couldn't find any relevant documents to answer your question. Please try uploading relevant documents first.",
                    "sources": [],
                    "query_classification": query_info,
                    "message": "No documents found"
                }
            
            # Step 3: Apply filters if specified
            if doc_type_filter or ticker_filter:
                results = self._filter_results(results, doc_type_filter, ticker_filter)
            
            # Separate documents and scores
            documents = [doc for doc, _ in results]
            scores = [score for _, score in results]
            
            # Step 4: Generate answer
            answer = self.answer_generator.generate_answer(
                question,
                documents,
                query_info
            )
            
            # Step 5: Format sources
            sources = self.answer_generator.format_sources(documents, scores)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Query processed successfully ({duration:.2f}s)")
            
            return {
                "answer": answer,
                "sources": sources,
                "query_classification": query_info,
                "num_sources": len(sources),
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "answer": f"An error occurred while processing your query: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def chat(
        self,
        question: str,
        history: Optional[List[Dict[str, str]]] = None,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Conversational interface with chat history
        
        Args:
            question: User question
            history: Chat history [{"role": "user/assistant", "content": "..."}]
            k: Number of documents to retrieve
            
        Returns:
            Dict with answer and updated history
        """
        # For now, just use regular query
        # TODO: Implement proper chat history integration
        result = self.query(question, k=k)
        
        # Build history
        if history is None:
            history = []
        
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": result["answer"]})
        
        result["history"] = history
        return result
    
    def get_document_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all ingested documents
        
        Returns:
            List of document info dictionaries
        """
        return list(self.document_registry.values())
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Delete a document from the system
        
        Note: Currently only removes from registry.
        FAISS doesn't support deletion without rebuild.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            Status dict
        """
        if doc_id in self.document_registry:
            doc_info = self.document_registry.pop(doc_id)
            self._save_document_registry()
            logger.info(f"Document removed from registry: {doc_id}")
            return {
                "status": "success",
                "message": "Document removed from registry. Rebuild index to remove from search.",
                "doc_info": doc_info
            }
        else:
            return {
                "status": "error",
                "message": "Document not found"
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get RAG system statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            "storage_path": str(self.storage_path),
            "total_documents": len(self.document_registry),
            "vector_store": self.vector_store.get_stats(),
            "embeddings_model": self.embeddings_manager.get_model_info(),
            "supported_formats": DocumentLoader.get_supported_extensions()
        }
    
    def _filter_results(
        self,
        results: List[tuple],
        doc_type_filter: Optional[str],
        ticker_filter: Optional[str]
    ) -> List[tuple]:
        """Filter search results by metadata"""
        filtered = []
        for doc, score in results:
            if doc_type_filter and doc.metadata.get("doc_type") != doc_type_filter:
                continue
            if ticker_filter and doc.metadata.get("ticker") != ticker_filter:
                continue
            filtered.append((doc, score))
        return filtered
    
    def _load_document_registry(self):
        """Load document registry from disk"""
        registry_path = self.storage_path / "document_registry.json"
        if registry_path.exists():
            import json
            with open(registry_path, 'r') as f:
                self.document_registry = json.load(f)
            logger.info(f"Loaded {len(self.document_registry)} documents from registry")
    
    def _save_document_registry(self):
        """Save document registry to disk"""
        registry_path = self.storage_path / "document_registry.json"
        import json
        with open(registry_path, 'w') as f:
            json.dump(self.document_registry, f, indent=2)
        logger.info("Document registry saved")
