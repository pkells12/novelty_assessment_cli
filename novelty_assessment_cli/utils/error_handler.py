"""
Error handling utilities for Patent Novelty Analyzer.
"""


class PatentAnalyzerError(Exception):
    """Base exception for Patent Novelty Analyzer."""
    pass


class APIConnectionError(PatentAnalyzerError):
    """Raised when an API connection fails."""
    pass


class APIAuthenticationError(PatentAnalyzerError):
    """Raised when API authentication fails."""
    pass


class APIRateLimitError(PatentAnalyzerError):
    """Raised when an API rate limit is exceeded."""
    pass


class InputValidationError(PatentAnalyzerError):
    """Raised when user input validation fails."""
    pass


class ConfigurationError(PatentAnalyzerError):
    """Raised when configuration is invalid or missing."""
    pass


def handle_exceptions(func):
    """Decorator to handle exceptions gracefully.
    
    Args:
        func: The function to wrap.
    
    Returns:
        The wrapped function.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PatentAnalyzerError as e:
            print(f"Error: {str(e)}")
            # You might want to add logging here
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            # You might want to add logging here
            return None
    
    return wrapper
