from flask import Flask, request, jsonify
from config import META_VERIFY_TOKEN, WELCOME_MESSAGE_MEDIA_ID
from services.wacloud_api import (parse_incoming_message, send_whatsapp_message, send_whatsapp_interactive_message, send_whatsapp_message_image_and_button)

# Import logging configuration
import logging
import sys

# Basic configuration that logs to stdout. Adjust level and format as needed.
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose logging
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory session store for demo purposes (keyed by sender_id)
user_sessions = {}

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Bot is running", 200

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    Webhook verification endpoint required by Meta.
    """
    verify_token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if verify_token == META_VERIFY_TOKEN:
        return challenge, 200
    return "Verification token mismatch", 403

def send_welcome_message(recipient_id, custom_messge=""):
    msg="Welcome to the ecommerce bot" if not custom_messge else custom_messge
    # send_whatsapp_interactive_message(
    #     recipient_id,
    #     msg,
    #     "FIND_BEST_DEAL",  # payload that we'll check on button click
    #     "Find Best Deal"
    # )

    send_whatsapp_message_image_and_button(
        recipient_id,
        msg,
        "FIND_BEST_DEAL",  # payload that we'll check on button click
        "🤝 Find Best Deal",
        WELCOME_MESSAGE_MEDIA_ID
    )

    # Mark session state as awaiting feature selection
    user_sessions[recipient_id] = {"state": "awaiting_feature_selection"}
    return jsonify({"status": "welcome message sent"}), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Endpoint to receive messages and respond.
    """
    data = request.get_json()
    logger.debug("\nReceived webhook payload: %s\n", data)
    sender_id, message_text = parse_incoming_message(data)

    if not sender_id or not message_text:
        logger.warning("Missing sender_id or message_text in payload: %s", data)
        return jsonify({"status": "invalid payload"}), 400

    session = user_sessions.get(sender_id)
    logger.debug("\nSession: %s\n", session)

    # New session: send welcome interactive message with a "Find Best Deal" button
    if session is None:
        logger.info("Starting new session for sender: %s", sender_id)
        return send_welcome_message(sender_id)
        
    state = session.get("state")

    # HOME STATE
    if state == "awaiting_feature_selection":
        if message_text == "FIND_BEST_DEAL":
            # Update session to waiting for product link input
            user_sessions[sender_id]["state"] = "awaiting_product_link"
            # send_whatsapp_message(
            #     sender_id,
            #     "Please paste the link to the AliExpress product, and we'll find the best deal for this product!"
            # )
            send_whatsapp_interactive_message(
                sender_id,
                "Please paste the link to the AliExpress product, and we'll find the best deal for this product!",
                "HOME",  # payload that we'll check on button click
                "Back"
            )
            return jsonify({"status": "prompt for product link sent"}), 200
        elif message_text == "HOME":
            return send_welcome_message(sender_id)
        else:
            return send_welcome_message(sender_id)
        
        
    # BEST DEAL STATE
    elif state == "awaiting_product_link":
        if message_text == "HOME":
            return send_welcome_message(sender_id)
        
        # Check if the message text contains what looks like a valid AliExpress link.
        if message_text.startswith("http") and "aliexpress.com" in message_text:
            # For now, we call the AliExpress service synchronously.
            from services.aliexpress import get_product_info
            try:
                product_info = get_product_info(message_text)
                send_whatsapp_message(sender_id, f"Product info: {product_info}")
            except Exception as e:
                logger.error("Error fetching product info: %s", e)
                return send_welcome_message(sender_id, "Error fetching product info. Please try again later.")
            # Clear the session once done.
            user_sessions.pop(sender_id, None)
            return jsonify({"status": "product info sent"}), 200
        else:
            send_whatsapp_interactive_message(
                sender_id,
                "Can't find AliExpress product, please check your link and try again.",
                "HOME",  # payload that we'll check on button click
                "Back"
            )
            return jsonify({"status": "invalid link"}), 200

    # Default fallback if the session state is unknown.
    send_whatsapp_message(sender_id, "I didn't understand that. Please try again.")
    return jsonify({"status": "unknown state"}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception: %s", e)
    # Optionally, return a generic message to the client.
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
