// src/components/dashboard/Dashboard.tsx
import React, { useEffect } from 'react';
import {
  AppBar,
  Box,
  Container,
  Toolbar,
  Typography,
  IconButton,
  Button,
  Grid,
  Paper,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Chip,
} from '@mui/material';
import {
  Logout,
  AccountCircle,
  TrendingUp,
  Assessment,
  History,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logout } from '../../store/authSlice';
import { fetchQueries } from '../../store/querySlice';
import { AppDispatch, RootState } from '../../store/store';
import QueryInput from './QueryInput';
import QueryHistory from './QueryHistory';
import ResultDisplay from './ResultDisplay';
import ThemeToggle from '../common/ThemeToggle';

const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);
  const { currentQuery, queries } = useSelector((state: RootState) => state.query);
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

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
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="static"
        elevation={0}
        sx={{
          background: (theme) =>
            theme.palette.mode === 'dark'
              ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)'
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
      <Box
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          pt: 4,
          pb: 4,
        }}
      >
        <Container maxWidth="xl">
          <Grid container spacing={3}>
            {/* Left Column - Query Input */}
            <Grid item xs={12} md={4}>
              <Paper
                elevation={2}
                sx={{
                  p: 3,
                  height: '100%',
                  background: (theme) =>
                    theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)'
                      : 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Assessment sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6" fontWeight="bold">
                    Ask TA Agent
                  </Typography>
                </Box>
                <QueryInput />
              </Paper>
            </Grid>

            {/* Middle Column - Results */}
            <Grid item xs={12} md={5}>
              <Paper elevation={2} sx={{ p: 3, minHeight: 500 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                  <Typography variant="h6" fontWeight="bold">
                    Results
                  </Typography>
                  {currentQuery && (
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
                </Box>
                {currentQuery ? (
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
                    <Assessment sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      No query selected
                    </Typography>
                    <Typography variant="body2" color="text.disabled">
                      Submit a query or select from history
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>

            {/* Right Column - Query History */}
            <Grid item xs={12} md={3}>
              <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <History sx={{ mr: 1, color: 'secondary.main' }} />
                  <Typography variant="h6" fontWeight="bold">
                    Query History
                  </Typography>
                </Box>
                <QueryHistory />
              </Paper>
            </Grid>
          </Grid>

          {/* Stats Cards */}
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  textAlign: 'center',
                  background: (theme) =>
                    theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)'
                      : 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)',
                }}
              >
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {queries.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Queries
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  textAlign: 'center',
                  background: (theme) =>
                    theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%)'
                      : 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%)',
                }}
              >
                <Typography variant="h4" fontWeight="bold" color="primary.main">
                  {queries.filter((q) => q.status === 'completed').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completed
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  textAlign: 'center',
                  background: (theme) =>
                    theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%)'
                      : 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%)',
                }}
              >
                <Typography variant="h4" fontWeight="bold" color="secondary.main">
                  AI
                </Typography>
                <Typography variant="body2" color="text.secondary">
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
