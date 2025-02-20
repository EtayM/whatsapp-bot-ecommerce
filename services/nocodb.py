# services/nocodb.py

import requests
import logging


from config import NOCODB_API_BASE_URL, NOCODB_API_KEY
logger = logging.getLogger(__name__)

FETCH_TABLE_RECORDS_ENDPOINT="api/v2/tables/"

def fetch_table_records(table_id):
    url = NOCODB_API_BASE_URL + FETCH_TABLE_RECORDS_ENDPOINT + table_id + "/records"
    Headers = { "xc-token" : NOCODB_API_KEY }
    try:
        response = requests.get(url, headers=Headers)
        response.raise_for_status()
        logger.debug("nocodb endpoint response: %s", response.text)
        return response.json()
    except requests.RequestException as e:
        logger.error("Error calling nocodb API: %s", e)
        raise
