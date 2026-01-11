# TA Agent Frontend - New Components & Utils Documentation

## 📁 File Structure

```
src/
├── utils/
│   └── currencyUtils.ts          # Currency formatting utilities
├── components/
│   ├── common/
│   │   ├── LoadingSkeleton.tsx   # Loading skeleton components
│   │   └── Sparkline.tsx         # Mini chart component
│   └── dashboard/
│       ├── QuickActionsBar.tsx   # Action buttons component
│       ├── RAGResultDisplay.tsx  # Enhanced RAG results display
│       ├── Dashboard.tsx         # Main dashboard (updated)
│       ├── ResultDisplay.tsx     # Results display (updated)
│       ├── ComparisonDisplay.tsx # Comparison display (updated)
│       └── StockComparison.tsx   # Stock comparison (updated)
└── test/
    └── importVerification.ts     # Verification test file
```

---

## 🛠️ Utilities

### 1. Currency Utils (`utils/currencyUtils.ts`)

Handles currency formatting based on stock exchange.

#### Functions:

**`getCurrencySymbol(ticker: string): string`**
- Returns appropriate currency symbol based on ticker suffix
- Supports: USD ($), INR (₹), GBP (£), EUR (€), JPY (¥), HKD (HK$), CAD (C$), AUD (A$)

**`formatPrice(price: number, ticker: string, decimals?: number): string`**
- Formats price with currency symbol and thousand separators
- Example: `formatPrice(3207.80, 'TCS.NS')` → `"₹3,207.80"`

**`formatPriceChange(change: number, ticker: string, decimals?: number)`**
- Returns formatted price change with color
- Example: `{formatted: '+₹12.50', color: '#10b981', isPositive: true}`

**`formatPercentChange(percentChange: number)`**
- Formats percentage with sign and color
- Example: `{formatted: '-2.35%', color: '#ef4444', isPositive: false}`

#### Usage:
```tsx
import { formatPrice } from '../../utils/currencyUtils';

<Typography>{formatPrice(3207.80, 'TCS.NS')}</Typography>
// Displays: ₹3,207.80
```

---

## 🎨 Common Components

### 2. Loading Skeletons (`components/common/LoadingSkeleton.tsx`)

Pre-built skeleton loaders for different UI sections.

#### Components:
- `MetricCardSkeleton` - For metric cards
- `AnalysisResultSkeleton` - For full analysis view
- `QueryHistorySkeleton` - For query history list
- `RAGResultSkeleton` - For RAG results
- `ChartSkeleton` - For chart placeholders

#### Usage:
```tsx
import { AnalysisResultSkeleton } from '../common/LoadingSkeleton';

{loading ? <AnalysisResultSkeleton /> : <ActualContent />}
```

### 3. Sparkline (`components/common/Sparkline.tsx`)

Lightweight SVG-based mini chart component.

#### Props:
- `data: number[]` - Array of data points
- `width?: number` - Width in pixels (default: 100)
- `height?: number` - Height in pixels (default: 30)
- `color?: string` - Line color
- `showArea?: boolean` - Show filled area (default: false)

#### Usage:
```tsx
import Sparkline from '../common/Sparkline';

<Sparkline 
  data={[100, 105, 103, 108, 112]} 
  width={120} 
  height={30}
  color="#3b82f6"
  showArea={true}
/>
```

---

## 🎯 Dashboard Components

### 4. Quick Actions Bar (`components/dashboard/QuickActionsBar.tsx`)

Reusable action buttons with share, download, print, etc.

#### Props:
```typescript
interface QuickActionsBarProps {
  ticker?: string;
  onCopy?: () => void;
  onDownload?: () => void;
  onPrint?: () => void;
  onRefresh?: () => void;
  onCompare?: () => void;
  onSetAlert?: () => void;
}
```

#### Features:
- Copy to clipboard
- Download PDF
- Print
- Share (Twitter, LinkedIn, Copy Link)
- Add to watchlist
- Set price alerts
- Compare stocks
- Refresh data

#### Usage:
```tsx
import QuickActionsBar from './QuickActionsBar';

<QuickActionsBar
  ticker="AAPL"
  onCopy={handleCopy}
  onDownload={handleDownload}
  onPrint={handlePrint}
/>
```

