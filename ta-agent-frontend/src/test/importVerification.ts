// Test file to verify all imports work correctly
// This file is for verification purposes only - do not import in production

// Currency Utils
import { 
  getCurrencySymbol, 
  formatPrice, 
  formatPriceChange, 
  formatPercentChange 
} from '../utils/currencyUtils';

// Loading Skeletons
import {
  MetricCardSkeleton,
  AnalysisResultSkeleton,
  QueryHistorySkeleton,
  RAGResultSkeleton,
  ChartSkeleton
} from '../components/common/LoadingSkeleton';

// Sparkline
import Sparkline from '../components/common/Sparkline';

// Quick Actions Bar
import QuickActionsBar from '../components/dashboard/QuickActionsBar';

// RAG Result Display
import RAGResultDisplay from '../components/dashboard/RAGResultDisplay';

// Test currency formatting
const testCurrency = () => {
  console.log('Testing Currency Utils:');
  console.log('Indian Stock:', formatPrice(3207.80, 'TCS.NS')); // Should show ₹3,207.80
  console.log('US Stock:', formatPrice(259.77, 'AAPL')); // Should show $259.77
  console.log('UK Stock:', formatPrice(150.25, 'HSBA.L')); // Should show £150.25
  console.log('Japanese Stock:', formatPrice(5000, 'SONY.T')); // Should show ¥5,000.00
  
  const priceChange = formatPriceChange(12.50, 'TCS.NS');
  console.log('Price Change:', priceChange); // Should show {formatted: '+₹12.50', color: '#10b981', isPositive: true}
  
  const percentChange = formatPercentChange(-2.35);
  console.log('Percent Change:', percentChange); // Should show {formatted: '-2.35%', color: '#ef4444', isPositive: false}
};

// Test sparkline data
const testSparklineData = [100, 105, 103, 108, 112, 110, 115, 118, 116, 120];

// Export for testing
export {
  testCurrency,
  testSparklineData,
  MetricCardSkeleton,
  AnalysisResultSkeleton,
  QueryHistorySkeleton,
  RAGResultSkeleton,
  ChartSkeleton,
  Sparkline,
  QuickActionsBar,
  RAGResultDisplay,
  getCurrencySymbol,
  formatPrice,
  formatPriceChange,
  formatPercentChange
};

console.log('✅ All imports successful!');
