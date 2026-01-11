// src/components/dashboard/QueryHistory.tsx
import React, { useEffect, useState } from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Chip,
  IconButton,
  Typography,
  Box,
  CircularProgress,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Sort as SortIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchQueries, fetchQuery, deleteQuery } from '../../store/querySlice';
import { AppDispatch, RootState } from '../../store/store';
import { Query } from '../../types';
import { QueryHistorySkeleton } from '../common/LoadingSkeleton';
import { formatRelativeTime, formatFullTimestamp } from '../../utils/formatters';

const QueryHistory: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { queries, loading, currentQuery } = useSelector((state: RootState) => state.query);

  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'ticker'>('newest');
  const [hoveredId, setHoveredId] = useState<number | null>(null);

  useEffect(() => {
    dispatch(fetchQueries({ skip: 0, limit: 20 }));
  }, [dispatch]);

  const handleQueryClick = (query: Query) => {
    dispatch(fetchQuery(query.id));
  };

  const handleDelete = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Delete this query?')) {
      dispatch(deleteQuery(id));
    }
  };

  const handleRefresh = () => {
    dispatch(fetchQueries({ skip: 0, limit: 20 }));
  };

  // Removed auto-refresh - QueryInput handles polling for active queries

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Filter queries based on search term
  const filteredQueries = queries.filter((query) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      query.query_text?.toLowerCase().includes(searchLower) ||
      query.ticker?.toLowerCase().includes(searchLower)
    );
  });

  // Sort queries
  const sortedQueries = [...filteredQueries].sort((a, b) => {
    if (sortBy === 'newest') {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    } else if (sortBy === 'oldest') {
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    } else if (sortBy === 'ticker') {
      return (a.ticker || '').localeCompare(b.ticker || '');
    }
    return 0;
  });

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Search and Controls */}
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search queries..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 1.5 }}
        />

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <FormControl size="small" fullWidth>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              label="Sort By"
              onChange={(e) => setSortBy(e.target.value as any)}
              startAdornment={<SortIcon fontSize="small" sx={{ ml: 1, mr: -0.5 }} />}
            >
              <MenuItem value="newest">Newest First</MenuItem>
              <MenuItem value="oldest">Oldest First</MenuItem>
              <MenuItem value="ticker">By Ticker</MenuItem>
            </Select>
          </FormControl>
          
          <Tooltip title="Refresh history" arrow>
            <IconButton 
              size="small" 
              onClick={handleRefresh} 
              sx={{ 
                flexShrink: 0,
                transition: 'all 0.2s ease',
                '&:hover': {
                  transform: 'rotate(90deg)',
                  bgcolor: 'action.hover',
                },
              }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Query List */}
      {loading && queries.length === 0 ? (
        <QueryHistorySkeleton />
      ) : sortedQueries.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            {searchTerm ? 'No matching queries' : 'No queries yet'}
          </Typography>
        </Box>
      ) : (
        <List sx={{ flexGrow: 1, overflow: 'auto', px: 0 }}>
          {sortedQueries.map((query) => {
            const queryText = query.query_text || query.ticker || 'No query text';
            const displayText = queryText.length > 45 ? queryText.substring(0, 45) + '...' : queryText;
            const isActive = currentQuery?.id === query.id;
            const isHovered = hoveredId === query.id;
            
            return (
              <Tooltip
                key={query.id}
                title={
                  <Box>
                    <Typography variant="caption" fontWeight="bold">
                      {query.query_text || 'No query text'}
                    </Typography>
                    <br />
                    <Typography variant="caption" color="inherit">
                      {formatFullTimestamp(query.created_at)}
                    </Typography>
                  </Box>
                }
                placement="right"
                arrow
              >
                <ListItem
                  disablePadding
                  sx={{
                    mb: 1,
                    borderRadius: 1.5,
                    bgcolor: isActive
                      ? (theme) =>
                          theme.palette.mode === 'dark'
                            ? 'rgba(59, 130, 246, 0.2)'
                            : 'rgba(102, 126, 234, 0.15)'
                      : 'transparent',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      bgcolor: (theme) =>
                        theme.palette.mode === 'dark'
                          ? 'rgba(255, 255, 255, 0.05)'
                          : 'rgba(0, 0, 0, 0.03)',
                      transform: 'translateX(4px)',
                    },
                  }}
                  onMouseEnter={() => setHoveredId(query.id)}
                  onMouseLeave={() => setHoveredId(null)}
                  secondaryAction={
                    isHovered ? (
                      <Tooltip title="Delete query" arrow>
                        <IconButton
                          edge="end"
                          size="small"
                          onClick={(e) => handleDelete(query.id, e)}
                          sx={{
                            opacity: 0,
                            animation: 'fadeIn 0.2s ease forwards',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              color: 'error.main',
                              transform: 'scale(1.1)',
                            },
                            '@keyframes fadeIn': {
                              from: { opacity: 0 },
                              to: { opacity: 1 },
                            },
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    ) : null
                  }
                >
                  <ListItemButton
                    onClick={() => handleQueryClick(query)}
                    sx={{
                      py: 1.5,
                      px: 2,
                      borderRadius: 1.5,
                    }}
                  >
                    <ListItemText
                      primary={
                        <Typography
                          variant="body2"
                          fontWeight={isActive ? 600 : 400}
                          sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            pr: isHovered ? 4 : 0,
                          }}
                        >
                          {displayText}
                        </Typography>
                      }
                      secondary={
                        <Box sx={{ mt: 0.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip
                            label={query.status}
                            size="small"
                            color={getStatusColor(query.status) as any}
                            sx={{ 
                              height: 20, 
                              fontSize: '0.7rem',
                              fontWeight: 600,
                            }}
                          />
                          {query.ticker && (
                            <Chip
                              label={query.ticker}
                              size="small"
                              variant="outlined"
                              sx={{ 
                                height: 20, 
                                fontSize: '0.7rem',
                              }}
                            />
                          )}
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ ml: 'auto', fontSize: '0.7rem' }}
                          >
                            {formatRelativeTime(query.created_at)}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItemButton>
                </ListItem>
              </Tooltip>
            );
          })}
        </List>
      )}
    </Box>
  );
};

export default QueryHistory;
