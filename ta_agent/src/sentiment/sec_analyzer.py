"""
SEC Filings Analyzer
Analyzes insider trading (Form 4) and material events (Form 8-K)
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

from .base_analyzer import BaseSentimentAnalyzer, SentimentScore
from ..core.logging import logger


class SECFilingsAnalyzer(BaseSentimentAnalyzer):
    """
    Analyzes SEC filings for sentiment signals.
    
    Analyzes:
    - Form 4: Insider transactions (buying/selling)
    - Form 8-K: Material corporate events
    - Form 10-Q/10-K: Quarterly/Annual reports (mentions/tone)
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://data.sec.gov"
        self.headers = {
            'User-Agent': 'TA-Agent Sentiment Analyzer contact@ta-agent.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
        
        # Event sentiment mapping for 8-K items
        self.event_sentiment = {
            '1.01': ('Entry into Material Agreement', 0.3),
            '1.02': ('Termination of Material Agreement', -0.2),
            '2.01': ('Completion of Acquisition', 0.5),
            '2.02': ('Results of Operations', 0.0),  # Neutral until analyzed
            '2.03': ('Creation of Direct Financial Obligation', -0.1),
            '2.04': ('Triggering Events', -0.5),
            '3.01': ('Notice of Delisting', -0.8),
            '3.02': ('Unregistered Sales of Equity', -0.2),
            '4.01': ('Changes in Control', 0.0),
            '4.02': ('Non-Reliance on Previously Issued Statements', -0.6),
            '5.01': ('Changes in Directors or Officers', 0.0),
            '5.02': ('Departure of Directors/Officers', -0.3),
            '5.03': ('Amendments to Articles of Incorporation', 0.0),
            '7.01': ('Regulation FD Disclosure', 0.0),
            '8.01': ('Other Events', 0.0),
            '9.01': ('Financial Statements', 0.0),
        }
    
    def analyze(
        self,
        ticker: str,
        days: int = 90,
        include_insider: bool = True,
        include_events: bool = True
    ) -> SentimentScore:
        """
        Analyze SEC filings sentiment.
        
        Args:
            ticker: Stock ticker symbol
            days: Days to look back
            include_insider: Analyze Form 4 (insider trading)
            include_events: Analyze Form 8-K (material events)
            
        Returns:
            SentimentScore object
        """
        logger.info(f"Analyzing SEC filings for {ticker} (past {days} days)")
        
        # Get CIK (Central Index Key) for the ticker
        cik = self._get_cik(ticker)
        if not cik:
            logger.warning(f"Could not find CIK for ticker {ticker}")
            return self._empty_score(ticker, "CIK not found")
        
        signals = []
        
        # Analyze insider trading
        if include_insider:
            insider_signal = self._analyze_insider_trading(cik, days)
            if insider_signal:
                signals.append(insider_signal)
        
        # Analyze material events
        if include_events:
            events_signal = self._analyze_material_events(cik, days)
            if events_signal:
                signals.append(events_signal)
        
        if not signals:
            return self._empty_score(ticker, "No recent filings")
        
        # Aggregate signals
        return self._aggregate_sec_sentiment(ticker, signals)
    
    def _get_cik(self, ticker: str) -> Optional[str]:
        """Get CIK (Central Index Key) for a ticker"""
        try:
            # Use SEC's ticker to CIK mapping
            url = f"{self.base_url}/submissions/CIK{ticker}.json"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                # Try alternative approach: search company tickers JSON
                ticker_url = "https://www.sec.gov/files/company_tickers.json"
                ticker_response = requests.get(ticker_url, headers=self.headers, timeout=10)
                
                if ticker_response.status_code == 200:
                    data = ticker_response.json()
                    for entry in data.values():
                        if entry.get('ticker', '').upper() == ticker.upper():
                            cik = str(entry.get('cik_str', '')).zfill(10)
                            return cik
            elif response.status_code == 200:
                data = response.json()
                cik = data.get('cik', '')
                return str(cik).zfill(10)
            
        except Exception as e:
            logger.error(f"Error getting CIK for {ticker}: {e}")
        
        return None
    
    def _analyze_insider_trading(self, cik: str, days: int) -> Optional[Dict]:
        """Analyze Form 4 insider trading"""
        try:
            # Get company filings
            url = f"{self.base_url}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filings = data.get('filings', {}).get('recent', {})
            
            # Filter for Form 4 in recent period
            form_types = filings.get('form', [])
            filing_dates = filings.get('filingDate', [])
            accession_numbers = filings.get('accessionNumber', [])
            
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            form4_filings = []
            for i, form_type in enumerate(form_types):
                if form_type == '4' and filing_dates[i] >= cutoff_date:
                    form4_filings.append({
                        'date': filing_dates[i],
                        'accession': accession_numbers[i]
                    })
            
            if not form4_filings:
                return None
            
            # Analyze transactions (simplified - real implementation would parse XML)
            # For now, count number of Form 4s as proxy for insider activity
            num_filings = len(form4_filings)
            
            # Heuristic: More Form 4 filings can indicate insider buying (bullish)
            # or selling (bearish). Without detailed parsing, we use neutral to slight positive
            if num_filings > 5:
                sentiment = 0.2  # Moderate activity
            elif num_filings > 2:
                sentiment = 0.1  # Some activity
            else:
                sentiment = 0.0  # Limited activity
            
            return {
                'type': 'insider_trading',
                'score': sentiment,
                'count': num_filings,
                'recent_filings': form4_filings[:5],
                'weight': 0.3  # 30% weight in SEC analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing insider trading: {e}")
            return None
    
    def _analyze_material_events(self, cik: str, days: int) -> Optional[Dict]:
        """Analyze Form 8-K material events"""
        try:
            url = f"{self.base_url}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filings = data.get('filings', {}).get('recent', {})
            
            form_types = filings.get('form', [])
            filing_dates = filings.get('filingDate', [])
            primary_docs = filings.get('primaryDocument', [])
            
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Find 8-K filings
            events = []
            for i, form_type in enumerate(form_types):
                if form_type == '8-K' and filing_dates[i] >= cutoff_date:
                    # Extract item numbers from document name if possible
                    doc_name = primary_docs[i] if i < len(primary_docs) else ''
                    
                    events.append({
                        'date': filing_dates[i],
                        'document': doc_name
                    })
            
            if not events:
                return None
            
            # Analyze events (simplified)
            # Real implementation would parse each 8-K to extract item numbers
            event_scores = []
            
            for event in events:
                # Default neutral for events we can't classify
                event_scores.append(0.0)
            
            avg_score = sum(event_scores) / len(event_scores) if event_scores else 0.0
            
            return {
                'type': 'material_events',
                'score': avg_score,
                'count': len(events),
                'events': events[:5],
                'weight': 0.7  # 70% weight in SEC analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing material events: {e}")
            return None
    
    def _aggregate_sec_sentiment(self, ticker: str, signals: List[Dict]) -> SentimentScore:
        """Aggregate SEC signals into overall sentiment"""
        
        scores = [s['score'] for s in signals]
        weights = [s['weight'] for s in signals]
        
        weighted_score = self.weighted_average(scores, weights)
        
        total_filings = sum(s['count'] for s in signals)
        confidence = self.calculate_confidence(total_filings)
        
        metadata = {
            'signals': signals,
            'total_filings': total_filings,
            'analysis_components': [s['type'] for s in signals]
        }
        
        return SentimentScore(
            ticker=ticker,
            source='sec_filings',
            score=weighted_score,
            label=self.classify_score(weighted_score),
            confidence=confidence,
            timestamp=datetime.now(),
            num_samples=total_filings,
            metadata=metadata
        )
    
    def _empty_score(self, ticker: str, reason: str) -> SentimentScore:
        """Return empty sentiment score"""
        return SentimentScore(
            ticker=ticker,
            source='sec_filings',
            score=0.0,
            label=self.classify_score(0.0),
            confidence=0.0,
            timestamp=datetime.now(),
            num_samples=0,
            metadata={'warning': reason}
        )
    
    def get_recent_form4(self, ticker: str, limit: int = 10) -> List[Dict]:
        """Get recent Form 4 filings for a ticker"""
        cik = self._get_cik(ticker)
        if not cik:
            return []
        
        try:
            url = f"{self.base_url}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filings = data.get('filings', {}).get('recent', {})
            
            form_types = filings.get('form', [])
            filing_dates = filings.get('filingDate', [])
            
            form4_list = []
            for i, form_type in enumerate(form_types):
                if form_type == '4' and len(form4_list) < limit:
                    form4_list.append({
                        'date': filing_dates[i],
                        'form': form_type
                    })
            
            return form4_list
            
        except Exception as e:
            logger.error(f"Error getting Form 4 filings: {e}")
            return []
