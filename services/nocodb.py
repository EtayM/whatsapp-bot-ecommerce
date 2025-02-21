# services/nocodb.py

import requests
import logging


from config import NOCODB_API_BASE_URL, NOCODB_API_KEY
logger = logging.getLogger(__name__)

TABLE_RECORDS_ENDPOINT="api/v2/tables/"

CHATS_TABLE_ID = "myd0mpbrbpy3pm1"

def fetch_table_records(table_id):
    url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + table_id + "/records"
    Headers = { "xc-token" : NOCODB_API_KEY }
    try:
        response = requests.get(url, headers=Headers)
        response.raise_for_status()
        logger.debug("nocodb endpoint response: %s", response.text)
        return response.json()
    except requests.RequestException as e:
        logger.error("Error calling nocodb API: %s", e)
        raise

def get_user_state(number):
    try:
        fetched_user = fetch_user(number)
        _, phone_number, current_state = parse_chat_data(fetched_user)
        if not phone_number or not current_state:
            insert_new_chat(number)
            return number, "HOME"
        return phone_number, current_state

    except requests.RequestException as e:
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
        logger.error("Error calling nocodb API: %s", e)
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
        logger.error("Error calling nocodb API: %s", e)
        raise

def update_user_state(phone_number, new_state):
    try:
        fetched_user = fetch_user(phone_number)
        row_id, _, current_state = parse_chat_data(fetched_user)
        if not row_id or not _ or not current_state:
            logger.error("Error", e)
            raise
        if current_state == new_state:
            logger.error("Error", e)
            raise
        url = NOCODB_API_BASE_URL + TABLE_RECORDS_ENDPOINT + CHATS_TABLE_ID + "/records"
        headers = { "xc-token" : NOCODB_API_KEY }
        payload = {
            "id": row_id,
            "current_state": new_state
        }
        response = requests.patch(url, headers=headers, data=payload)
        response.raise_for_status()
        logger.debug("nocodb insert endpoint response: %s", response.text)
        return response.json()
    except Exception as e:
        logger.error("Error calling nocodb API: %s", e)
        raise