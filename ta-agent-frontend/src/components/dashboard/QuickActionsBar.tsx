// src/components/dashboard/QuickActionsBar.tsx
import React, { useState } from 'react';
import {
  Box,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  ContentCopy,
  Download,
  Print,
  Share,
  Bookmark,
  BookmarkBorder,
  Notifications,
  NotificationsActive,
  Compare,
  Refresh,
} from '@mui/icons-material';

interface QuickActionsBarProps {
  ticker?: string;
  onCopy?: () => void;
  onDownload?: () => void;
  onPrint?: () => void;
  onRefresh?: () => void;
  onCompare?: () => void;
  onSetAlert?: () => void;
}

const QuickActionsBar: React.FC<QuickActionsBarProps> = ({
  ticker,
  onCopy,
  onDownload,
  onPrint,
  onRefresh,
  onCompare,
  onSetAlert,
}) => {
  const [shareAnchor, setShareAnchor] = useState<null | HTMLElement>(null);
  const [bookmarked, setBookmarked] = useState(false);
  const [alertSet, setAlertSet] = useState(false);
  const [snackbar, setSnackbar] = useState<{open: boolean; message: string; severity: 'success' | 'info'}>({
    open: false,
    message: '',
    severity: 'success'
  });

  const handleShare = (platform: string) => {
    const url = window.location.href;
    const text = `Check out ${ticker || 'this'} analysis on TA Agent`;
    
    let shareUrl = '';
    switch(platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
        break;
      case 'linkedin':
        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
        break;
      case 'copy':
        navigator.clipboard.writeText(url);
        setSnackbar({ open: true, message: 'Link copied to clipboard!', severity: 'success' });
        setShareAnchor(null);
        return;
    }
    
    if (shareUrl) {
      window.open(shareUrl, '_blank', 'width=600,height=400');
    }
    setShareAnchor(null);
  };

  const handleBookmark = () => {
    setBookmarked(!bookmarked);
    setSnackbar({ 
      open: true, 
      message: bookmarked ? 'Removed from watchlist' : 'Added to watchlist', 
      severity: 'success' 
    });
  };

  const handleSetAlert = () => {
    setAlertSet(!alertSet);
    if (onSetAlert) onSetAlert();
    setSnackbar({ 
      open: true, 
      message: alertSet ? 'Alert removed' : 'Alert set successfully', 
      severity: 'success' 
    });
  };

  return (
    <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
      {onCopy && (
        <Tooltip title="Copy Analysis">
          <IconButton size="small" onClick={onCopy}>
            <ContentCopy fontSize="small" />
          </IconButton>
        </Tooltip>
      )}

      {onDownload && (
        <Tooltip title="Download PDF">
          <IconButton size="small" onClick={onDownload}>
            <Download fontSize="small" />
          </IconButton>
        </Tooltip>
      )}

      {onPrint && (
        <Tooltip title="Print">
          <IconButton size="small" onClick={onPrint}>
            <Print fontSize="small" />
          </IconButton>
        </Tooltip>
      )}

      <Tooltip title="Share">
        <IconButton size="small" onClick={(e) => setShareAnchor(e.currentTarget)}>
          <Share fontSize="small" />
        </IconButton>
      </Tooltip>

      {ticker && (
        <>
          <Tooltip title={bookmarked ? "Remove from Watchlist" : "Add to Watchlist"}>
            <IconButton size="small" onClick={handleBookmark}>
              {bookmarked ? <Bookmark fontSize="small" color="primary" /> : <BookmarkBorder fontSize="small" />}
            </IconButton>
          </Tooltip>

          <Tooltip title={alertSet ? "Remove Alert" : "Set Price Alert"}>
            <IconButton size="small" onClick={handleSetAlert}>
              {alertSet ? <NotificationsActive fontSize="small" color="primary" /> : <Notifications fontSize="small" />}
            </IconButton>
          </Tooltip>
        </>
      )}

      {onCompare && (
        <Tooltip title="Compare Stocks">
          <IconButton size="small" onClick={onCompare}>
            <Compare fontSize="small" />
          </IconButton>
        </Tooltip>
      )}

      {onRefresh && (
        <Tooltip title="Refresh Data">
          <IconButton size="small" onClick={onRefresh}>
            <Refresh fontSize="small" />
          </IconButton>
        </Tooltip>
      )}

      {/* Share Menu */}
      <Menu
        anchorEl={shareAnchor}
        open={Boolean(shareAnchor)}
        onClose={() => setShareAnchor(null)}
      >
        <MenuItem onClick={() => handleShare('twitter')}>
          <ListItemIcon>
            <Share fontSize="small" />
          </ListItemIcon>
          <ListItemText>Share on Twitter</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleShare('linkedin')}>
          <ListItemIcon>
            <Share fontSize="small" />
          </ListItemIcon>
          <ListItemText>Share on LinkedIn</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleShare('copy')}>
          <ListItemIcon>
            <ContentCopy fontSize="small" />
          </ListItemIcon>
          <ListItemText>Copy Link</ListItemText>
        </MenuItem>
      </Menu>

      {/* Snackbar Notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default QuickActionsBar;
