// src/store/store.ts - Redux store configuration
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import queryReducer from './querySlice';
import themeReducer from './themeSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    query: queryReducer,
    theme: themeReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
