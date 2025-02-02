import logging
import sys
from flask import Flask, request, jsonify
from config import META_VERIFY_TOKEN
from services.wacloud_api import parse_incoming_message, send_whatsapp_message

# Basic configuration that logs to stdout. Adjust level and format as needed.
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more verbose logging
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

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

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Endpoint to receive messages and respond.
    """
    data = request.get_json()
    logger.debug("Received webhook payload: %s", data)

    sender_id, message_text = parse_incoming_message(data)
    
    if sender_id is None or message_text is None:
        logger.debug("Received webhook with missing sender or message: %s", data)
        return jsonify({"status": "invalid payload"}), 400
    
    if sender_id is not None and message_text is not None:

        # Send a basic reply
        response_text = f"Hello! I've received your message: \"{message_text}\""
        response = send_whatsapp_message(sender_id, response_text)
        if 'error' in response:
            logger.error("Error sending message: %s", response.get('error'))
        else:
            logger.info("Message sent successfully to %s", sender_id)


    return jsonify({"status": "received"}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception: %s", e)
    # Optionally, return a generic message to the client.
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
