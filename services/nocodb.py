# services/nocodb.py

import requests
import logging
import json

from config import NOCODB_API_BASE_URL, NOCODB_API_KEY
logger = logging.getLogger(__name__)

TABLE_RECORDS_ENDPOINT="api/v2/tables/"

CHATS_TABLE_ID = "myd0mpbrbpy3pm1"
CATEGORIES_TABLE_ID = "mbr8dwnprhoi34d"
SUB_CATEGORIES_TABLE_ID = "mhq2ssap9fngceo"

def fetch_table_records(table_id, querystring=None):
    url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + table_id + "/records"
    headers = { "xc-token" : NOCODB_API_KEY }
    try:
        if not querystring:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        logger.debug("nocodb endpoint response: %s", response.text)
        return response.json()
    except requests.RequestException as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "fetch_table_records", "nocodb API", table_id)
        raise

def get_user_state(number):
    try:
        fetched_user = fetch_user(number)
        row_id, phone_number, state_name, subcategory_id = parse_chat_data(fetched_user)
        if not phone_number or not state_name:
            insert_new_chat(number)
            return number, "UNKNOWN", None # Default state, no subcategory
        return phone_number, state_name, subcategory_id
    except requests.RequestException as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "get_user_state", "nocodb API", number)
        raise
    
def fetch_user(phone_number):
    url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + CHATS_TABLE_ID + "/records"
    headers = { "xc-token" : NOCODB_API_KEY }
    querystring = {"where":f"(PhoneNumber,eq,{phone_number})"}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        logger.debug("nocodb endpoint response: %s", response.text)
        return response.json()
    except requests.RequestException as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "fetch_user", "nocodb API", phone_number)
        raise

def parse_chat_data(data):
    """
    Extracts relevant data (sender ID, message text, button clicks, etc.)
    from the webhook payload.
    """
    # Adjust to match the actual JSON structure from WhatsApp
    list = data.get("list", [])
    if not list:
        return None, None, None, None
    row_id = list[0].get("Id", [])
    phone_number = list[0].get("PhoneNumber", []) # Upper camel case
    state_name = list[0].get("StateName", []) # Upper camel case
    subcategory_id = list[0].get("SubcategoryId", []) # Upper camel case
    if not row_id or not phone_number or not state_name:
        return None, None, None, None
    return row_id, phone_number, state_name, subcategory_id

def insert_new_chat(phone_number):
    url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + CHATS_TABLE_ID + "/records"
    headers = { "xc-token" : NOCODB_API_KEY }
    payload = {
        "PhoneNumber": phone_number, # Upper camel case
        "StateName": "UNKNOWN", # Default state # Upper camel case
        "SubcategoryId": None # No subcategory yet # Upper camel case
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        logger.debug("nocodb insert endpoint response: %s", response.text)
        return response.json()
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "insert_new_chat", "nocodb API", payload)
        raise

def update_user_state(phone_number, new_state_name: str, subcategory_id = None):
    try:
        fetched_user = fetch_user(phone_number)
        row_id, _, current_state_name, _ = parse_chat_data(fetched_user)
        if not current_state_name:
            logger.error("Error")
            #raise # Remove raise

        if current_state_name == new_state_name:
            logger.info(f"Aborting update_user_state because user is already in {new_state_name} state.")
            return
        url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + CHATS_TABLE_ID + "/records"
        headers = { "xc-token" : NOCODB_API_KEY }
        payload = {
            "Id": row_id,
            "StateName": new_state_name, # Changed from current_state # Upper camel case
            "SubcategoryId": subcategory_id # Upper camel case
        }

        response = requests.patch(url, headers=headers, data=payload)
        response.raise_for_status()
        logger.debug("nocodb insert endpoint response: %s", response.text)
        return response.json()
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "update_user_state", "nocodb API", payload)
        raise

def get_categories():
    try:
        categories_data = fetch_table_records(CATEGORIES_TABLE_ID)
        logger.debug("Categories: %s", categories_data)
    except requests.RequestException as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "get_categories", "nocodb API", CATEGORIES_TABLE_ID)
        raise

    categories = []
    for category_data in categories_data['list']:
        categories.append({'Id':str(category_data['CategoryId']), 'Name': str(category_data['Name'])})
    return categories

def get_sub_categories(category_id):
    try:
        sub_categories_data = fetch_table_records(SUB_CATEGORIES_TABLE_ID, {"where":f"(CategoryId,eq,{category_id})"}) # Upper camel case
        logger.debug("Sub-Categories: %s", sub_categories_data)
    except requests.RequestException as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "get_sub_categories", "nocodb API", SUB_CATEGORIES_TABLE_ID)
        raise

    sub_categories = []
    for sub_category_data in sub_categories_data['list']:
        sub_categories.append({'Id':str(sub_category_data['SubCategoryId']), 'Name': str(sub_category_data['Name'])}) # Upper camel case
    
    return sub_categories