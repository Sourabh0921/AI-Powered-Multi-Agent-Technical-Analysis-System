// src/services/ragService.ts
/**
 * RAG (Retrieval Augmented Generation) Service
 * Handles document upload and RAG query endpoints
 */
import api from './api';

export interface DocumentUploadResponse {
  success: boolean;
  message: string;
  data: {
    file_id: string;
    filename: string;
    doc_id: string;
    doc_type: string;
    chunks: number;
  };
}

export interface RAGQueryRequest {
  question: string;
  ticker?: string;
  include_technical_analysis?: boolean;
  period?: string;
}

export interface RAGQueryResponse {
  question: string;
  timestamp: string;
  document_insights: {
    answer: string;
    sources: Array<{
      content: string;
      metadata: any;
      score: number;
    }>;
    retrieved_count: number;
  };
  technical_analysis?: any;
  integrated_answer?: string;
  query_classification?: any;
  summary?: string;
}

export interface RAGChatRequest {
  message: string;
  ticker?: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

/**
 * Upload a document for RAG ingestion
 */
export const uploadDocument = async (
  file: File,
  metadata?: {
    ticker?: string;
    doc_type?: string;
    description?: string;
    tags?: string;
  }
): Promise<DocumentUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (metadata?.ticker) formData.append('ticker', metadata.ticker);
  if (metadata?.doc_type) formData.append('doc_type', metadata.doc_type);
  if (metadata?.description) formData.append('description', metadata.description);
  if (metadata?.tags) formData.append('tags', metadata.tags);

  const response = await api.post('/rag/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Query the RAG system
 */
export const queryRAG = async (request: RAGQueryRequest): Promise<RAGQueryResponse> => {
  const response = await api.post('/rag/query', request);
  return response.data.data || response.data;
};

/**
 * Chat with RAG system
 */
export const chatWithRAG = async (request: RAGChatRequest): Promise<any> => {
  const response = await api.post('/rag/chat', request);
  return response.data;
};

/**
 * List uploaded documents
 */
export const listDocuments = async (): Promise<any> => {
  const response = await api.get('/rag/documents');
  return response.data;
};

/**
 * Delete a document
 */
export const deleteDocument = async (docId: string): Promise<any> => {
  const response = await api.delete(`/rag/documents/${docId}`);
  return response.data;
};
