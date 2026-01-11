// src/components/dashboard/RAGQuery.tsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Stack,
} from '@mui/material';
import {
  Send,
} from '@mui/icons-material';
import { queryRAG, RAGQueryResponse } from '../../services/ragService';

interface RAGQueryProps {
  onResultChange: (result: RAGQueryResponse | null) => void;
}

const RAGQuery: React.FC<RAGQueryProps> = ({ onResultChange }) => {
  const [question, setQuestion] = useState('');
  const [ticker, setTicker] = useState('');
  const [includeTechnicalAnalysis, setIncludeTechnicalAnalysis] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);
    onResultChange(null);

    try {
      const response = await queryRAG({
        question: question.trim(),
        ticker: ticker.trim() || undefined,
        include_technical_analysis: includeTechnicalAnalysis,
        period: '3mo',
      });

      onResultChange(response);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Query failed';
      setError(errorMessage);
      onResultChange(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Ask questions about uploaded documents with optional technical analysis
      </Typography>

      {/* Query Form */}
      <Box component="form" onSubmit={handleSubmit}>
        <Stack spacing={2}>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Your Question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What are the key risks mentioned in the annual report?"
            disabled={loading}
          />

          <TextField
            fullWidth
            size="small"
            label="Ticker (Optional)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="e.g., AAPL"
            helperText="Add technical analysis for this stock"
            disabled={loading}
          />

          <FormControlLabel
            control={
              <Switch
                checked={includeTechnicalAnalysis}
                onChange={(e) => setIncludeTechnicalAnalysis(e.target.checked)}
                disabled={loading}
              />
            }
            label="Include Technical Analysis"
          />

          <Button
            type="submit"
            variant="contained"
            fullWidth
            size="large"
            disabled={loading || !question.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
            sx={{
              background: (theme) =>
                theme.palette.mode === 'dark'
                  ? 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)'
                  : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: (theme) =>
                  theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, #1e40af 0%, #6d28d9 100%)'
                    : 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
              },
            }}
          >
            {loading ? 'Processing...' : 'Ask Question'}
          </Button>
        </Stack>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Success Message */}
      {loading && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Analyzing documents and generating answer...
        </Alert>
      )}
    </Box>
  );
};

export default RAGQuery;
