// src/components/dashboard/ResultDisplay.tsx
import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Chip,
  Grid,
  Paper,
  Alert,
  Collapse,
  IconButton,
  Tooltip,
  Button,
  Snackbar,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  ContentCopy as ContentCopyIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import { Query } from '../../types';
import StockCharts from './StockCharts';
import { formatPrice } from '../../utils/currencyUtils';
import { formatNumber, copyToClipboard } from '../../utils/formatters';
import { AnalysisResultSkeleton } from '../common/LoadingSkeleton';
import Sparkline from '../common/Sparkline';
import QuickActionsBar from './QuickActionsBar';

interface ResultDisplayProps {
  query: Query;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ query }) => {
  const [expandedSections, setExpandedSections] = useState<{ [key: string]: boolean }>({
    charts: true,
    metrics: true,
    analysis: true,
  });
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const contentRef = useRef<HTMLDivElement>(null);

  // Show loading skeleton if query is pending
  if (query.status === 'pending') {
    return <AnalysisResultSkeleton />;
  }

  // Better error handling
  if (query.status === 'failed') {
    return (
      <Alert 
        severity="error" 
        sx={{ 
          boxShadow: 2,
          borderRadius: 2,
        }}
        action={
          <Button 
            color="inherit" 
            size="small" 
            startIcon={<RefreshIcon />}
            onClick={() => window.location.reload()}
          >
            Retry
          </Button>
        }
      >
        <Typography variant="subtitle1" fontWeight="600" gutterBottom>
          Analysis Failed
        </Typography>
        <Typography variant="body2">
          {query.error_message || 'An error occurred while processing your query. Please try again.'}
        </Typography>
      </Alert>
    );
  }

  // Return early if no results
  if (!query.result) {
    return (
      <Alert severity="info" sx={{ boxShadow: 2, borderRadius: 2 }}>
        No analysis results available yet.
      </Alert>
    );
  }

  // Copy to clipboard with notification
  const handleCopy = async (text?: string) => {
    const contentToCopy = text || query.result?.analysis || query.result?.response || '';
    const success = await copyToClipboard(contentToCopy);
    if (success) {
      setSnackbarMessage('Copied to clipboard!');
      setSnackbarOpen(true);
    } else {
      setSnackbarMessage('Failed to copy');
      setSnackbarOpen(true);
    }
  };

  // Copy ticker to clipboard
  const handleCopyTicker = async () => {
    if (query.ticker) {
      const success = await copyToClipboard(query.ticker);
      if (success) {
        setSnackbarMessage(`Copied ${query.ticker} to clipboard!`);
        setSnackbarOpen(true);
      }
    }
  };

  // Download as PDF
  const handleDownloadPdf = async () => {
    if (!contentRef.current) return;
    
    try {
      const canvas = await html2canvas(contentRef.current, {
        scale: 2,
        logging: false,
        useCORS: true,
      });
      
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgWidth = 210;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      let heightLeft = imgHeight;
      let position = 0;
      
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= 297;
      
      while (heightLeft > 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= 297;
      }
      
      pdf.save(`analysis-${query.ticker || 'report'}-${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (err) {
      console.error('Failed to generate PDF:', err);
    }
  };

  // Print
  const handlePrint = () => {
    window.print();
  };

  // Toggle sections
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const result = query.result;

  return (
    <Box ref={contentRef}>
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />

      {/* Action Buttons with ticker copy */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 1 }}>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
          <Chip label={query.query_type} color="primary" size="small" />
          {query.ticker && (
            <Tooltip title="Click to copy ticker" arrow>
              <Chip 
                label={query.ticker} 
                variant="outlined" 
                size="small"
                onClick={handleCopyTicker}
                icon={<ContentCopyIcon fontSize="small" />}
                sx={{
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    bgcolor: 'primary.light',
                    color: 'white',
                    transform: 'scale(1.05)',
                  }
                }}
              />
            </Tooltip>
          )}
        </Box>
        
        <QuickActionsBar
          ticker={query.ticker}
          onCopy={handleCopy}
          onDownload={handleDownloadPdf}
          onPrint={handlePrint}
        />
      </Box>

      {/* Stock Analysis Results */}
      {(query.query_type === 'analyze' || query.query_type === 'ai_analysis') && result.analysis && (
        <Box>
          {/* Interactive Charts */}
          {result.price_data && result.indicator_data && Array.isArray(result.price_data) && result.price_data.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  mb: 2,
                  cursor: 'pointer',
                }}
                onClick={() => toggleSection('charts')}
              >
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  📊 Interactive Charts
                </Typography>
                <IconButton size="small">
                  {expandedSections.charts ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>
              
              <Collapse in={expandedSections.charts}>
                <StockCharts 
                  ticker={query.ticker || result.ticker}
                  priceData={result.price_data}
                  indicatorData={result.indicator_data}
                  patterns={result.patterns || []}
                />
              </Collapse>
            </Box>
          )}
          
          {/* Debug Info - Remove after testing */}
          {(query.query_type === 'analyze' || query.query_type === 'ai_analysis') && !result.price_data && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Chart data not available. Missing price_data in API response.
            </Alert>
          )}
          {result.price_data && (!Array.isArray(result.price_data) || result.price_data.length === 0) && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Chart data is empty. API returned {result.price_data ? result.price_data.length : 0} data points.
            </Alert>
          )}

          {/* Detected Patterns Section */}
          {result.patterns && Array.isArray(result.patterns) && result.patterns.length > 0 && (() => {
            // Deduplicate patterns based on type and signal
            const uniquePatterns = result.patterns.reduce((acc: any[], pattern: any) => {
              const key = `${pattern.type}-${pattern.signal}`;
              const exists = acc.find(p => `${p.type}-${p.signal}` === key);
              if (!exists) {
                acc.push(pattern);
              }
              return acc;
            }, []);
            
            // Limit to top 5 most relevant patterns
            const displayPatterns = uniquePatterns.slice(0, 5);
            
            return (
              <Box sx={{ mb: 3 }}>
                <Paper sx={{ p: 2, bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100' }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    🎯 Detected Patterns ({uniquePatterns.length} total, showing {displayPatterns.length})
                  </Typography>
                  <Grid container spacing={1}>
                    {displayPatterns.map((pattern: any, idx: number) => (
                      <Grid item key={`${pattern.type}-${pattern.signal}-${idx}`}>
                        <Chip
                          icon={
                            pattern.signal === 'bullish' ? (
                              <Box component="span" sx={{ fontSize: '1.2em' }}>📈</Box>
                            ) : pattern.signal === 'bearish' ? (
                              <Box component="span" sx={{ fontSize: '1.2em' }}>📉</Box>
                            ) : (
                              <Box component="span" sx={{ fontSize: '1.2em' }}>⚠️</Box>
                            )
                          }
                          label={`${pattern.type} - ${pattern.description}`}
                          color={pattern.signal === 'bullish' ? 'success' : pattern.signal === 'bearish' ? 'error' : 'warning'}
                          size="medium"
                          sx={{ fontSize: '0.9rem', py: 2.5 }}
                        />
                      </Grid>
                    ))}
                  </Grid>
                </Paper>
              </Box>
            );
          })()}

          {/* Metrics Section */}
          {result.latest_price && (
            <Box sx={{ mb: 3 }}>
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  mb: 2,
                  cursor: 'pointer',
                }}
                onClick={() => toggleSection('metrics')}
              >
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Key Metrics
                </Typography>
                <IconButton size="small">
                  {expandedSections.metrics ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>
              
              <Collapse in={expandedSections.metrics}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper 
                      sx={{ 
                        p: 2.5, 
                        textAlign: 'center',
                        background: (theme) => 
                          theme.palette.mode === 'dark' 
                            ? 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)'
                            : 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)',
                        color: 'white',
                        position: 'relative',
                        overflow: 'hidden',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: 4,
                        }
                      }}
                    >
                      <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5 }}>
                        Price
                      </Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                        {formatPrice(result.latest_price, result.ticker)}
                      </Typography>
                      {result.price_history && result.price_history.length > 0 && (
                        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
                          <Sparkline 
                            data={result.price_history} 
                            width={120} 
                            height={30}
                            color="rgba(255,255,255,0.8)"
                            showArea={true}
                          />
                        </Box>
                      )}
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper 
                      sx={{ 
                        p: 2.5, 
                        textAlign: 'center',
                        background: (theme) => 
                          theme.palette.mode === 'dark'
                            ? 'linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%)'
                            : 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
                        color: 'white',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: 4,
                        }
                      }}
                    >
                      <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5 }}>
                        RSI
                      </Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                        {formatNumber(result.rsi, 2)}
                      </Typography>
                      {result.rsi_history && result.rsi_history.length > 0 && (
                        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
                          <Sparkline 
                            data={result.rsi_history} 
                            width={120} 
                            height={30}
                            color="rgba(255,255,255,0.8)"
                          />
                        </Box>
                      )}
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper 
                      sx={{ 
                        p: 2.5, 
                        textAlign: 'center',
                        background: (theme) => 
                          theme.palette.mode === 'dark'
                            ? 'linear-gradient(135deg, #be123c 0%, #f43f5e 100%)'
                            : 'linear-gradient(135deg, #f43f5e 0%, #fb7185 100%)',
                        color: 'white',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: 4,
                        }
                      }}
                    >
                      <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5 }}>
                        MACD
                      </Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                        {formatNumber(result.macd, 4)}
                      </Typography>
                      {result.macd_history && result.macd_history.length > 0 && (
                        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
                          <Sparkline 
                            data={result.macd_history} 
                            width={120} 
                            height={30}
                            color="rgba(255,255,255,0.8)"
                          />
                        </Box>
                      )}
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper 
                      sx={{ 
                        p: 2.5, 
                        textAlign: 'center',
                        background: result.signal === 'BUY'
                          ? 'linear-gradient(135deg, #059669 0%, #10b981 100%)'
                          : result.signal === 'SELL'
                          ? 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)'
                          : 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)',
                        color: 'white',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: 4,
                        }
                      }}
                    >
                      <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5 }}>
                        Signal
                      </Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        {result.signal}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Collapse>
            </Box>
          )}

          {/* Analysis Section */}
          <Box>
            <Box 
              sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                mb: 2,
                cursor: 'pointer',
              }}
              onClick={() => toggleSection('analysis')}
            >
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                AI Analysis
              </Typography>
              <IconButton size="small">
                {expandedSections.analysis ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
            
            <Collapse in={expandedSections.analysis}>
              <Paper 
                sx={{ 
                  p: 3,
                  bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50',
                  '& .markdown-content': {
                    '& h1, & h2, & h3': {
                      fontWeight: 700,
                      mb: 2,
                      mt: 3,
                      color: 'primary.main',
                    },
                    '& h1': { fontSize: '2rem' },
                    '& h2': { fontSize: '1.5rem' },
                    '& h3': { fontSize: '1.25rem' },
                    '& p': {
                      mb: 2,
                      lineHeight: 1.8,
                      fontSize: '0.95rem',
                    },
                    '& strong': {
                      fontWeight: 700,
                      color: (theme) => theme.palette.mode === 'dark' ? 'primary.light' : 'primary.dark',
                    },
                    '& ul, & ol': {
                      mb: 2,
                      pl: 3,
                    },
                    '& li': {
                      mb: 1,
                      lineHeight: 1.8,
                    },
                    '& table': {
                      width: '100%',
                      borderCollapse: 'collapse',
                      mb: 2,
                      mt: 2,
                    },
                    '& th': {
                      backgroundColor: (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.200',
                      padding: '12px',
                      textAlign: 'left',
                      fontWeight: 700,
                      borderBottom: '2px solid',
                      borderColor: (theme) => theme.palette.divider,
                    },
                    '& td': {
                      padding: '12px',
                      borderBottom: '1px solid',
                      borderColor: (theme) => theme.palette.divider,
                    },
                    '& code': {
                      backgroundColor: (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.200',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      fontSize: '0.9em',
                      fontFamily: 'monospace',
                    },
                    '& pre': {
                      backgroundColor: (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.200',
                      padding: '16px',
                      borderRadius: '8px',
                      overflow: 'auto',
                      mb: 2,
                    },
                    '& blockquote': {
                      borderLeft: '4px solid',
                      borderColor: 'primary.main',
                      pl: 2,
                      ml: 0,
                      fontStyle: 'italic',
                      color: 'text.secondary',
                    },
                  },
                }}
              >
                <Box className="markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {result.analysis}
                  </ReactMarkdown>
                </Box>
              </Paper>
            </Collapse>
          </Box>
        </Box>
      )}

      {/* General Query Results */}
      {query.query_type === 'general' && result.response && (
        <Paper 
          sx={{ 
            p: 3,
            bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50',
          }}
        >
          <Box className="markdown-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {result.response}
            </ReactMarkdown>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default ResultDisplay;
