// src/components/dashboard/StockComparison.tsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  CompareArrows as CompareIcon,
} from '@mui/icons-material';
import { ApexOptions } from 'apexcharts';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store/store';
import { setComparisonData } from '../../store/querySlice';
import api from '../../services/api';
import { formatPrice } from '../../utils/currencyUtils';

interface ComparisonData {
  ticker: string;
  current_price: number;
  performance: number;
  rsi: number;
  macd: number;
  signal: string;
  price_data: Array<{ date: string; close: number }>;
  error?: string;
}

const StockComparison: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const [tickers, setTickers] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [comparisonData, setComparisonDataLocal] = useState<ComparisonData[]>([]);
  const [error, setError] = useState<string>('');
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const handleCompare = async () => {
    const tickerList = tickers
      .split(',')
      .map(t => t.trim().toUpperCase())
      .filter(t => t.length > 0);

    if (tickerList.length < 2 || tickerList.length > 5) {
      setError('Please enter 2-5 tickers separated by commas');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/ai/compare', {
        tickers: tickerList,
        period: '6mo',
      });

      const comparisonResult = response.data.comparison;
      setComparisonDataLocal(comparisonResult);
      
      // Dispatch to Redux store to show in Analysis Results panel
      dispatch(setComparisonData({
        comparison: comparisonResult,
        period: '6mo',
      }));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to compare stocks');
    } finally {
      setLoading(false);
    }
  };

  // Note: Chart options and series are defined but not currently used in the component
  // Keeping them for future implementation
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const comparisonChartOptions: ApexOptions = {
    chart: {
      type: 'line',
      height: 400,
      background: 'transparent',
      toolbar: {
        show: true,
        tools: {
          download: true,
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: true,
          reset: true,
        },
      },
    },
    title: {
      text: 'Price Comparison (Normalized)',
      align: 'left',
      style: {
        color: theme.palette.text.primary,
        fontSize: '18px',
        fontWeight: 600,
      },
    },
    xaxis: {
      type: 'datetime',
      labels: {
        style: {
          colors: theme.palette.text.secondary,
        },
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: theme.palette.text.secondary,
        },
        formatter: (value: number) => `${value.toFixed(2)}%`,
      },
    },
    stroke: {
      curve: 'smooth',
      width: 3,
    },
    colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
    grid: {
      borderColor: isDark ? '#334155' : '#e2e8f0',
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      y: {
        formatter: (value: number) => `${value.toFixed(2)}%`,
      },
    },
    legend: {
      position: 'top',
      labels: {
        colors: theme.palette.text.primary,
      },
    },
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const comparisonChartSeries = comparisonData
    .filter(d => !d.error)
    .map(stock => {
      const normalizedData = stock.price_data.map((d, idx) => {
        const basePrice = stock.price_data[0].close;
        const change = ((d.close - basePrice) / basePrice) * 100;
        return {
          x: new Date(d.date).getTime(),
          y: change,
        };
      });

      return {
        name: stock.ticker,
        data: normalizedData,
      };
    });

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, fontSize: '1rem' }}>
        📊 Compare Stocks
      </Typography>

      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          size="small"
          label="Tickers (comma-separated)"
          placeholder="AAPL, MSFT, GOOGL"
          value={tickers}
          onChange={(e) => setTickers(e.target.value)}
          sx={{ mb: 1.5 }}
        />

        <Button
          variant="contained"
          fullWidth
          size="medium"
          startIcon={loading ? <CircularProgress size={18} /> : <CompareIcon />}
          onClick={handleCompare}
          disabled={loading}
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
          {loading ? 'Comparing...' : 'Compare'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2, fontSize: '0.85rem' }}>
          {error}
        </Alert>
      )}

      {comparisonData.length > 0 && (
        <Box>
          <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
            Results:
          </Typography>
          {comparisonData.slice(0, 3).map((stock, idx) => (
            <Card
              key={idx}
              sx={{
                mb: 1.5,
                background:
                  stock.error
                    ? 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)'
                    : stock.performance >= 0
                    ? 'linear-gradient(135deg, #059669 0%, #10b981 100%)'
                    : 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
                color: 'white',
              }}
            >
              <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                {stock.error ? (
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                      {stock.ticker}
                    </Typography>
                    <Typography variant="caption">Error loading data</Typography>
                  </Box>
                ) : (
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                        {stock.ticker}
                      </Typography>
                      {stock.performance >= 0 ? (
                        <TrendingUpIcon fontSize="small" />
                      ) : (
                        <TrendingDownIcon fontSize="small" />
                      )}
                    </Box>

                    <Typography variant="body2" sx={{ mb: 0.5 }}>
                      {formatPrice(stock.current_price, stock.ticker)}
                    </Typography>

                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                      {stock.performance >= 0 ? '+' : ''}
                      {stock.performance.toFixed(2)}%
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      <Chip
                        label={`RSI: ${stock.rsi.toFixed(0)}`}
                        size="small"
                        sx={{ bgcolor: 'rgba(255,255,255,0.25)', color: 'white', fontSize: '0.7rem' }}
                      />
                      <Chip
                        label={stock.signal}
                        size="small"
                        sx={{ bgcolor: 'rgba(255,255,255,0.35)', color: 'white', fontWeight: 600, fontSize: '0.7rem' }}
                      />
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default StockComparison;