### 5. Enhanced RAG Result Display (`components/dashboard/RAGResultDisplay.tsx`)

Improved RAG query results with better UX.

#### Features:
- Keyword highlighting in sources
- Confidence color coding
- Individual source actions (copy, save)
- Better visual hierarchy
- Document metadata display
- Collapsible sections

#### Usage:
```tsx
import RAGResultDisplay from './RAGResultDisplay';
import { RAGQueryResponse } from '../../services/ragService';

<RAGResultDisplay result={ragQueryResponse} />
```

---

## 🔄 Updated Components

### 6. Dashboard (`components/dashboard/Dashboard.tsx`)

**Changes:**
- Added RAG result state management
- Responsive grid layout
- Conditional rendering based on active view
- Integration with RAGResultDisplay

**Key Updates:**
```tsx
const [ragResult, setRagResult] = useState<RAGQueryResponse | null>(null);

// Pass callback to RAGQuery
<RAGQuery onResultChange={setRagResult} />

// Conditional rendering in results panel
{activeView === 2 && ragResult ? (
  <RAGResultDisplay result={ragResult} />
) : ...}
```

### 7. Result Display (`components/dashboard/ResultDisplay.tsx`)

**Changes:**
- Loading skeleton integration
- Sparklines in metric cards
- Quick Actions Bar integration
- Responsive grid (xs={12} sm={6} md={3})
- Hover effects on cards
- Currency formatting

### 8. Comparison Display & Stock Comparison

**Changes:**
- Currency formatting with `formatPrice()`
- Updated for all price displays
- Proper currency symbols based on exchange

---

## 📱 Responsive Design

All components support responsive breakpoints:

```tsx
// Metric Cards
<Grid item xs={12} sm={6} md={3}>

// Main Panels
height: { xs: 'auto', md: '600px', lg: '650px' }

// Padding
p: { xs: 2, md: 3 }

// Spacing
spacing={{ xs: 2, md: 3 }}

// History Panel (hidden on mobile)
display: { xs: 'none', md: 'block' }
```

---

## ✅ Testing

Run the import verification:
```bash
# Import the test file in your IDE
# Check console for "✅ All imports successful!"
```

Test currency formatting:
```typescript
import { testCurrency } from './test/importVerification';
testCurrency();
```

---

## 🎨 Color Scheme

### Confidence Colors:
- **Green** (#10b981): High confidence (>80%)
- **Blue** (#3b82f6): Medium confidence (60-80%)
- **Yellow** (#fbbf24): Low confidence (40-60%)
- **Red** (#ef4444): Very low confidence (<40%)

### Price Change Colors:
- **Green** (#10b981): Positive change
- **Red** (#ef4444): Negative change

---

## 🚀 Quick Start

1. **Import currency utils:**
```tsx
import { formatPrice } from '../../utils/currencyUtils';
```

2. **Use in component:**
```tsx
<Typography>{formatPrice(price, ticker)}</Typography>
```

3. **Add loading skeleton:**
```tsx
{loading ? <AnalysisResultSkeleton /> : <YourContent />}
```

4. **Add sparkline to card:**
```tsx
<Sparkline data={priceHistory} width={120} height={30} />
```

5. **Add quick actions:**
```tsx
<QuickActionsBar onCopy={handleCopy} onDownload={handleDownload} />
```

---

## 📝 Notes

- All components are TypeScript-ready
- Material-UI v5 compatible
- Optimized for performance
- Accessible with ARIA labels
- Dark mode support
- Mobile responsive

## 🐛 Troubleshooting

**Currency not showing correctly?**
- Check ticker format includes exchange suffix (e.g., `.NS`, `.BO`)

**Sparkline not rendering?**
- Ensure data array is not empty
- Check that values are numbers, not strings

**RAG results not updating?**
- Verify `onResultChange` callback is passed to RAGQuery
- Check that ragResult state is properly managed in Dashboard

---

## 📚 Related Files

- Type definitions: `src/types/index.ts`
- Services: `src/services/ragService.ts`
- Store: `src/store/querySlice.ts`

---

**Last Updated:** January 10, 2026
**Version:** 2.0.0
