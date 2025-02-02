import requests
from config import META_WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID
import logging

logger = logging.getLogger(__name__)

WHATSAPP_API_BASE_URL = "https://graph.facebook.com/v15.0"  # Adjust version as needed

def send_whatsapp_message(recipient_id, message_text):
    """
    Sends a text message via WhatsApp Cloud API.
    """
    url = f"{WHATSAPP_API_BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "text": {
            "body": message_text
        }
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    except requests.RequestException as err:
        logger.error("Failed to send WhatsApp message: %s", err)
        return {"error": str(err)}


    try:
        return response.json()
    except ValueError:
        logger.error("Invalid JSON response from WhatsApp API: %s", response.text)
        return {"error": "Invalid JSON response"}

def parse_incoming_message(request_body):
    """
    Extracts relevant data (sender ID, message text, button clicks, etc.)
    from the webhook payload.
    """
    # Adjust to match the actual JSON structure from WhatsApp
    entry = request_body.get("entry", [])
    if not entry:
        return None, None

    changes = entry[0].get("changes", [])
    if not changes:
        return None, None

    messages = changes[0].get("value", {}).get("messages", [])
    if not messages:
        return None, None

    msg = messages[0]
    sender_id = msg["from"]  # The user's phone number in WhatsApp
    message_text = ""

    # If it's a text message
    if msg.get("text"):
        message_text = msg["text"]["body"]

    # If it's a button reply
    if msg.get("button"):
        message_text = msg["button"]["payload"]

    return sender_id, message_text
