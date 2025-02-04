# services/aliexpress.py
import requests
import logging
from config import ALIEXPRESS_API_KEY, ALIEXPRESS_API_URL

logger = logging.getLogger(__name__)

def get_product_info(product_link):
    """
    Fetch product info from AliExpress using their API.
    
    You must sign up for the AliExpress Affiliate/API program and obtain an API key.
    ALIEXPRESS_API_URL should point to the correct endpoint.
    """
    params = {
        'api_key': ALIEXPRESS_API_KEY,
        'product_url': product_link
    }
    
    try:
        response = requests.get(ALIEXPRESS_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Error calling AliExpress API: %s", e)
        raise
