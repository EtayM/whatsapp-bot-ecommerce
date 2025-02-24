# services/aliexpress.py

import time
import hmac
import hashlib
import urllib.parse
import requests
import logging
import re
import concurrent.futures



from config import ALIEXPRESS_API_APP_KEY, ALIEXPRESS_API_APP_SECRET, ALIEXPRESS_API_URL
logger = logging.getLogger(__name__)

SIGN_METHOD = "sha256"
API_METHOD = "aliexpress.affiliate.product.query"

def sign_api_request(params, request_body, app_secret, sign_method):
    """
    This function constructs the base string by concatenating the parameters (sorted by key in lexicographical order) and then
    calculates the HMAC-SHA256 signature using the app_secret.
    
    The expected base string format is:
       base_string = (key1 + value1) + (key2 + value2) + ... + request_body (if any)
    """

    sorted_keys = sorted(params.keys())
    base_string = ''
    for key in sorted_keys:
        base_string += key + params[key]
    if request_body:
        base_string += request_body

    # Compute the signature using HMAC-SHA256
    if sign_method.lower() == "sha256":
        signature = hmac.new(app_secret.encode('utf-8'),
                             base_string.encode('utf-8'),
                             hashlib.sha256).hexdigest()
        return signature
    else:
        raise ValueError("Unsupported sign method: {}".format(sign_method))

def make_ali_express_api_call(parameters):

    params = {
        "app_key": ALIEXPRESS_API_APP_KEY,
        "timestamp": str(int(time.time() * 1000)),
        "sign_method": SIGN_METHOD,
        **parameters  # Unpacking all keys and values from 'parameters'
    }

    request_body = None  # No body for GET requests

    # Generate signature and add it to parameters
    sign = sign_api_request(params, request_body, ALIEXPRESS_API_APP_SECRET, SIGN_METHOD)
    params["sign"] = sign.upper()

    # Construct the full URL with URL-encoded parameters
    base_url = "https://api-sg.aliexpress.com/sync?"
    query_string = urllib.parse.urlencode(params)
    url = base_url + query_string

    # Optionally, send GET request (this part is just for demonstration)
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.debug("AliExpress endpoint response: %s", response.text)
        return response.json()
    except requests.RequestException as e:
        logger.error("Error calling AliExpress API: %s", e)
        raise


def extract_product_id_from_link(product_link):
    return (m.group(1) if (m := re.search(r'item/(\d+)\.html', product_link)) else None)

def get_product_info_from_link(product_link):
    product_id = extract_product_id_from_link(product_link)
    if product_id is None:
        logger.debug("Invalid AliExpress product link: %s", product_link)
        return None
    get_products_info(product_id)

def get_products_info(product_ids):
    """
    Fetch product info from AliExpress using their API.
    """

    params = {
        "product_ids": ",".join(map(str, product_ids)),
        "method": "aliexpress.affiliate.productdetail.get"
    }
    
    try:
        product_info = make_ali_express_api_call(params)
        print(product_info)
        if product_info is None:
            return None
        products=product_info['aliexpress_affiliate_productdetail_get_response']['resp_result']['result']['products']['product']
        # name=products['product_title']
        # category=products['first_level_category_name']
        # image_url=products['product_main_image_url']

        extracted_data = [
            {
                "name": product.get("product_title", ""),
                "category": product.get("first_level_category_name", ""),
                "image_url": product.get("product_main_image_url", "")
            }
            for product in products
        ]
        return extracted_data

        # return f"Name: {name}\nCategory: {category}\nimage: {image_url}"
        # response = requests.get(ALIEXPRESS_API_URL, params=params)
        # response.raise_for_status()
        # return response.json()
    except requests.RequestException as e:
        logger.error("Error: %s", e)
        raise

# def get_products_info_async(product_links):
#     results = []
#     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#         # Submit all tasks to the executor
#         future_to_link = {executor.submit(get_product_info, link): link for link in product_links}
        
#         for future in concurrent.futures.as_completed(future_to_link):
#             link = future_to_link[future]
#             try:
#                 result = future.result()
#                 results.append(result)
#             except Exception as e:
#                 print(f"Error fetching {link}: {e}")
    
#     return results