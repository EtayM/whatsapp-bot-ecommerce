import requests
import logging
from config import META_WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID

logger = logging.getLogger(__name__)
WHATSAPP_API_BASE_URL = "https://graph.facebook.com/v21.0"  # Adjust version as needed

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
        "text": {"body": message_text}
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    except requests.RequestException as err:
        from services.helpers import handle_api_error
        handle_api_error(err, "send_whatsapp_message", "WhatsApp Cloud API", payload)
        return {"error": str(err)}

    try:
        return response.json()
    except ValueError:
        from services.helpers import handle_api_error
        handle_api_error(ValueError("Invalid JSON response"), "send_whatsapp_message", "WhatsApp Cloud API", response.text)
        return {"error": "Invalid JSON response"}



def send_whatsapp_interactive_message(recipient_id, body_text, button_payload, button_text):
    """
    Sends an interactive (button) message.
    The button payload (e.g. "FIND_BEST_DEAL") will be returned when the user clicks it.
    """
    url = f"{WHATSAPP_API_BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": button_payload, "title": button_text}
                    }
                ]
            }
        }
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "send_whatsapp_interactive_message", "WhatsApp Cloud API", payload)
        return {"error": str(e)}
    
def send_whatsapp_message_image_and_buttons(recipient_id, body_text, media_id, buttons=None):
    """
    Sends a WhatsApp message with an image, text, and optional buttons.

    :param recipient_id: WhatsApp recipient ID
    :param body_text: Message text
    :param media_id: ID of the pre-uploaded media (image)
    :param buttons: List of tuples (button_payload, button_text) or None
    :return: API response JSON
    """
    url = f"{WHATSAPP_API_BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "image",
                "image": {
                    "id": media_id  # Use pre-uploaded media ID
                }
            },
            "body": {
                "text": body_text
            }
        }
    }

    # If buttons are provided, add them to payload
    if buttons:
        payload["interactive"]["action"] = {
            "buttons": [
                {
                    "type": "reply",
                    "reply": {
                        "id": button_payload,
                        "title": button_text
                    }
                }
                for button_payload, button_text in buttons
            ]
        }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "send_whatsapp_message_image_and_buttons", "WhatsApp Cloud API", payload)
        return {"error": str(e)}

def parse_incoming_message(request_body):
    """
    Extracts relevant data (sender ID, message text, button clicks, etc.)
    from the webhook payload.
    """
    # Adjust to match the actual JSON structure from WhatsApp
    entry = request_body.get("entry", [])
    if not entry:
        return None, None, None

    changes = entry[0].get("changes", [])
    if not changes:
        return None, None, None

    messages = changes[0].get("value", {}).get("messages", [])
    if not messages:
        return None, None, None

    msg = messages[0]
    sender_id = msg["from"]  # The user's phone number in WhatsApp
    message_text = ""

    # If it's a text message
    if msg.get("text"):
        message_text = msg["text"]["body"]

    # If it's a button reply
    if msg.get("interactive", {}).get("button_reply", {}):
        message_text = msg["interactive"]["button_reply"]["id"]

    message_id = msg["id"]  # WhatsApp's unique message ID
    return sender_id, message_text, message_id
