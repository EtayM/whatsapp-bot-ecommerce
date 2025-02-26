# services/nocodb.py

import requests
import logging
import json

from services.state import State
from config import NOCODB_API_BASE_URL, NOCODB_API_KEY
logger = logging.getLogger(__name__)

TABLE_RECORDS_ENDPOINT="api/v2/tables/"

CHATS_TABLE_ID = "myd0mpbrbpy3pm1"
CATEGORIES_TABLE_ID = "mbr8dwnprhoi34d"
SUB_CATEGORIES_TABLE_ID = "mhq2ssap9fngceo"

def str_to_state(data: str) -> State:
    return State.__members__.get(data, State.UNKNOWN)

def fetch_table_records(table_id):
    url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + table_id + "/records"
    Headers = { "xc-token" : NOCODB_API_KEY }
    try:
        response = requests.get(url, headers=Headers)
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
        _, phone_number, current_state = parse_chat_data(fetched_user)
        if not phone_number or not current_state:
            insert_new_chat(number)
            return number, State.UNKNOWN
        return phone_number, str_to_state(current_state)

    except requests.RequestException as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "get_user_state", "nocodb API", number)
        raise
    
def fetch_user(phone_number):
    url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + CHATS_TABLE_ID + "/records"
    headers = { "xc-token" : NOCODB_API_KEY }
    querystring = {"where":f"(phone_number,eq,{phone_number})"}
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
        return None, None, None
    row_id = list[0].get("Id", [])
    phone_number = list[0].get("phone_number", [])
    current_state = list[0].get("current_state", [])
    if not row_id or not phone_number or not current_state:
        return None, None, None
    return row_id, phone_number, current_state

def insert_new_chat(phone_number):
    url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + CHATS_TABLE_ID + "/records"
    headers = { "xc-token" : NOCODB_API_KEY }
    payload = {
        "phone_number": phone_number
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

def update_user_state(phone_number, new_state: State):
    try:
        fetched_user = fetch_user(phone_number)
        row_id, _, current_state_str = parse_chat_data(fetched_user)
        if not row_id or not _ or not current_state_str:
            logger.error("Error")
            raise
        current_state = str_to_state(current_state_str)

        if current_state == new_state:
            logger.info(f"Aborting update_user_state because user is already in {new_state} state.")
            return
        url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + CHATS_TABLE_ID + "/records"
        headers = { "xc-token" : NOCODB_API_KEY }
        payload = {
            "id": row_id,
            "current_state": new_state.name
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
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "get_categories", "nocodb API", CATEGORIES_TABLE_ID)

    categories = []
    for category_data in categories_data['list']:
        categories.append({'Id':int(category_data['Id']), 'Name': str(category_data['Name'])})
    return categories
    # product_info = get_products_info(products)
    # products_info = get_products_info_async(products)
    # products_info_to_send = "\n".join(
    #     f"{i+1}. Name: {truncate(product['name'])}\nCategory: {product['category']}\nImage URL: {product['image_url']}"
    #     for i, product in enumerate(product_info)
    # )
    # products_info_to_send = "\n".join(
    #     f"{i+1}. Name: {truncate(product['name'])}\nCategory: {product['category']}"
    #     for i, product in enumerate(product_info)
    # )
    # print(f"\n\n\n\n\n\n\n\n {products_info_to_send}")

def get_sub_categories():
    try:
        categories_data = fetch_table_records(SUB_CATEGORIES_TABLE_ID)
        logger.debug("Sub-Categories: %s", categories_data)
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "get_sub_categories", "nocodb API", SUB_CATEGORIES_TABLE_ID)

    categories = []
    for category_data in categories_data['list']:
        categories.append({"category_id":int(category_data['id']), "category_name": str(category_data['Name'])})
    return json.dumps(categories)