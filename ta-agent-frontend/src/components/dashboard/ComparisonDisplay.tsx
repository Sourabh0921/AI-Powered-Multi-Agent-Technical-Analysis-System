// src/components/dashboard/ComparisonDisplay.tsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  useTheme,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import Chart from 'react-apexcharts';
import { ApexOptions } from 'apexcharts';
import { formatPrice } from '../../utils/currencyUtils';

interface ComparisonStock {
  ticker: string;
  current_price: number;
  performance: number;
  rsi: number;
  macd: number;
  signal: string;
  price_data: Array<{ date: string; close: number }>;
  error?: string;
}

interface ComparisonDisplayProps {
  comparison: ComparisonStock[];
  period: string;
}

const ComparisonDisplay: React.FC<ComparisonDisplayProps> = ({ comparison, period }) => {
  const [activeTab, setActiveTab] = useState(0);
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const validStocks = comparison.filter(s => !s.error);
  
  // Find best and worst performers
  const bestPerformer = validStocks.reduce((best, stock) => 
    stock.performance > best.performance ? stock : best
  , validStocks[0]);
  
  const worstPerformer = validStocks.reduce((worst, stock) => 
    stock.performance < worst.performance ? stock : worst
  , validStocks[0]);

  // Normalized Price Comparison Chart
  const normalizedChartOptions: ApexOptions = {
    chart: {
      type: 'line',
      height: 400,
      background: 'transparent',
      toolbar: {
        show: true,
        tools: {
          download: true,
          zoom: true,
          pan: true,
          reset: true,
        },
      },
    },
    title: {
      text: `Stock Price Comparison - Normalized (${period.toUpperCase()})`,
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
      title: {
        text: 'Percentage Change (%)',
        style: {
          color: theme.palette.text.secondary,
        },
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
      shared: true,
      intersect: false,
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

  const normalizedChartSeries = validStocks.map(stock => {
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

  // Performance Bar Chart
  const performanceChartOptions: ApexOptions = {
    chart: {
      type: 'bar',
      height: 300,
      background: 'transparent',
      toolbar: { show: false },
    },
    title: {
      text: `Performance Comparison (${period.toUpperCase()})`,
      align: 'left',
      style: {
        color: theme.palette.text.primary,
        fontSize: '18px',
        fontWeight: 600,
      },
    },
    plotOptions: {
      bar: {
        horizontal: false,
        borderRadius: 8,
        dataLabels: {
          position: 'top',
        },
      },
    },
    dataLabels: {
      enabled: true,
      formatter: (val: number) => `${val.toFixed(2)}%`,
      offsetY: -20,
      style: {
        fontSize: '12px',
        colors: [theme.palette.text.primary],
      },
    },
    xaxis: {
      categories: validStocks.map(s => s.ticker),
      labels: {
        style: {
          colors: theme.palette.text.secondary,
          fontSize: '14px',
          fontWeight: 600,
        },
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: theme.palette.text.secondary,
        },
        formatter: (value: number) => `${value.toFixed(1)}%`,
      },
      title: {
        text: 'Return (%)',
        style: {
          color: theme.palette.text.secondary,
        },
      },
    },
    colors: validStocks.map(s => s.performance >= 0 ? '#10b981' : '#ef4444'),
    grid: {
      borderColor: isDark ? '#334155' : '#e2e8f0',
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      y: {
        formatter: (value: number) => `${value.toFixed(2)}%`,
      },
    },
  };

  const performanceChartSeries = [
    {
      name: 'Performance',
      data: validStocks.map(s => s.performance),
    },
  ];

  // RSI Comparison Chart
  const rsiChartOptions: ApexOptions = {
    chart: {
      type: 'bar',
      height: 250,
      background: 'transparent',
      toolbar: { show: false },
    },
    title: {
      text: 'RSI Comparison',
      align: 'left',
      style: {
        color: theme.palette.text.primary,
        fontSize: '16px',
        fontWeight: 600,
      },
    },
    plotOptions: {
      bar: {
        horizontal: true,
        borderRadius: 6,
      },
    },
    dataLabels: {
      enabled: true,
      formatter: (val: number) => val.toFixed(1),
    },
    xaxis: {
      categories: validStocks.map(s => s.ticker),
      min: 0,
      max: 100,
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
          fontSize: '14px',
          fontWeight: 600,
        },
      },
    },
    colors: validStocks.map(s => {
      if (s.rsi > 70) return '#ef4444'; // Overbought
      if (s.rsi < 30) return '#10b981'; // Oversold
      return '#3b82f6'; // Neutral
    }),
    grid: {
      borderColor: isDark ? '#334155' : '#e2e8f0',
    },
    annotations: {
      xaxis: [
        {
          x: 70,
          borderColor: '#ef4444',
          label: {
            text: 'Overbought',
            style: {
              color: '#fff',
              background: '#ef4444',
            },
          },
        },
        {
          x: 30,
          borderColor: '#10b981',
          label: {
            text: 'Oversold',
            style: {
              color: '#fff',
              background: '#10b981',
            },
          },
        },
      ],
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
    },
  };

  const rsiChartSeries = [
    {
      name: 'RSI',
      data: validStocks.map(s => s.rsi),
    },
  ];

  return (
    <Box ref={null}>
      {/* Best/Worst Performer Alert */}
      {validStocks.length > 0 && (
        <Alert 
          severity="info" 
          sx={{ 
            mb: 2,
            '& .MuiAlert-message': { width: '100%' }
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                🏆 Best Performer: <span style={{ color: theme.palette.success.main }}>{bestPerformer.ticker}</span> 
                {' '}(+{bestPerformer.performance.toFixed(2)}%)
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                📉 Worst Performer: <span style={{ color: theme.palette.error.main }}>{worstPerformer.ticker}</span>
                {' '}({worstPerformer.performance.toFixed(2)}%)
              </Typography>
            </Box>
          </Box>
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {comparison.map((stock, idx) => (
          <Grid item xs={12} sm={6} md={comparison.length > 3 ? 3 : 12 / comparison.length} key={idx}>
            {stock.error ? (
              <Paper
                sx={{
                  p: 2,
                  background: 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)',
                  color: 'white',
                }}
              >
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  {stock.ticker}
                </Typography>
                <Typography variant="body2">Error loading data</Typography>
              </Paper>
            ) : (
              <Paper
                sx={{
                  p: 2,
                  background:
                    stock.performance >= 0
                      ? 'linear-gradient(135deg, #059669 0%, #10b981 100%)'
                      : 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
                  color: 'white',
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="h5" sx={{ fontWeight: 700 }}>
                    {stock.ticker}
                  </Typography>
                  {stock.performance >= 0 ? <TrendingUpIcon /> : <TrendingDownIcon />}
                </Box>

                <Typography variant="h6" sx={{ mb: 0.5 }}>
                  {formatPrice(stock.current_price, stock.ticker)}
                </Typography>

                <Typography variant="body1" sx={{ mb: 1, fontWeight: 600 }}>
                  {stock.performance >= 0 ? '+' : ''}
                  {stock.performance.toFixed(2)}%
                </Typography>

                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  <Chip
                    label={`RSI: ${stock.rsi.toFixed(0)}`}
                    size="small"
                    sx={{ bgcolor: 'rgba(255,255,255,0.25)', color: 'white', fontSize: '0.75rem' }}
                  />
                  <Chip
                    label={stock.signal}
                    size="small"
                    sx={{ bgcolor: 'rgba(255,255,255,0.35)', color: 'white', fontWeight: 600, fontSize: '0.75rem' }}
                  />
                </Box>
              </Paper>
            )}
          </Grid>
        ))}
      </Grid>

      {/* Chart Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            px: 2,
            '& .MuiTab-root': { fontWeight: 600, textTransform: 'none' },
          }}
        >
          <Tab label="Price Comparison" />
          <Tab label="Performance" />
          <Tab label="RSI Analysis" />
          <Tab label="Metrics Table" />
        </Tabs>

        <Box sx={{ p: 2 }}>
          {activeTab === 0 && (
            <Box>
              <Chart options={normalizedChartOptions} series={normalizedChartSeries} type="line" height={400} />
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                <strong>Note:</strong> All prices are normalized to 0% at the start date for easy comparison. 
                This shows relative performance regardless of actual price levels.
              </Typography>
            </Box>
          )}

          {activeTab === 1 && (
            <Box>
              <Chart options={performanceChartOptions} series={performanceChartSeries} type="bar" height={300} />
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                <strong>Performance:</strong> Shows the total return percentage for each stock over the selected period.
              </Typography>
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              <Chart options={rsiChartOptions} series={rsiChartSeries} type="bar" height={250} />
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                <strong>RSI Analysis:</strong> RSI above 70 indicates overbought (red), below 30 indicates oversold (green).
              </Typography>
            </Box>
          )}

          {activeTab === 3 && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>Ticker</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>
                      Price
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>
                      Performance
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>
                      RSI
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>
                      MACD
                    </TableCell>
                    <TableCell align="center" sx={{ fontWeight: 700 }}>
                      Signal
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {validStocks.map((stock, idx) => (
                    <TableRow key={idx} hover>
                      <TableCell>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                          {stock.ticker}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">{formatPrice(stock.current_price, stock.ticker)}</TableCell>
                      <TableCell
                        align="right"
                        sx={{
                          color: stock.performance >= 0 ? 'success.main' : 'error.main',
                          fontWeight: 600,
                        }}
                      >
                        {stock.performance >= 0 ? '+' : ''}
                        {stock.performance.toFixed(2)}%
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{
                          color:
                            stock.rsi > 70 ? 'error.main' : stock.rsi < 30 ? 'success.main' : 'text.primary',
                        }}
                      >
                        {stock.rsi.toFixed(1)}
                      </TableCell>
                      <TableCell align="right">{stock.macd.toFixed(4)}</TableCell>
                      <TableCell align="center">
                        <Chip
                          label={stock.signal}
                          size="small"
                          color={
                            stock.signal === 'BUY' ? 'success' : stock.signal === 'SELL' ? 'error' : 'default'
                          }
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default ComparisonDisplay;
