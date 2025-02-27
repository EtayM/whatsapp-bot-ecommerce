import logging

logger = logging.getLogger('__main__')

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

class APIError(Exception):
    """Custom exception for API errors."""
    pass

def handle_api_error(e, function_name, api_endpoint, params=None):
    """
    Handles API errors by logging them with context and re-raising a custom exception.
    """
    logger.error(f"Error in {function_name} calling {api_endpoint} with params {params}. Error: {e}")
    raise APIError(f"Error calling {api_endpoint}: {e}")

import importlib.util
import sys
from pathlib import Path
from config import LOCALES_DIR, DEFAULT_LANGUAGE, RTL_LANGUAGES

# Cache for loaded language modules
_language_modules = {}

def _load_language_module(language):
    """
    Load a language module from the absolute path.
    Uses caching to avoid repeated loads.
    """
    if language in _language_modules:
        return _language_modules[language]

    try:
        # Construct absolute path to the language file
        lang_file = Path(LOCALES_DIR) / f"{language}.py"
        if not lang_file.exists():
            raise ImportError(f"Language file not found: {lang_file}")

        # Load module from file path
        spec = importlib.util.spec_from_file_location(f"locales.{language}", str(lang_file))
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        
        _language_modules[language] = module
        return module
    except Exception as e:
        logger.error(f"Failed to load language module '{language}': {e}")
        return None

def get_localized_string(language, key):
    """
    Gets a localized string for the given key and language.
    Supports nested keys (e.g. "button.recommended").
    Falls back to default language if string not found.
    Applies RTL formatting if needed.
    
    Args:
        key (str): The string key, can be nested using dots
        language (str): The language code (e.g. 'en', 'he')
        
    Returns:
        str: The localized string
    """
    def get_nested_value(strings_dict, key_parts):
        """Helper to get nested dictionary value"""
        value = strings_dict
        for k in key_parts:
            value = value[k]
        return value

    try:
        # Load the requested language module
        lang_module = _load_language_module(language)
        if lang_module and hasattr(lang_module, 'strings'):
            try:
                # Try to get the string from the requested language
                value = get_nested_value(lang_module.strings, key.split('.'))
                return format_rtl(value, language)
            except (KeyError, AttributeError):
                pass  # Fall through to default language

        # If we're already trying the default language, or if loading fails, return the key
        if language == DEFAULT_LANGUAGE:
            logger.warning(f"String '{key}' not found in default language")
            return key

        # Try default language as fallback
        default_module = _load_language_module(DEFAULT_LANGUAGE)
        if default_module and hasattr(default_module, 'strings'):
            try:
                value = get_nested_value(default_module.strings, key.split('.'))
                return format_rtl(value, language)  # Still apply RTL formatting if needed
            except (KeyError, AttributeError) as e:
                logger.error(f"String '{key}' not found in default language: {e}")

        return key  # Return the key itself as last resort

    except Exception as e:
        logger.error(f"Error getting localized string '{key}' for language '{language}': {e}")
        return key

def format_rtl(text, language):
    """
    Formats text for right-to-left languages.
    """
    if language in RTL_LANGUAGES:
        return f"\u200F{text}"  # Add right-to-left mark
    return text

def get_user_lang(phone_number):
    return "he" if phone_number.startswith("972") else "en"