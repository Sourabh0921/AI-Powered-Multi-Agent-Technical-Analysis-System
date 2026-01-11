// src/components/dashboard/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  AppBar,
  Toolbar,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Chip,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Logout,
  TrendingUp,
  Assessment,
  History,
  CompareArrows,
  Description,
  CloudUpload,
  ChevronLeft,
  ChevronRight,
  Menu as MenuIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logout } from '../../store/authSlice';
import { fetchQueries } from '../../store/querySlice';
import { AppDispatch, RootState } from '../../store/store';
import QueryInput from './QueryInput';
import QueryHistory from './QueryHistory';
import ResultDisplay from './ResultDisplay';
import StockComparison from './StockComparison';
import ComparisonDisplay from './ComparisonDisplay';
import DocumentUpload from './DocumentUpload';
import RAGQuery from './RAGQuery';
import RAGResultDisplay from './RAGResultDisplay';
import ThemeToggle from '../common/ThemeToggle';
import { RAGQueryResponse } from '../../services/ragService';

const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);
  const { currentQuery, comparisonData, queries } = useSelector((state: RootState) => state.query);
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [activeView, setActiveView] = useState(0);
  const [ragResult, setRagResult] = useState<RAGQueryResponse | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    dispatch(fetchQueries({ skip: 0, limit: 20 }));
  }, [dispatch]);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* App Bar */}
      <AppBar
        position="static"
        elevation={2}
        sx={{
          background: (theme) =>
            theme.palette.mode === 'dark'
              ? 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)'
              : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 40,
                height: 40,
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.2)',
                mr: 2,
              }}
            >
              <TrendingUp sx={{ color: 'white' }} />
            </Box>
            <Typography variant="h6" component="div" fontWeight="bold">
              TA Agent Dashboard
            </Typography>
          </Box>

          <ThemeToggle />

          <IconButton color="inherit" onClick={handleMenu} sx={{ ml: 1 }}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'rgba(255, 255, 255, 0.2)' }}>
              {user?.username?.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem disabled>
              <Box>
                <Typography variant="subtitle2">{user?.full_name || user?.username}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {user?.email}
                </Typography>
              </Box>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <Logout fontSize="small" sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, pt: { xs: 2, md: 3 }, pb: { xs: 2, md: 3 } }}>
        <Container maxWidth="xl">
          <Grid container spacing={{ xs: 2, md: 3 }}>
            {/* Left Column - Query History - Collapsible */}
            {!sidebarCollapsed && (
              <Grid item xs={12} md={3} sx={{ display: { xs: 'none', md: 'block' } }}>
                <Paper
                  elevation={3}
                  sx={{
                    p: 2.5,
                    height: { md: '600px', lg: '650px' },
                    display: 'flex',
                    flexDirection: 'column',
                    position: 'relative',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                    transition: 'box-shadow 0.3s ease',
                    '&:hover': {
                      boxShadow: '0 8px 30px rgba(0, 0, 0, 0.12)',
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <History sx={{ mr: 1, color: 'secondary.main' }} />
                    <Typography variant="h6" fontWeight="bold">
                      History
                    </Typography>
                    <Chip label={queries.length} size="small" color="secondary" sx={{ ml: 'auto', mr: 1 }} />
                    <IconButton 
                      size="small" 
                      onClick={() => setSidebarCollapsed(true)}
                      sx={{ 
                        color: 'text.secondary',
                        transition: 'all 0.2s ease',
                        '&:hover': { 
                          bgcolor: 'action.hover',
                          transform: 'scale(1.1)',
                        }
                      }}
                    >
                      <ChevronLeft />
                    </IconButton>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
                    <QueryHistory />
                  </Box>
                </Paper>
              </Grid>
            )}

            {/* Collapse/Expand Button */}
            {sidebarCollapsed && (
              <Box
                sx={{
                  position: 'fixed',
                  left: 0,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  zIndex: 1200,
                  display: { xs: 'none', md: 'block' },
                }}
              >
                <Paper
                  elevation={3}
                  sx={{
                    borderRadius: '0 8px 8px 0',
                    overflow: 'hidden',
                  }}
                >
                  <IconButton
                    onClick={() => setSidebarCollapsed(false)}
                    sx={{
                      borderRadius: '0 8px 8px 0',
                      py: 4,
                      px: 0.5,
                      color: 'primary.main',
                      '&:hover': {
                        bgcolor: 'primary.light',
                        color: 'white',
                      },
                    }}
                  >
                    <ChevronRight />
                  </IconButton>
                </Paper>
              </Box>
            )}

            {/* Middle Column - Query Input / Comparison Toggle */}
            <Grid item xs={12} md={sidebarCollapsed ? 4 : 3}>
              <Paper
                elevation={3}
                sx={{
                  height: { xs: 'auto', md: '600px', lg: '650px' },
                  overflow: 'hidden',
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                  transition: 'box-shadow 0.3s ease',
                  '&:hover': {
                    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.12)',
                  },
                }}
              >
                <Tabs
                  value={activeView}
                  onChange={(_, newValue) => setActiveView(newValue)}
                  variant="fullWidth"
                  sx={{
                    borderBottom: 1,
                    borderColor: 'divider',
                    minHeight: 56,
                    '& .MuiTab-root': {
                      minHeight: 56,
                      fontSize: '0.75rem',
                      minWidth: 'auto',
                      px: 1,
                    },
                  }}
                >
                  <Tab label="Query" icon={<Assessment fontSize="small" />} iconPosition="top" />
                  <Tab label="Compare" icon={<CompareArrows fontSize="small" />} iconPosition="top" />
                  <Tab label="RAG" icon={<Description fontSize="small" />} iconPosition="top" />
                  <Tab label="Upload" icon={<CloudUpload fontSize="small" />} iconPosition="top" />
                </Tabs>

                <Box
                  sx={{
                    p: 2.5,
                    height: 'calc(100% - 56px)',
                    overflow: 'auto',
                    background: (theme) =>
                      theme.palette.mode === 'dark'
                        ? 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%)'
                        : 'linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)',
                  }}
                >
                  {activeView === 0 && <QueryInput />}
                  {activeView === 1 && <StockComparison />}
                  {activeView === 2 && <RAGQuery onResultChange={setRagResult} />}
                  {activeView === 3 && <DocumentUpload />}
                </Box>
              </Paper>
            </Grid>

            {/* Right Column - Results */}
            <Grid item xs={12} md={sidebarCollapsed ? 8 : 6}>
              <Paper
                elevation={3}
                sx={{
                  p: { xs: 2, md: 3 },
                  height: { xs: 'auto', md: '600px', lg: '650px' },
                  overflow: 'auto',
                  bgcolor: (theme) => (theme.palette.mode === 'dark' ? 'grey.900' : 'white'),
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                  transition: 'box-shadow 0.3s ease',
                  '&:hover': {
                    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.12)',
                  },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  {activeView === 2 ? (
                    <Description sx={{ mr: 1, color: 'primary.main' }} />
                  ) : (
                    <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                  )}
                  <Typography variant="h6" fontWeight="bold">
                    {activeView === 2 ? 'RAG Query Results' : comparisonData ? 'Stock Comparison' : 'Analysis Results'}
                  </Typography>
                  {currentQuery && activeView !== 2 && (
                    <Chip
                      label={currentQuery.status}
                      size="small"
                      color={
                        currentQuery.status === 'completed'
                          ? 'success'
                          : currentQuery.status === 'failed'
                          ? 'error'
                          : 'warning'
                      }
                      sx={{ ml: 2 }}
                    />
                  )}
                  {comparisonData && (
                    <Chip
                      label={`${comparisonData.comparison.length} stocks`}
                      size="small"
                      color="primary"
                      sx={{ ml: 2 }}
                    />
                  )}
                </Box>
                <Divider sx={{ mb: 3 }} />
                {activeView === 2 && ragResult ? (
                  <RAGResultDisplay result={ragResult} />
                ) : comparisonData ? (
                  <ComparisonDisplay 
                    comparison={comparisonData.comparison} 
                    period={comparisonData.period} 
                  />
                ) : currentQuery ? (
                  <ResultDisplay query={currentQuery} />
                ) : (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minHeight: 400,
                      flexDirection: 'column',
                    }}
                  >
                    <Assessment sx={{ fontSize: 80, color: 'text.disabled', mb: 2, opacity: 0.3 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      No Analysis Yet
                    </Typography>
                    <Typography variant="body2" color="text.disabled" textAlign="center">
                      {activeView === 2 ? 'Ask a question about your documents' : 'Submit a query or compare stocks to see results'}
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
          </Grid>

          {/* Stats Cards */}
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <Paper
                elevation={2}
                sx={{
                  p: 3,
                  textAlign: 'center',
                  background: (theme) =>
                    theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)'
                      : 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)',
                  borderLeft: (theme) => `4px solid ${theme.palette.success.main}`,
                  boxShadow: '0 4px 15px rgba(16, 185, 129, 0.2)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(16, 185, 129, 0.3)',
                  },
                }}
              >
                <Typography variant="h3" fontWeight="bold" color="success.main">
                  {queries.length}
                </Typography>
                <Typography variant="body1" color="text.secondary" fontWeight={500}>
                  Total Queries
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper
                elevation={2}
                sx={{
                  p: 3,
                  textAlign: 'center',
                  background: (theme) =>
                    theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%)'
                      : 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%)',
                  borderLeft: (theme) => `4px solid ${theme.palette.primary.main}`,
                }}
              >
                <Typography variant="h3" fontWeight="bold" color="primary.main">
                  {queries.filter((q) => q.status === 'completed').length}
                </Typography>
                <Typography variant="body1" color="text.secondary" fontWeight={500}>
                  Completed
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper
                elevation={2}
                sx={{
                  p: 3,
                  textAlign: 'center',
                  background: (theme) =>
                    theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(124, 58, 237, 0.15) 100%)'
                      : 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%)',
                  borderLeft: (theme) => `4px solid ${theme.palette.secondary.main}`,
                }}
              >
                <Typography variant="h3" fontWeight="bold" color="secondary.main">
                  AI
                </Typography>
                <Typography variant="body1" color="text.secondary" fontWeight={500}>
                  Powered Analysis
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default Dashboard;
