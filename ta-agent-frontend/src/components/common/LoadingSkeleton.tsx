// src/components/common/LoadingSkeleton.tsx
import React from 'react';
import { Box, Skeleton, Grid, Paper } from '@mui/material';

export const MetricCardSkeleton: React.FC = () => (
  <Paper sx={{ p: 2.5, textAlign: 'center' }}>
    <Skeleton variant="text" width="60%" sx={{ mx: 'auto', mb: 1 }} />
    <Skeleton variant="text" width="80%" height={40} sx={{ mx: 'auto' }} />
  </Paper>
);

export const AnalysisResultSkeleton: React.FC = () => (
  <Box>
    {/* Header */}
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
      <Skeleton variant="circular" width={24} height={24} sx={{ mr: 1 }} />
      <Skeleton variant="text" width={200} height={32} />
      <Skeleton variant="rounded" width={80} height={24} sx={{ ml: 2, borderRadius: 10 }} />
    </Box>

    {/* Metric Cards */}
    <Grid container spacing={2} sx={{ mb: 3 }}>
      {[1, 2, 3, 4].map((i) => (
        <Grid item xs={6} md={3} key={i}>
          <MetricCardSkeleton />
        </Grid>
      ))}
    </Grid>

    {/* Analysis Section */}
    <Paper sx={{ p: 3, mb: 2 }}>
      <Skeleton variant="text" width={150} height={28} sx={{ mb: 2 }} />
      <Skeleton variant="rectangular" height={200} sx={{ mb: 2, borderRadius: 1 }} />
      <Skeleton variant="text" width="100%" />
      <Skeleton variant="text" width="95%" />
      <Skeleton variant="text" width="90%" />
    </Paper>
  </Box>
);

export const QueryHistorySkeleton: React.FC = () => (
  <Box>
    {[1, 2, 3, 4, 5].map((i) => (
      <Paper key={i} sx={{ p: 2, mb: 1.5 }}>
        <Skeleton variant="text" width="80%" sx={{ mb: 1 }} />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Skeleton variant="rounded" width={70} height={20} sx={{ borderRadius: 10 }} />
          <Skeleton variant="rounded" width={50} height={20} sx={{ borderRadius: 10 }} />
          <Skeleton variant="text" width={60} sx={{ ml: 'auto' }} />
        </Box>
      </Paper>
    ))}
  </Box>
);

export const RAGResultSkeleton: React.FC = () => (
  <Box>
    {/* Question */}
    <Paper sx={{ p: 2, mb: 2, borderRadius: 2 }}>
      <Skeleton variant="text" width={100} height={20} sx={{ mb: 1 }} />
      <Skeleton variant="text" width="90%" height={24} />
      <Skeleton variant="text" width="70%" height={24} />
    </Paper>

    {/* Document Insights */}
    <Paper sx={{ mb: 2 }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Skeleton variant="text" width={180} height={28} />
      </Box>
      <Box sx={{ p: 2 }}>
        <Skeleton variant="text" width="100%" />
        <Skeleton variant="text" width="95%" />
        <Skeleton variant="text" width="90%" />
        <Skeleton variant="text" width="85%" />
        <Box sx={{ mt: 3 }}>
          {[1, 2, 3].map((i) => (
            <Paper key={i} variant="outlined" sx={{ p: 2, mb: 1.5 }}>
              <Skeleton variant="text" width="60%" sx={{ mb: 1 }} />
              <Skeleton variant="text" width="100%" />
              <Skeleton variant="text" width="80%" />
            </Paper>
          ))}
        </Box>
      </Box>
    </Paper>
  </Box>
);

export const ChartSkeleton: React.FC = () => (
  <Paper sx={{ p: 3 }}>
    <Skeleton variant="text" width={200} height={28} sx={{ mb: 2 }} />
    <Skeleton variant="rectangular" height={350} sx={{ borderRadius: 1 }} />
  </Paper>
);
