// src/services/queryService.ts - Query service
import api from './api';
import { Query, QueryCreate, QueryListResponse } from '../types';

export const queryService = {
  async createQuery(data: QueryCreate): Promise<Query> {
    // Use the new unified query endpoint that handles both general and stock analysis
    const response = await api.post<Query>('/queries/', data);
    return response.data;
  },

  async getQueries(skip: number = 0, limit: number = 20): Promise<QueryListResponse> {
    const response = await api.get<QueryListResponse>('/queries/', {
      params: { skip, limit },
    });
    return response.data;
  },

  async getQuery(id: number): Promise<Query> {
    const response = await api.get<Query>(`/queries/${id}`);
    return response.data;
  },

  async deleteQuery(id: number): Promise<void> {
    await api.delete(`/queries/${id}`);
  },
};
