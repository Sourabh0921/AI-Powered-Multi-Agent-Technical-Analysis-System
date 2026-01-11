// src/components/dashboard/RAGResultDisplay.tsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  alpha,
} from '@mui/material';
import {
  ExpandMore,
  Description,
  TrendingUp,
  Source,
  ContentCopy,
  CheckCircle,
  Star,
  StarBorder,
} from '@mui/icons-material';
import { RAGQueryResponse } from '../../services/ragService';
import QuickActionsBar from './QuickActionsBar';

interface RAGResultDisplayProps {
  result: RAGQueryResponse;
}

const highlightKeywords = (text: string, keywords: string[]): JSX.Element[] => {
  if (!keywords || keywords.length === 0) return [<span key={0}>{text}</span>];
  
  const regex = new RegExp(`(${keywords.join('|')})`, 'gi');
  const parts = text.split(regex);
  
  return parts.map((part, index) => {
    if (keywords.some(keyword => keyword.toLowerCase() === part.toLowerCase())) {
      return (
        <Box
          key={index}
          component="span"
          sx={{
            backgroundColor: (theme) => alpha(theme.palette.warning.main, 0.3),
            padding: '2px 4px',
            borderRadius: '3px',
            fontWeight: 600,
          }}
        >
          {part}
        </Box>
      );
    }
    return <span key={index}>{part}</span>;
  });
};

