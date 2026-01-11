"""
Constants and Configuration for Multi-Agent Coordinator
"""

# Default analysis weights
DEFAULT_WEIGHTS = {
    'technical': 0.40,  # 40% weight
    'sentiment': 0.35,  # 35% weight
    'risk': 0.25        # 25% weight
}

# Score thresholds for classification
SCORE_THRESHOLDS = {
    'technical': {
        'very_bullish': 0.5,
        'bullish': 0.2,
        'neutral_high': -0.2,
        'bearish': -0.5,
    },
    'composite': {
        'strong_buy': 0.4,
        'buy': 0.15,
        'neutral_high': -0.15,
        'sell': -0.4,
    }
}

# Risk assessment thresholds
RISK_THRESHOLDS = {
    'volatility': {
        'high': 50,      # > 50% annualized
        'moderate': 30,  # 30-50%
        'low': 20        # < 20%
    },
    'drawdown': {
        'severe': -30,   # < -30%
        'high': -20,     # -20% to -30%
        'moderate': -10  # -10% to -20%
    },
    'beta': {
        'very_high': 1.5,  # > 1.5
        'high': 1.2        # 1.2-1.5
    },
    'score_levels': {
        'low': 30,      # < 30 = low risk
        'moderate': 60  # 30-60 = moderate, >60 = high
    }
}

# Recommendation action thresholds
RECOMMENDATION_THRESHOLDS = {
    'strong_buy': {'score': 0.4, 'confidence': 0.65},
    'buy': {'score': 0.2, 'confidence': 0.55},
    'strong_sell': {'score': -0.4, 'confidence': 0.65},
    'sell': {'score': -0.2, 'confidence': 0.55},
}

# RSI thresholds
RSI_THRESHOLDS = {
    'overbought': 70,
    'oversold': 30,
    'neutral_low': 40,
    'neutral_high': 60
}

# Position sizing by confidence and risk
POSITION_SIZING = {
    'high_confidence_low_risk': "5-7% of portfolio",
    'moderate_confidence': "3-5% of portfolio",
    'low_confidence': "1-2% of portfolio (low conviction)"
}

# Stop loss and take profit multipliers
STOP_LOSS_MULTIPLIER = 0.95  # 5% below support
STOP_LOSS_RESISTANCE_MULTIPLIER = 1.05  # 5% above resistance
TAKE_PROFIT_MULTIPLIERS = [1.0, 1.1]  # First TP at resistance, second at +10%
