// src/components/dashboard/QueryInput.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { createQuery, fetchQueries, fetchQuery } from '../../store/querySlice';
import { AppDispatch, RootState } from '../../store/store';

const QueryInput: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { loading } = useSelector((state: RootState) => state.query);

  const [queryText, setQueryText] = useState('');
  const [queryType, setQueryType] = useState('general'); // Default to general analysis
  const [ticker, setTicker] = useState('');
  const [pollingQueryId, setPollingQueryId] = useState<number | null>(null);

  // Poll for query completion
  useEffect(() => {
    if (!pollingQueryId) return;

    const pollInterval = setInterval(async () => {
      const result = await dispatch(fetchQuery(pollingQueryId));
      
      if (fetchQuery.fulfilled.match(result)) {
        const query = result.payload;
        if (query.status === 'completed' || query.status === 'failed') {
          setPollingQueryId(null); // Stop polling
          await dispatch(fetchQueries({ skip: 0, limit: 20 })); // Refresh history
        }
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [pollingQueryId, dispatch]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryText.trim()) return;

    // For stock analysis, ticker is required
    if (queryType === 'analyze' && !ticker.trim()) {
      alert('Please enter a ticker symbol for stock analysis');
      return;
    }

    const result = await dispatch(createQuery({
      query_text: queryText,
      query_type: queryType,
      ticker: queryType === 'analyze' ? (ticker || 'AAPL') : undefined, // Only send ticker for stock analysis
    }));

    // Refresh query history after submission
    if (createQuery.fulfilled.match(result)) {
      await dispatch(fetchQueries({ skip: 0, limit: 20 }));
      // Start polling for this query
      setPollingQueryId(result.payload.id);
    }

    setQueryText('');
    setTicker('');
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
        <InputLabel>Query Type</InputLabel>
        <Select
          value={queryType}
          label="Query Type"
          onChange={(e) => setQueryType(e.target.value)}
        >
          <MenuItem value="general">General Analysis</MenuItem>
          <MenuItem value="analyze">Stock Analysis</MenuItem>
        </Select>
      </FormControl>

      {queryType === 'analyze' && (
        <TextField
          fullWidth
          size="small"
          label="Ticker Symbol"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          placeholder="e.g., AAPL, MSFT"
          sx={{ mb: 2 }}
        />
      )}

      <TextField
        fullWidth
        multiline
        rows={8}
        label="Your Question"
        value={queryText}
        onChange={(e) => setQueryText(e.target.value)}
        placeholder={queryType === 'general' ? "Example: What is support and resistance? Explain moving averages." : "Example: Should I buy AAPL now? What's the trend?"}
        sx={{ mb: 2 }}
      />

      <Button
        type="submit"
        variant="contained"
        fullWidth
        size="large"
        disabled={loading || !queryText.trim()}
        startIcon={loading ? <CircularProgress size={20} sx={{ color: 'white' }} /> : <SendIcon />}
        sx={{
          background: (theme) =>
            theme.palette.mode === 'dark'
              ? 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)'
              : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          transition: 'all 0.3s ease',
          transform: 'scale(1)',
          boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
          '&:hover': {
            background: (theme) =>
              theme.palette.mode === 'dark'
                ? 'linear-gradient(135deg, #1e40af 0%, #6d28d9 100%)'
                : 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
            transform: 'scale(1.02) translateY(-2px)',
            boxShadow: '0 8px 20px rgba(102, 126, 234, 0.6)',
          },
          '&:active': {
            transform: 'scale(0.98)',
          },
          '&:disabled': {
            background: 'rgba(102, 126, 234, 0.3)',
            color: 'rgba(255, 255, 255, 0.5)',
          },
        }}
      >
        {loading ? 'Analyzing...' : 'Submit Query'}
      </Button>
    </Box>
  );
};

export default QueryInput;
