"""
Custom exceptions for the application.
"""


class TAAgentException(Exception):
    """Base exception for TA Agent"""
    pass


class DataFetchError(TAAgentException):
    """Error fetching market data"""
    pass


class AnalysisError(TAAgentException):
    """Error during technical analysis"""
    pass


class AIServiceError(TAAgentException):
    """Error with AI service"""
    pass


class AuthenticationError(TAAgentException):
    """Authentication failed"""
    pass


class AuthorizationError(TAAgentException):
    """Authorization failed"""
    pass


class ValidationError(TAAgentException):
    """Validation error"""
    pass


class CacheError(TAAgentException):
    """Cache operation error"""
    pass
