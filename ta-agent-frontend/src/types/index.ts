// src/types/index.ts - Type definitions
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email_or_username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Query {
  id: number;
  user_id: number;
  query_text: string;
  query_type: string;
  ticker?: string;
  result?: any;
  status: 'pending' | 'completed' | 'failed';
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface QueryCreate {
  query_text: string;
  query_type: string;
  ticker?: string;
}

export interface QueryListResponse {
  total: number;
  queries: Query[];
}