const RAGResultDisplay: React.FC<RAGResultDisplayProps> = ({ result }) => {
  const [copiedSource, setCopiedSource] = useState<number | null>(null);
  const [savedSources, setSavedSources] = useState<Set<number>>(new Set());

  const handleCopySource = (content: string, index: number) => {
    navigator.clipboard.writeText(content);
    setCopiedSource(index);
    setTimeout(() => setCopiedSource(null), 2000);
  };

  const handleSaveSource = (index: number) => {
    const newSaved = new Set(savedSources);
    if (newSaved.has(index)) {
      newSaved.delete(index);
    } else {
      newSaved.add(index);
    }
    setSavedSources(newSaved);
  };

  const extractKeywords = (question: string): string[] => {
    const stopWords = ['what', 'is', 'the', 'are', 'in', 'of', 'for', 'to', 'a', 'an'];
    return question
      .toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 3 && !stopWords.includes(word));
  };

  const keywords = extractKeywords(result.question);

  const getConfidenceColor = (score: number) => {
    if (score > 0.8) return 'success';
    if (score > 0.6) return 'info';
    if (score > 0.4) return 'warning';
    return 'error';
  };

  const handleCopyAnalysis = () => {
    const text = `Question: ${result.question}\n\nAnswer:\n${result.document_insights?.answer || ''}`;
    navigator.clipboard.writeText(text);
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rag-analysis-${Date.now()}.json`;
    a.click();
  };

  return (
    <Box>
      {/* Question Card with Actions */}
      <Paper 
        elevation={2}
        sx={{ 
          p: 2.5, 
          mb: 3, 
          background: (theme) => 
            theme.palette.mode === 'dark' 
              ? 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)'
              : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: 2,
          position: 'relative',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" sx={{ opacity: 0.9, display: 'block', mb: 1 }}>
              Your Question
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 600, lineHeight: 1.4 }}>
              {result.question}
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.7, display: 'block', mt: 1 }}>
              {new Date(result.timestamp).toLocaleString()}
            </Typography>
          </Box>
          <Box sx={{ ml: 2 }}>
            <QuickActionsBar
              onCopy={handleCopyAnalysis}
              onDownload={handleDownload}
            />
          </Box>
        </Box>
      </Paper>

      {/* Document Insights */}
      <Accordion 
        defaultExpanded
        sx={{
          '&:before': { display: 'none' },
          boxShadow: 2,
          borderRadius: '8px !important',
          mb: 2,
        }}
      >
        <AccordionSummary 
          expandIcon={<ExpandMore />}
          sx={{ 
            borderRadius: '8px',
            '&:hover': { bgcolor: 'action.hover' }
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
            <Description fontSize="small" color="primary" />
            <Typography variant="subtitle1" fontWeight="bold">
              Document Insights
            </Typography>
            {result.document_insights?.retrieved_count !== undefined && (
              <Chip 
                label={`${result.document_insights.retrieved_count} ${result.document_insights.retrieved_count === 1 ? 'source' : 'sources'}`}
                size="small" 
                color="primary"
                sx={{ ml: 'auto' }}
              />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails sx={{ pt: 0 }}>
          <Paper 
            elevation={0}
            sx={{ 
              p: 2.5, 
              mb: 3, 
              bgcolor: 'background.default',
              borderLeft: 3,
              borderColor: 'primary.main',
              borderRadius: 1,
            }}
          >
            <Typography 
              variant="body1" 
              sx={{ 
                whiteSpace: 'pre-wrap', 
                lineHeight: 1.8,
                fontSize: '1rem',
              }}
            >
              {result.document_insights?.answer || 'No answer available'}
            </Typography>
          </Paper>

          {/* Sources */}
          {result.document_insights?.sources && result.document_insights.sources.length > 0 && (
            <Box>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Source fontSize="small" color="action" />
                <Typography 
                  variant="subtitle2" 
                  color="text.secondary"
                  fontWeight={600}
                >
                  Referenced Sources
                </Typography>
              </Box>
              {result.document_insights.sources.map((source, idx) => (
                <Paper 
                  key={idx} 
                  elevation={1}
                  sx={{ 
                    p: 2.5, 
                    mb: 2, 
                    bgcolor: 'background.paper',
                    borderLeft: 4,
                    borderColor: getConfidenceColor(source.score),
                    borderRadius: 1,
                    transition: 'all 0.2s',
                    '&:hover': {
                      boxShadow: 3,
                      transform: 'translateY(-2px)',
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5, flexWrap: 'wrap' }}>
                        <Typography variant="body2" fontWeight={600} color="text.primary">
                          📄 {source.metadata?.original_filename || 'Unknown Document'}
                        </Typography>
                        {source.metadata?.ticker && (
                          <Chip 
                            label={source.metadata.ticker} 
                            size="small" 
                            color="secondary"
                            sx={{ height: 22, fontSize: '0.75rem' }} 
                          />
                        )}
                        {source.metadata?.doc_type && (
                          <Chip 
                            label={source.metadata.doc_type} 
                            size="small" 
                            variant="outlined"
                            sx={{ height: 22, fontSize: '0.7rem' }} 
                          />
                        )}
                      </Box>
                      <Chip 
                        label={`Confidence: ${(source.score * 100).toFixed(0)}%`} 
                        size="small" 
                        color={getConfidenceColor(source.score)}
                        sx={{ height: 20, fontSize: '0.7rem' }} 
                      />
                    </Box>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title={savedSources.has(idx) ? "Unsave" : "Save source"}>
                        <IconButton 
                          size="small" 
                          onClick={() => handleSaveSource(idx)}
                          color={savedSources.has(idx) ? "primary" : "default"}
                        >
                          {savedSources.has(idx) ? <Star fontSize="small" /> : <StarBorder fontSize="small" />}
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={copiedSource === idx ? "Copied!" : "Copy source"}>
                        <IconButton 
                          size="small" 
                          onClick={() => handleCopySource(source.content, idx)}
                        >
                          {copiedSource === idx ? 
                            <CheckCircle fontSize="small" color="success" /> : 
                            <ContentCopy fontSize="small" />
                          }
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                  <Typography 
                    variant="body2" 
                    color="text.secondary" 
                    sx={{ 
                      fontStyle: 'italic', 
                      lineHeight: 1.7,
                      pl: 2,
                      borderLeft: 2,
                      borderColor: 'divider',
                      bgcolor: (theme) => alpha(theme.palette.background.default, 0.5),
                      p: 1.5,
                      borderRadius: 1,
                    }}
                  >
                    "{highlightKeywords(source.content.substring(0, 400), keywords)}{source.content.length > 400 ? '...' : ''}"
                  </Typography>
                </Paper>
              ))}
            </Box>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Technical Analysis */}
      {result.technical_analysis && (
        <Accordion sx={{ mt: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendingUp fontSize="small" color="success" />
              <Typography variant="subtitle1" fontWeight="bold">
                Technical Analysis
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box 
              component="pre" 
              sx={{ 
                whiteSpace: 'pre-wrap', 
                wordWrap: 'break-word',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                bgcolor: 'background.default',
                p: 2,
                borderRadius: 1,
                overflow: 'auto'
              }}
            >
              {JSON.stringify(result.technical_analysis, null, 2)}
            </Box>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Integrated Answer */}
      {result.integrated_answer && (
        <Accordion sx={{ mt: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1" fontWeight="bold">
              Integrated Analysis
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
              {result.integrated_answer}
            </Typography>
          </AccordionDetails>
        </Accordion>
      )}
    </Box>
  );
};

export default RAGResultDisplay;
