def truncate(text, max_length=35):
    if len(text) <= max_length:
        return text
    
    words = text.split()
    truncated = ""
    
    for word in words:
        if len(truncated) + len(word) + (1 if truncated else 0) > max_length:
            break
        truncated += (" " if truncated else "") + word

    return truncated + "..." if truncated else text[:max_length] + "..."

import logging

logger = logging.getLogger('__main__')

class APIError(Exception):
    """Custom exception for API errors."""
    pass

def handle_api_error(e, function_name, api_endpoint, params):
    """
    Handles API errors by logging them with context and re-raising a custom exception.
    """
    logger.error(f"Error in {function_name} calling {api_endpoint} with params {params}: {e}")
    raise APIError(f"Error calling {api_endpoint}: {e}")