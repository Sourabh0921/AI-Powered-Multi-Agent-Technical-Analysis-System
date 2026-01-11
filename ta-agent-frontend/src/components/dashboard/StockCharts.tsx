// src/components/dashboard/StockCharts.tsx
import React, { useState, useRef } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  useTheme,
  FormControlLabel,
  Checkbox,
  FormGroup,
  Grid,
  Button,
  Stack,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Download as DownloadIcon,
} from '@mui/icons-material';
import Chart from 'react-apexcharts';
import { ApexOptions } from 'apexcharts';

interface PriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface IndicatorData {
  date: string;
  rsi: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_hist: number | null;
  sma_20: number | null;
  sma_50: number | null;
  sma_200: number | null;
  ema_12: number | null;
  ema_26: number | null;
  bb_upper: number | null;
  bb_middle: number | null;
  bb_lower: number | null;
}

interface Pattern {
  type: string;
  date: string;
  signal: string;
  description: string;
  level?: number;
}

interface StockChartsProps {
  ticker: string;
  priceData: PriceData[];
  indicatorData: IndicatorData[];
  patterns?: Pattern[];
}

const StockCharts: React.FC<StockChartsProps> = ({ ticker, priceData, indicatorData, patterns = [] }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [dateRange, setDateRange] = useState('all');
  const [chartType, setChartType] = useState<'candlestick' | 'line'>('candlestick');
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const chartRef = useRef<any>(null);

  // Overlay toggles
  const [overlays, setOverlays] = useState({
    sma20: false,
    sma50: false,
    sma200: false,
    ema12: false,
    ema26: false,
    bollinger: false,
  });

  // Detect currency based on ticker suffix
  const getCurrencySymbol = (tickerSymbol: string): string => {
    const upperTicker = tickerSymbol.toUpperCase();
    
    if (upperTicker.endsWith('.NS') || upperTicker.endsWith('.BO')) {
      return '₹'; // Indian Rupee for NSE/BSE stocks
    } else if (upperTicker.endsWith('.L')) {
      return '£'; // British Pound for London Stock Exchange
    } else if (upperTicker.endsWith('.TO') || upperTicker.endsWith('.V')) {
      return 'C$'; // Canadian Dollar
    } else if (upperTicker.endsWith('.AX')) {
      return 'A$'; // Australian Dollar
    } else if (upperTicker.endsWith('.HK')) {
      return 'HK$'; // Hong Kong Dollar
    } else if (upperTicker.endsWith('.T')) {
      return '¥'; // Japanese Yen
    } else if (upperTicker.endsWith('.KS') || upperTicker.endsWith('.KQ')) {
      return '₩'; // Korean Won
    } else if (upperTicker.endsWith('.SA')) {
      return 'R$'; // Brazilian Real
    } else if (upperTicker.endsWith('.PA')) {
      return '€'; // Euro for Euronext Paris
    } else if (upperTicker.endsWith('.DE') || upperTicker.endsWith('.F')) {
      return '€'; // Euro for German exchanges
    } else {
      return '$'; // Default to US Dollar
    }
  };

  const currencySymbol = getCurrencySymbol(ticker);

  // Debug logging
  console.log('StockCharts render:', { 
    ticker, 
    priceDataLength: priceData?.length, 
    indicatorDataLength: indicatorData?.length,
    patternsLength: patterns?.length,
    firstPrice: priceData?.[0],
    firstIndicator: indicatorData?.[0]
  });

  // Validate data (AFTER all hooks)
  if (!priceData || !Array.isArray(priceData) || priceData.length === 0) {
    console.error('Invalid price data:', priceData);
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="error">No price data available for charting.</Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          Received: {priceData ? (Array.isArray(priceData) ? `Array with ${priceData.length} items` : 'Invalid format') : 'null/undefined'}
        </Typography>
      </Paper>
    );
  }

  if (!indicatorData || !Array.isArray(indicatorData)) {
    console.error('Invalid indicator data:', indicatorData);
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="error">No indicator data available for charting.</Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          Received: {indicatorData ? (Array.isArray(indicatorData) ? `Array with ${(indicatorData as any[]).length} items` : 'Invalid format') : 'null/undefined'}
        </Typography>
      </Paper>
    );
  }

  // Filter data based on date range
  const getFilteredData = () => {
    if (dateRange === 'all') return { priceData, indicatorData };
    
    const days = dateRange === '1m' ? 30 : dateRange === '3m' ? 90 : dateRange === '6m' ? 180 : 365;
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const filtered = priceData.filter(d => new Date(d.date) >= cutoffDate);
    const filteredIndicators = indicatorData.filter(d => new Date(d.date) >= cutoffDate);
    
    return { priceData: filtered, indicatorData: filteredIndicators };
  };

  const { priceData: filteredPrice, indicatorData: filteredIndicators } = getFilteredData();

  // Export chart as image
  const handleExportChart = () => {
    if (chartRef.current) {
      chartRef.current.chart.dataURI().then((uri: any) => {
        const link = document.createElement('a');
        link.href = uri.imgURI;
        link.download = `${ticker}-chart-${new Date().toISOString().split('T')[0]}.png`;
        link.click();
      });
    }
  };

  // Build price chart series with overlays
  const buildPriceChartSeries = () => {
    const series: any[] = [
      {
        name: ticker,
        type: chartType,
        data: filteredPrice.map(d => ({
          x: new Date(d.date).getTime(),
          y: chartType === 'candlestick' ? [d.open, d.high, d.low, d.close] : d.close,
        })),
      },
    ];

    if (overlays.sma20) {
      series.push({
        name: 'SMA 20',
        type: 'line',
        data: filteredIndicators.filter(d => d.sma_20 !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.sma_20 })),
      });
    }
    if (overlays.sma50) {
      series.push({
        name: 'SMA 50',
        type: 'line',
        data: filteredIndicators.filter(d => d.sma_50 !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.sma_50 })),
      });
    }
    if (overlays.sma200) {
      series.push({
        name: 'SMA 200',
        type: 'line',
        data: filteredIndicators.filter(d => d.sma_200 !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.sma_200 })),
      });
    }
    if (overlays.ema12) {
      series.push({
        name: 'EMA 12',
        type: 'line',
        data: filteredIndicators.filter(d => d.ema_12 !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.ema_12 })),
      });
    }
    if (overlays.ema26) {
      series.push({
        name: 'EMA 26',
        type: 'line',
        data: filteredIndicators.filter(d => d.ema_26 !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.ema_26 })),
      });
    }
    if (overlays.bollinger) {
      series.push(
        {
          name: 'BB Upper',
          type: 'line',
          data: filteredIndicators.filter(d => d.bb_upper !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.bb_upper })),
        },
        {
          name: 'BB Middle',
          type: 'line',
          data: filteredIndicators.filter(d => d.bb_middle !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.bb_middle })),
        },
        {
          name: 'BB Lower',
          type: 'line',
          data: filteredIndicators.filter(d => d.bb_lower !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.bb_lower })),
        }
      );
    }

    return series;
  };

  // Price Chart Configuration
  const priceChartOptions: ApexOptions = {
    chart: {
      type: 'candlestick',
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
      text: `${ticker} Price Chart ${dateRange !== 'all' ? `(${dateRange.toUpperCase()})` : ''}`,
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
      tooltip: {
        enabled: true,
      },
      labels: {
        style: {
          colors: theme.palette.text.secondary,
        },
        formatter: (value) => `${currencySymbol}${value.toFixed(2)}`,
      },
    },
    grid: {
      borderColor: isDark ? '#334155' : '#e2e8f0',
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
    },
    legend: {
      show: true,
      position: 'top',
      labels: {
        colors: theme.palette.text.primary,
      },
    },
    stroke: {
      width: [1, 2, 2, 2, 2, 2, 2, 2, 2],
      dashArray: [0, 0, 0, 0, 5, 5, 0, 0, 0],
    },
    colors: ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316', '#14b8a6'],
  };

  const priceChartSeries = buildPriceChartSeries();

  // Volume Chart
  const volumeChartOptions: ApexOptions = {
    chart: {
      type: 'bar',
      height: 150,
      background: 'transparent',
      toolbar: { show: false },
    },
    plotOptions: {
      bar: {
        colors: {
          ranges: [
            { from: -1000000000, to: 0, color: '#ef4444' },
            { from: 0, to: 1000000000, color: '#10b981' },
          ],
        },
      },
    },
    dataLabels: { enabled: false },
    xaxis: {
      type: 'datetime',
      labels: { show: false },
    },
    yaxis: {
      labels: {
        style: { colors: theme.palette.text.secondary },
        formatter: (value) => {
          if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
          if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
          return value.toString();
        },
      },
    },
    grid: { borderColor: isDark ? '#334155' : '#e2e8f0' },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      y: { formatter: (value) => value.toLocaleString() },
    },
  };

  const volumeChartSeries = [
    {
      name: 'Volume',
      data: filteredPrice.map(d => ({ x: new Date(d.date).getTime(), y: d.volume })),
    },
  ];

  // RSI Chart
  const rsiChartOptions: ApexOptions = {
    chart: {
      type: 'line',
      height: 250,
      background: 'transparent',
      toolbar: { show: false },
    },
    stroke: { curve: 'smooth', width: 2 },
    colors: ['#8b5cf6'],
    title: {
      text: 'RSI (Relative Strength Index)',
      align: 'left',
      style: { color: theme.palette.text.primary, fontSize: '16px', fontWeight: 600 },
    },
    xaxis: {
      type: 'datetime',
      labels: { style: { colors: theme.palette.text.secondary } },
    },
    yaxis: {
      min: 0,
      max: 100,
      labels: { style: { colors: theme.palette.text.secondary } },
    },
    annotations: {
      yaxis: [
        {
          y: 70,
          borderColor: '#ef4444',
          label: { text: 'Overbought (70)', style: { color: '#fff', background: '#ef4444' } },
        },
        {
          y: 30,
          borderColor: '#10b981',
          label: { text: 'Oversold (30)', style: { color: '#fff', background: '#10b981' } },
        },
      ],
    },
    grid: { borderColor: isDark ? '#334155' : '#e2e8f0' },
    tooltip: { theme: isDark ? 'dark' : 'light' },
  };

  const rsiChartSeries = [
    {
      name: 'RSI',
      data: filteredIndicators.filter(d => d.rsi !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.rsi })),
    },
  ];

  // MACD Chart
  const macdChartOptions: ApexOptions = {
    chart: {
      type: 'line',
      height: 250,
      background: 'transparent',
      toolbar: { show: false },
    },
    stroke: { curve: 'smooth', width: 2 },
    colors: ['#3b82f6', '#f59e0b', '#10b981'],
    title: {
      text: 'MACD (Moving Average Convergence Divergence)',
      align: 'left',
      style: { color: theme.palette.text.primary, fontSize: '16px', fontWeight: 600 },
    },
    xaxis: {
      type: 'datetime',
      labels: { style: { colors: theme.palette.text.secondary } },
    },
    yaxis: {
      labels: {
        style: { colors: theme.palette.text.secondary },
        formatter: (value) => value.toFixed(4),
      },
    },
    legend: {
      position: 'top',
      labels: { colors: theme.palette.text.primary },
    },
    grid: { borderColor: isDark ? '#334155' : '#e2e8f0' },
    tooltip: { theme: isDark ? 'dark' : 'light' },
  };

  const macdChartSeries = [
    {
      name: 'MACD',
      type: 'line',
      data: filteredIndicators.filter(d => d.macd !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.macd })),
    },
    {
      name: 'Signal',
      type: 'line',
      data: filteredIndicators.filter(d => d.macd_signal !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.macd_signal })),
    },
    {
      name: 'Histogram',
      type: 'bar',
      data: filteredIndicators.filter(d => d.macd_hist !== null).map(d => ({ x: new Date(d.date).getTime(), y: d.macd_hist })),
    },
  ];

  return (
    <Box sx={{ mb: 3 }}>
      <Paper sx={{ p: 0, overflow: 'hidden' }}>
        {/* Controls Bar */}
        <Box sx={{ p: 2, bgcolor: isDark ? 'grey.900' : 'grey.50', borderBottom: 1, borderColor: 'divider' }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Stack direction="row" spacing={1}>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Date Range</InputLabel>
                  <Select value={dateRange} label="Date Range" onChange={(e) => setDateRange(e.target.value)}>
                    <MenuItem value="1m">1 Month</MenuItem>
                    <MenuItem value="3m">3 Months</MenuItem>
                    <MenuItem value="6m">6 Months</MenuItem>
                    <MenuItem value="1y">1 Year</MenuItem>
                    <MenuItem value="all">All Time</MenuItem>
                  </Select>
                </FormControl>

                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Chart Type</InputLabel>
                  <Select value={chartType} label="Chart Type" onChange={(e) => setChartType(e.target.value as 'candlestick' | 'line')}>
                    <MenuItem value="candlestick">Candlestick</MenuItem>
                    <MenuItem value="line">Line</MenuItem>
                  </Select>
                </FormControl>

                <Button variant="outlined" size="small" startIcon={<DownloadIcon />} onClick={handleExportChart}>
                  Export
                </Button>
              </Stack>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormGroup row sx={{ justifyContent: 'flex-end' }}>
                <FormControlLabel
                  control={<Checkbox size="small" checked={overlays.sma20} onChange={(e) => setOverlays({ ...overlays, sma20: e.target.checked })} />}
                  label="SMA 20"
                />
                <FormControlLabel
                  control={<Checkbox size="small" checked={overlays.sma50} onChange={(e) => setOverlays({ ...overlays, sma50: e.target.checked })} />}
                  label="SMA 50"
                />
                <FormControlLabel
                  control={<Checkbox size="small" checked={overlays.ema12} onChange={(e) => setOverlays({ ...overlays, ema12: e.target.checked })} />}
                  label="EMA 12"
                />
                <FormControlLabel
                  control={<Checkbox size="small" checked={overlays.bollinger} onChange={(e) => setOverlays({ ...overlays, bollinger: e.target.checked })} />}
                  label="Bollinger"
                />
              </FormGroup>
            </Grid>
          </Grid>
        </Box>

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
          <Tab label="Price Chart" />
          <Tab label="RSI Indicator" />
          <Tab label="MACD Indicator" />
        </Tabs>

        <Box sx={{ p: 2 }}>
          {activeTab === 0 && (
            <Box>
              <Chart ref={chartRef} options={priceChartOptions} series={priceChartSeries} type={chartType} height={400} />
              <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2, mb: 1 }}>
                Volume
              </Typography>
              <Chart options={volumeChartOptions} series={volumeChartSeries} type="bar" height={150} />
            </Box>
          )}

          {activeTab === 1 && (
            <Box>
              <Chart options={rsiChartOptions} series={rsiChartSeries} type="line" height={300} />
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                <strong>RSI Interpretation:</strong> RSI above 70 indicates overbought conditions (potential sell signal), 
                while RSI below 30 indicates oversold conditions (potential buy signal).
              </Typography>
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              <Chart options={macdChartOptions} series={macdChartSeries} type="line" height={300} />
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                <strong>MACD Interpretation:</strong> When MACD line crosses above signal line, it's a bullish signal. 
                When it crosses below, it's bearish. Histogram shows the difference between MACD and signal line.
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default StockCharts;
