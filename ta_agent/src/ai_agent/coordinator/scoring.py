"""
Composite Scoring Module
Combines multiple analysis scores into weighted composite
"""
from typing import Dict, Optional
import statistics

from .constants import SCORE_THRESHOLDS
from ...core.logging import logger


class CompositeScorer:
    """
    Composite Score Calculator
    
    Combines:
    - Technical Analysis Score
    - Sentiment Analysis Score
    - Risk Assessment Score
    
    With configurable weights to produce final composite score
    """
    
    def __init__(self):
        self.thresholds = SCORE_THRESHOLDS['composite']
    
    def calculate_composite(
        self,
        technical: Dict,
        sentiment: Optional[Dict],
        risk: Dict,
        weights: Dict[str, float]
    ) -> Dict:
        """
        Calculate weighted composite score
        
        Args:
            technical: Technical analysis result
            sentiment: Sentiment analysis result (optional)
            risk: Risk assessment result
            weights: Weight configuration
            
        Returns:
            Composite score dictionary
        """
        logger.info("🎲 Calculating composite score...")
        
        # Extract scores
        tech_score = technical['score']
        risk_score = risk['score']
        
        # Handle sentiment (may be None if disabled)
        if sentiment:
            sent_score = sentiment['composite_score']
            sent_weight = weights['sentiment']
        else:
            sent_score = 0
            sent_weight = 0
            # Redistribute sentiment weight
            weights = {
                'technical': weights['technical'] + sent_weight / 2,
                'sentiment': 0,
                'risk': weights['risk'] + sent_weight / 2
            }
        
        # Calculate weighted composite
        composite_score = (
            tech_score * weights['technical'] +
            sent_score * weights['sentiment'] +
            risk_score * weights['risk']
        )
        
        # Calculate confidence based on agreement between scores
        confidence = self._calculate_confidence(
            tech_score, sent_score, risk_score, sentiment
        )
        
        # Classify composite score
        label = self._classify_score(composite_score)
        
        return {
            'score': composite_score,
            'label': label,
            'confidence': confidence,
            'components': {
                'technical': tech_score,
                'sentiment': sent_score if sentiment else None,
                'risk': risk_score
            }
        }
    
    def _calculate_confidence(
        self,
        tech_score: float,
        sent_score: float,
        risk_score: float,
        sentiment: Optional[Dict]
    ) -> float:
        """
        Calculate confidence based on agreement between scores
        
        Low variance = high confidence (scores agree)
        High variance = low confidence (scores disagree)
        """
        scores = [tech_score, sent_score, risk_score] if sentiment else [tech_score, risk_score]
        
        # Measure agreement (low variance = high confidence)
        if len(scores) > 1:
            variance = statistics.stdev(scores)
        else:
            variance = 0.5
        
        agreement_factor = max(0.5, 1.0 - variance)
        
        # Base confidence from data quality
        base_confidence = 0.7
        if sentiment and sentiment.get('confidence'):
            base_confidence = (base_confidence + sentiment['confidence']) / 2
        
        confidence = base_confidence * agreement_factor
        
        return confidence
    
    def _classify_score(self, score: float) -> str:
        """Classify composite score into label"""
        if score > self.thresholds['strong_buy']:
            return "Strong Buy Signal"
        elif score > self.thresholds['buy']:
            return "Buy Signal"
        elif score > self.thresholds['neutral_high']:
            return "Neutral"
        elif score > self.thresholds['sell']:
            return "Sell Signal"
        else:
            return "Strong Sell Signal"
