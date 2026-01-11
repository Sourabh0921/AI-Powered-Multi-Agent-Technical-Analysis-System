# rag/document_processor.py
"""
Document processing utilities
Handles chunking, classification, and metadata management
"""
from typing import List, Dict, Any
import hashlib
import logging
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .prompts import RAGPrompts

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processes documents for RAG system
    Handles chunking, classification, and metadata
    """
    
    def __init__(
        self,
        llm,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize document processor
        
        Args:
            llm: Language model for classification
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.llm = llm
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        logger.info(
            f"DocumentProcessor initialized: "
            f"chunk_size={chunk_size}, overlap={chunk_overlap}"
        )
    
    def generate_document_hash(self, content: str) -> str:
        """
        Generate MD5 hash for document deduplication
        
        Args:
            content: Document content
            
        Returns:
            MD5 hash string
        """
        return hashlib.md5(content.encode()).hexdigest()
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of document chunks
        """
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def classify_document_type(self, content: str) -> str:
        """
        Classify document type using LLM
        
        Args:
            content: Document content (first 2000 chars)
            
        Returns:
            Document type classification
        """
        prompt = ChatPromptTemplate.from_messages(
            RAGPrompts.get_document_classifier_prompt()
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            logger.info("Classifying document type...")
            doc_type = chain.invoke({"content": content[:2000]})
            doc_type = doc_type.strip().lower()
            logger.info(f"Document classified as: {doc_type}")
            return doc_type
        except Exception as e:
            logger.error(f"Document classification failed: {e}")
            return "general"
    
    def add_metadata_to_chunks(
        self,
        chunks: List[Document],
        base_metadata: Dict[str, Any]
    ) -> List[Document]:
        """
        Add metadata to document chunks
        
        Args:
            chunks: List of document chunks
            base_metadata: Base metadata to add to all chunks
            
        Returns:
            Chunks with added metadata
        """
        for i, chunk in enumerate(chunks):
            chunk.metadata.update(base_metadata)
            chunk.metadata["chunk_index"] = i
        
        logger.info(f"Added metadata to {len(chunks)} chunks")
        return chunks
    
    def prepare_document_metadata(
        self,
        file_path: str,
        doc_type: str,
        doc_hash: str,
        chunk_count: int,
        additional_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Prepare comprehensive metadata for document
        
        Args:
            file_path: Source file path
            doc_type: Document type classification
            doc_hash: Document hash
            chunk_count: Number of chunks
            additional_metadata: Additional metadata from user
            
        Returns:
            Complete metadata dictionary
        """
        metadata = {
            "source": str(file_path),
            "doc_type": doc_type,
            "doc_id": doc_hash,
            "ingestion_date": datetime.now().isoformat(),
            "chunk_count": chunk_count,
        }
        
        # Add additional metadata if provided
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return metadata
    
    def combine_document_pages(self, documents: List[Document]) -> str:
        """
        Combine all pages/sections of documents into single text
        
        Args:
            documents: List of documents
            
        Returns:
            Combined text content
        """
        return "\n\n".join([doc.page_content for doc in documents])
