// src/utils/formatters.ts

/**
 * Format number with commas and optional decimal places
 */
export const formatNumber = (
  value: number | string | undefined | null,
  decimals: number = 2
): string => {
  if (value === undefined || value === null || value === '') return 'N/A';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) return 'N/A';
  
  return numValue.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

/**
 * Format large numbers with K, M, B suffixes
 */
export const formatCompactNumber = (
  value: number | string | undefined | null
): string => {
  if (value === undefined || value === null || value === '') return 'N/A';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) return 'N/A';
  
  const abs = Math.abs(numValue);
  
  if (abs >= 1e9) {
    return (numValue / 1e9).toFixed(2) + 'B';
  } else if (abs >= 1e6) {
    return (numValue / 1e6).toFixed(2) + 'M';
  } else if (abs >= 1e3) {
    return (numValue / 1e3).toFixed(2) + 'K';
  }
  
  return numValue.toFixed(2);
};

/**
 * Format percentage with sign
 */
export const formatPercentage = (
  value: number | string | undefined | null,
  decimals: number = 2,
  includeSign: boolean = true
): string => {
  if (value === undefined || value === null || value === '') return 'N/A';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) return 'N/A';
  
  const sign = includeSign && numValue > 0 ? '+' : '';
  
  return `${sign}${numValue.toFixed(decimals)}%`;
};

/**
 * Format relative time (e.g., "5m ago", "2h ago")
 */
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  
  // For older dates, show the date
  const options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' };
  if (date.getFullYear() !== now.getFullYear()) {
    options.year = 'numeric';
  }
  return date.toLocaleDateString('en-US', options);
};

/**
 * Format full timestamp with date and time
 */
export const formatFullTimestamp = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
};
