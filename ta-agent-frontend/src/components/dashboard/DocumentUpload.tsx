// src/components/dashboard/DocumentUpload.tsx
import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  Alert,
  LinearProgress,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  CheckCircle,
  Error as ErrorIcon,
  Close,
} from '@mui/icons-material';
import { uploadDocument, DocumentUploadResponse } from '../../services/ragService';

interface UploadedFile {
  id: string;
  name: string;
  status: 'uploading' | 'success' | 'error';
  message?: string;
  data?: DocumentUploadResponse['data'];
}

const DocumentUpload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [ticker, setTicker] = useState('');
  const [docType, setDocType] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    const fileId = Date.now().toString();
    const newFile: UploadedFile = {
      id: fileId,
      name: selectedFile.name,
      status: 'uploading',
    };

    setUploadedFiles((prev) => [newFile, ...prev]);
    setUploading(true);
    setError(null);

    try {
      const result = await uploadDocument(selectedFile, {
        ticker: ticker || undefined,
        doc_type: docType || undefined,
        description: description || undefined,
        tags: tags || undefined,
      });

      // Update file status to success
      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? {
                ...f,
                status: 'success',
                message: result.message,
                data: result.data,
              }
            : f
        )
      );

      // Reset form
      setSelectedFile(null);
      setTicker('');
      setDocType('');
      setDescription('');
      setTags('');
      
      // Reset file input
      const fileInput = document.getElementById('file-upload-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Upload failed';
      
      // Update file status to error
      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? {
                ...f,
                status: 'error',
                message: errorMessage,
              }
            : f
        )
      );
      
      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const removeUploadedFile = (id: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const getSupportedFormats = () => {
    return ['PDF', 'DOCX', 'TXT', 'MD'];
  };

  return (
    <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CloudUpload />
        Upload Documents
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Upload documents to enhance AI analysis with domain-specific knowledge
      </Typography>

      {/* File Selection */}
      <Box sx={{ mb: 2 }}>
        <input
          id="file-upload-input"
          type="file"
          accept=".pdf,.docx,.txt,.md"
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />
        <label htmlFor="file-upload-input">
          <Button
            variant="outlined"
            component="span"
            startIcon={<Description />}
            fullWidth
            disabled={uploading}
          >
            {selectedFile ? selectedFile.name : 'Choose File'}
          </Button>
        </label>
        <Box sx={{ mt: 1 }}>
          {getSupportedFormats().map((format) => (
            <Chip key={format} label={format} size="small" sx={{ mr: 0.5 }} />
          ))}
        </Box>
      </Box>

      {/* Metadata Fields */}
      <Stack spacing={2} sx={{ mb: 2 }}>
        <TextField
          size="small"
          label="Ticker (Optional)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          placeholder="e.g., AAPL"
          helperText="Associate document with a stock symbol"
        />

        <FormControl size="small">
          <InputLabel>Document Type</InputLabel>
          <Select
            value={docType}
            label="Document Type"
            onChange={(e) => setDocType(e.target.value)}
          >
            <MenuItem value="">None</MenuItem>
            <MenuItem value="earnings_report">Earnings Report</MenuItem>
            <MenuItem value="annual_report">Annual Report</MenuItem>
            <MenuItem value="research">Research Paper</MenuItem>
            <MenuItem value="news">News Article</MenuItem>
            <MenuItem value="analysis">Market Analysis</MenuItem>
            <MenuItem value="other">Other</MenuItem>
          </Select>
        </FormControl>

        <TextField
          size="small"
          label="Description (Optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description of the document"
          multiline
          rows={2}
        />

        <TextField
          size="small"
          label="Tags (Optional)"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="e.g., Q4, 2024, tech"
          helperText="Comma-separated tags"
        />
      </Stack>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Upload Button */}
      <Button
        variant="contained"
        fullWidth
        onClick={handleUpload}
        disabled={!selectedFile || uploading}
        startIcon={uploading ? <LinearProgress /> : <CloudUpload />}
      >
        {uploading ? 'Uploading...' : 'Upload & Process'}
      </Button>

      {/* Upload Progress */}
      {uploading && <LinearProgress sx={{ mt: 2 }} />}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Recent Uploads
          </Typography>
          <List dense>
            {uploadedFiles.map((file) => (
              <ListItem
                key={file.id}
                secondaryAction={
                  <IconButton
                    edge="end"
                    size="small"
                    onClick={() => removeUploadedFile(file.id)}
                  >
                    <Close fontSize="small" />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  {file.status === 'uploading' && <LinearProgress />}
                  {file.status === 'success' && (
                    <CheckCircle color="success" fontSize="small" />
                  )}
                  {file.status === 'error' && <ErrorIcon color="error" fontSize="small" />}
                </ListItemIcon>
                <ListItemText
                  primary={file.name}
                  secondary={
                    file.status === 'success'
                      ? `Processed: ${file.data?.chunks} chunks`
                      : file.message || 'Processing...'
                  }
                  primaryTypographyProps={{
                    variant: 'body2',
                    noWrap: true,
                  }}
                  secondaryTypographyProps={{
                    variant: 'caption',
                    color: file.status === 'error' ? 'error' : 'text.secondary',
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
};

export default DocumentUpload;
