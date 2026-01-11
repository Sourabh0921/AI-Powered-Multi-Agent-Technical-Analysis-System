// src/store/querySlice.ts - Redux query slice
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { queryService } from '../services/queryService';
import { Query, QueryCreate, QueryListResponse } from '../types';

interface QueryState {
  queries: Query[];
  currentQuery: Query | null;
  comparisonData: any | null; // Add comparison data
  total: number;
  loading: boolean;
  error: string | null;
}

const initialState: QueryState = {
  queries: [],
  currentQuery: null,
  comparisonData: null, // Initialize comparison data
  total: 0,
  loading: false,
  error: null,
};

export const createQuery = createAsyncThunk(
  'query/create',
  async (data: QueryCreate, { rejectWithValue }) => {
    try {
      return await queryService.createQuery(data);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to create query';
      if (Array.isArray(error.response?.data?.detail)) {
        const messages = error.response.data.detail.map((err: any) => err.msg || err).join(', ');
        return rejectWithValue(messages);
      }
      return rejectWithValue(typeof errorMessage === 'string' ? errorMessage : 'Failed to create query');
    }
  }
);

export const fetchQueries = createAsyncThunk(
  'query/fetchAll',
  async ({ skip = 0, limit = 20 }: { skip?: number; limit?: number }, { rejectWithValue }) => {
    try {
      return await queryService.getQueries(skip, limit);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch queries';
      return rejectWithValue(typeof errorMessage === 'string' ? errorMessage : 'Failed to fetch queries');
    }
  }
);

export const fetchQuery = createAsyncThunk(
  'query/fetchOne',
  async (id: number, { rejectWithValue }) => {
    try {
      return await queryService.getQuery(id);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch query';
      return rejectWithValue(typeof errorMessage === 'string' ? errorMessage : 'Failed to fetch query');
    }
  }
);

export const deleteQuery = createAsyncThunk(
  'query/delete',
  async (id: number, { rejectWithValue }) => {
    try {
      await queryService.deleteQuery(id);
      return id;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete query';
      return rejectWithValue(typeof errorMessage === 'string' ? errorMessage : 'Failed to delete query');
    }
  }
);

const querySlice = createSlice({
  name: 'query',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentQuery: (state) => {
      state.currentQuery = null;
      state.comparisonData = null;
    },
    setComparisonData: (state, action) => {
      state.comparisonData = action.payload;
      state.currentQuery = null; // Clear single query when showing comparison
    },
  },
  extraReducers: (builder) => {
    builder
      // Create Query
      .addCase(createQuery.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createQuery.fulfilled, (state, action: PayloadAction<Query>) => {
        state.loading = false;
        state.currentQuery = action.payload;
        state.comparisonData = null; // Clear comparison data when showing regular query result
        state.queries.unshift(action.payload);
      })
      .addCase(createQuery.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Queries
      .addCase(fetchQueries.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQueries.fulfilled, (state, action: PayloadAction<QueryListResponse>) => {
        state.loading = false;
        state.queries = action.payload.queries;
        state.total = action.payload.total;
      })
      .addCase(fetchQueries.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Single Query
      .addCase(fetchQuery.fulfilled, (state, action: PayloadAction<Query>) => {
        state.currentQuery = action.payload;
        const index = state.queries.findIndex(q => q.id === action.payload.id);
        if (index !== -1) {
          state.queries[index] = action.payload;
        }
      })
      // Delete Query
      .addCase(deleteQuery.fulfilled, (state, action: PayloadAction<number>) => {
        state.queries = state.queries.filter(q => q.id !== action.payload);
        state.total -= 1;
      });
  },
});

export const { clearError, clearCurrentQuery, setComparisonData } = querySlice.actions;
export default querySlice.reducer;
