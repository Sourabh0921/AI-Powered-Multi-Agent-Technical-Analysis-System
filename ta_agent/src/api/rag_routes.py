# rag_routes.py
"""
FastAPI routes for RAG document upload and QnA functionality
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
import shutil
from pathlib import Path
import uuid

from ..ai_agent.integration import IntegratedRAGAgent
# from ..core.dependencies import get_current_user  # If using auth


router = APIRouter(tags=["RAG"])

# Initialize RAG agent (singleton pattern)
rag_agent = None

def get_rag_agent() -> IntegratedRAGAgent:
    global rag_agent
    if rag_agent is None:
        rag_agent = IntegratedRAGAgent()
    return rag_agent


# Pydantic models
class QueryRequest(BaseModel):
    question: str
    ticker: Optional[str] = None
    include_technical_analysis: bool = True
    period: str = "3mo"


class ChatRequest(BaseModel):
    message: str
    ticker: Optional[str] = None
    conversation_history: Optional[List[dict]] = None


class DocumentMetadata(BaseModel):
    ticker: Optional[str] = None
    date: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None


# Routes
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    ticker: Optional[str] = Form(None),
    doc_type: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated
    # current_user: dict = Depends(get_current_user)  # Uncomment for auth
):
    """
    Upload a document for RAG ingestion
    
    Supported formats: PDF, DOCX, TXT, MD
    """
    agent = get_rag_agent()
    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.txt', '.md']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not supported. Allowed: {allowed_extensions}"
        )
    
    # Create upload directory
    upload_dir = Path("./data/uploaded_documents")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"
    
    try:
        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Prepare metadata
        metadata = {
            "original_filename": file.filename,
            "file_id": file_id,
            "description": description,
        }
        
        if ticker:
            metadata["ticker"] = ticker.upper()
        
        if tags:
            metadata["tags"] = [tag.strip() for tag in tags.split(",")]
        
        # Ingest document
        result = agent.ingest_document(
            str(file_path),
            metadata=metadata,
            doc_type=doc_type
        )
        
        if result["status"] == "success":
            return JSONResponse({
                "success": True,
                "message": "Document uploaded and ingested successfully",
                "data": {
                    "file_id": file_id,
                    "filename": file.filename,
                    "doc_id": result["doc_id"],
                    "doc_type": result["doc_type"],
                    "chunks": result["chunks"]
                }
            })
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Ingestion failed"))
    
    except Exception as e:
        # Cleanup on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    finally:
        file.file.close()


@router.post("/query")
async def query_rag(
    request: QueryRequest,
    # current_user: dict = Depends(get_current_user)  # Uncomment for auth
):
    """
    Query the RAG system with document and market context
    """
    agent = get_rag_agent()
    
    try:
        result = agent.query(
            question=request.question,
            ticker=request.ticker,
            include_technical_analysis=request.include_technical_analysis,
            period=request.period
        )
        
        return JSONResponse({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/chat")
async def chat_with_rag(
    request: ChatRequest,
    # current_user: dict = Depends(get_current_user)  # Uncomment for auth
):
    """
    Conversational chat interface with RAG
    """
    agent = get_rag_agent()
    
    try:
        result = agent.chat(
            message=request.message,
            ticker=request.ticker,
            conversation_history=request.conversation_history
        )
        
        return JSONResponse({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/documents")
async def list_documents(
    # current_user: dict = Depends(get_current_user)  # Uncomment for auth
):
    """
    List all ingested documents
    """
    agent = get_rag_agent()
    
    try:
        documents = agent.get_document_list()
        stats = agent.get_statistics()
        
        return JSONResponse({
            "success": True,
            "data": {
                "documents": documents,
                "statistics": stats
            }
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    # current_user: dict = Depends(get_current_user)  # Uncomment for auth
):
    """
    Delete a document from RAG system
    """
    agent = get_rag_agent()
    
    try:
        result = agent.delete_document(doc_id)
        
        return JSONResponse({
            "success": result["status"] == "success",
            "message": result["message"]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/statistics")
async def get_statistics(
    # current_user: dict = Depends(get_current_user)  # Uncomment for auth
):
    """
    Get RAG system statistics
    """
    agent = get_rag_agent()
    
    try:
        stats = agent.get_statistics()
        
        return JSONResponse({
            "success": True,
            "data": stats
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/health")
async def rag_health_check():
    """
    Check RAG system health
    """
    agent = get_rag_agent()
    
    return JSONResponse({
        "success": True,
        "status": "healthy",
        "data": {
            "rag_engine": "initialized",
            "document_count": len(agent.get_document_list())
        }
    })
