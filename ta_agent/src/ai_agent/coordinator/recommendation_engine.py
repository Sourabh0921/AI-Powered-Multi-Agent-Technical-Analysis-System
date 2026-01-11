"""
Recommendation Engine Module
Generates final trading recommendations with entry/exit points
"""
from typing import Dict, Optional

from .constants import (
    RECOMMENDATION_THRESHOLDS,
    POSITION_SIZING,
    STOP_LOSS_MULTIPLIER,
    STOP_LOSS_RESISTANCE_MULTIPLIER,
    TAKE_PROFIT_MULTIPLIERS
)
from ...core.logging import logger


class RecommendationEngine:
    """
    Trading Recommendation Generator
    
    Produces:
    - Action (STRONG BUY, BUY, HOLD, SELL, STRONG SELL)
    - Entry/Exit Strategy
    - Stop Loss & Take Profit levels
    - Risk/Reward ratio
    - Position sizing advice
    """
    
    def __init__(self):
        self.thresholds = RECOMMENDATION_THRESHOLDS
        self.position_sizing = POSITION_SIZING
    
    def generate_recommendation(
        self,
        ticker: str,
        technical: Dict,
        sentiment: Optional[Dict],
        risk: Dict,
        composite: Dict
    ) -> Dict:
        """
        Generate final trading recommendation
        
        Args:
            ticker: Stock ticker symbol
            technical: Technical analysis result
            sentiment: Sentiment analysis result (optional)
            risk: Risk assessment result
            composite: Composite score result
            
        Returns:
            Complete recommendation dictionary
        """
        logger.info(f"💡 Generating recommendation for {ticker}")
        
        score = composite['score']
        confidence = composite['confidence']
        
        # Determine action and reasoning
        action, reasoning = self._determine_action(score, confidence)
        
        # Calculate entry/exit strategy
        entry_strategy = self._calculate_entry_strategy(
            action, technical, score, confidence
        )
        
        # Calculate position sizing
        position_size = self._calculate_position_sizing(confidence, risk)
        
        # Determine time horizon
        time_horizon = self._determine_time_horizon(action)
        
        return {
            'action': action,
            'confidence': round(confidence * 100, 1),
            'reasoning': reasoning,
            'entry_strategy': entry_strategy,
            'position_sizing': position_size,
            'time_horizon': time_horizon,
            'key_levels': {
                'support': round(technical['support'], 2),
                'resistance': round(technical['resistance'], 2),
                'current': round(technical['indicators']['close'], 2)
            }
        }
    
    def _determine_action(self, score: float, confidence: float) -> tuple[str, str]:
        """
        Determine trading action and reasoning
        
        Returns:
            Tuple of (action, reasoning)
        """
        if (score > self.thresholds['strong_buy']['score'] and 
            confidence > self.thresholds['strong_buy']['confidence']):
            return "STRONG BUY", "Strong positive signals across all analyses"
        
        elif (score > self.thresholds['buy']['score'] and 
              confidence > self.thresholds['buy']['confidence']):
            return "BUY", "Positive signals with good confidence"
        
        elif (score < self.thresholds['strong_sell']['score'] and 
              confidence > self.thresholds['strong_sell']['confidence']):
            return "STRONG SELL", "Strong negative signals across all analyses"
        
        elif (score < self.thresholds['sell']['score'] and 
              confidence > self.thresholds['sell']['confidence']):
            return "SELL", "Negative signals with good confidence"
        
        else:
            return "HOLD", "Mixed signals or insufficient confidence"
    
    def _calculate_entry_strategy(
        self,
        action: str,
        technical: Dict,
        score: float,
        confidence: float
    ) -> Dict:
        """Calculate entry price, stop loss, and take profit levels"""
        current_price = technical['indicators']['close']
        support = technical['support']
        resistance = technical['resistance']
        
        if action in ["STRONG BUY", "BUY"]:
            entry_price = current_price
            stop_loss = support * STOP_LOSS_MULTIPLIER
            take_profit_1 = resistance * TAKE_PROFIT_MULTIPLIERS[0]
            take_profit_2 = resistance * TAKE_PROFIT_MULTIPLIERS[1]
            risk = entry_price - stop_loss
            reward = take_profit_2 - entry_price
            
        elif action in ["STRONG SELL", "SELL"]:
            entry_price = current_price
            stop_loss = resistance * STOP_LOSS_RESISTANCE_MULTIPLIER
            take_profit_1 = support * TAKE_PROFIT_MULTIPLIERS[0]
            take_profit_2 = support * (2 - TAKE_PROFIT_MULTIPLIERS[1])  # Inverse for short
            risk = stop_loss - entry_price
            reward = entry_price - take_profit_2
            
        else:  # HOLD
            entry_price = current_price
            stop_loss = current_price * STOP_LOSS_MULTIPLIER
            take_profit_1 = current_price * 1.05
            take_profit_2 = current_price * 1.10
            risk = entry_price - stop_loss
            reward = take_profit_1 - entry_price
        
        # Calculate risk/reward ratio
        risk_reward = reward / risk if risk > 0 else 0
        
        return {
            'target_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'risk_reward_ratio': round(risk_reward, 2)
        }
    
    def _calculate_position_sizing(self, confidence: float, risk: Dict) -> str:
        """Calculate recommended position size based on confidence and risk"""
        risk_level = risk['risk_level']
        
        if confidence > 0.7 and risk_level == "Low":
            return self.position_sizing['high_confidence_low_risk']
        elif confidence > 0.6:
            return self.position_sizing['moderate_confidence']
        else:
            return self.position_sizing['low_confidence']
    
    def _determine_time_horizon(self, action: str) -> str:
        """Determine recommended investment time horizon"""
        if action != 'HOLD':
            return '3-6 months'
        else:
            return 'Monitor'
