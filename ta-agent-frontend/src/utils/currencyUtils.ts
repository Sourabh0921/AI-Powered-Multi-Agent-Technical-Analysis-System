// src/utils/currencyUtils.ts
/**
 * Utility functions for currency formatting
 */

/**
 * Get currency symbol based on ticker exchange
 * @param ticker Stock ticker symbol
 * @returns Currency symbol (₹ for Indian stocks, $ for others)
 */
export const getCurrencySymbol = (ticker: string): string => {
  if (!ticker) return '$';
  
  const upperTicker = ticker.toUpperCase();
  
  // Indian stock exchanges
  if (upperTicker.endsWith('.NS') || upperTicker.endsWith('.BO')) {
    return '₹'; // Indian Rupee
  }
  
  // UK stocks
  if (upperTicker.endsWith('.L')) {
    return '£'; // British Pound
  }
  
  // European stocks
  if (upperTicker.endsWith('.PA') || upperTicker.endsWith('.DE') || upperTicker.endsWith('.AS')) {
    return '€'; // Euro
  }
  
  // Japanese stocks
  if (upperTicker.endsWith('.T')) {
    return '¥'; // Japanese Yen
  }
  
  // Hong Kong stocks
  if (upperTicker.endsWith('.HK')) {
    return 'HK$'; // Hong Kong Dollar
  }
  
  // Canadian stocks
  if (upperTicker.endsWith('.TO') || upperTicker.endsWith('.V')) {
    return 'C$'; // Canadian Dollar
  }
  
  // Australian stocks
  if (upperTicker.endsWith('.AX')) {
    return 'A$'; // Australian Dollar
  }
  
  // Default to USD
  return '$';
};

/**
 * Format price with appropriate currency symbol
 * @param price Price value
 * @param ticker Stock ticker symbol
 * @param decimals Number of decimal places (default: 2)
 * @returns Formatted price string with currency symbol
 */
export const formatPrice = (price: number, ticker: string, decimals: number = 2): string => {
  if (price === null || price === undefined || isNaN(price)) {
    return 'N/A';
  }
  
  const symbol = getCurrencySymbol(ticker);
  const formattedValue = price.toFixed(decimals);
  
  // For large numbers, add thousand separators
  const parts = formattedValue.split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  
  return `${symbol}${parts.join('.')}`;
};

/**
 * Format price change with sign and color
 * @param change Price change value
 * @param ticker Stock ticker symbol
 * @param decimals Number of decimal places (default: 2)
 * @returns Object with formatted string and color
 */
export const formatPriceChange = (
  change: number, 
  ticker: string, 
  decimals: number = 2
): { formatted: string; color: string; isPositive: boolean } => {
  if (change === null || change === undefined || isNaN(change)) {
    return { formatted: 'N/A', color: 'inherit', isPositive: false };
  }
  
  const symbol = getCurrencySymbol(ticker);
  const sign = change >= 0 ? '+' : '';
  const color = change >= 0 ? '#10b981' : '#ef4444'; // green : red
  const isPositive = change >= 0;
  
  return {
    formatted: `${sign}${symbol}${Math.abs(change).toFixed(decimals)}`,
    color,
    isPositive
  };
};

/**
 * Format percentage change
 * @param percentChange Percentage change value
 * @returns Object with formatted string and color
 */
export const formatPercentChange = (
  percentChange: number
): { formatted: string; color: string; isPositive: boolean } => {
  if (percentChange === null || percentChange === undefined || isNaN(percentChange)) {
    return { formatted: 'N/A', color: 'inherit', isPositive: false };
  }
  
  const sign = percentChange >= 0 ? '+' : '';
  const color = percentChange >= 0 ? '#10b981' : '#ef4444';
  const isPositive = percentChange >= 0;
  
  return {
    formatted: `${sign}${percentChange.toFixed(2)}%`,
    color,
    isPositive
  };
};
