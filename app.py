from flask import Flask, request, jsonify
from config import META_VERIFY_TOKEN, WELCOME_MESSAGE_MEDIA_ID
from services.state import State
from services.wacloud_api import (parse_incoming_message, send_whatsapp_message, send_whatsapp_interactive_message, send_whatsapp_message_image_and_button)
from services.nocodb import fetch_table_records, get_user_state, update_user_state
from services.aliexpress import get_products_info
from services.helpers import truncate


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

@app.route("/aliwebhook", methods=["GET"])
def verify_ali_webhook():
    """
    Webhook verification endpoint required by Meta.
    """
    try:
        data = request.get_json()
        logger.debug("\nReceived webhook payload: %s\n", data)
    except:
        logger.debug("\nno data")
    return "Test", 200

def send_welcome_message(recipient_id, custom_messge=""):
    msg="היי, בבקשה בחר פעולה" if not custom_messge else custom_messge

    send_whatsapp_message_image_and_button(
        recipient_id,
        msg,
        WELCOME_MESSAGE_MEDIA_ID,
        [
            ("VIEW_CATEGORIES", "👀 המומלצים"),
            ("FIND_BEST_DEAL", "🤝 מצא דיל הכי משתלם")
        ]
    )

    # Mark session state as home
    update_user_state(recipient_id, State.HOME)
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
        # logger.debug("Missing sender_id or message_text in payload: %s", data)
        return jsonify({"status": "invalid payload"}), 400

    # FETCHING CHAT DATA FROM DATABASE
    try:
        phone_number, current_state = get_user_state(sender_id)
        logger.info(f"phone_number: {phone_number}, current_state: {current_state}")
    except Exception as e:
        logger.error("Error fetching chat_DB_data: %s", e)
        return send_welcome_message(sender_id, "אירעה שגיאה, אנא נסה שוב.")

    # New session: send welcome interactive message with a "Find Best Deal" button
    if current_state == State.UNKNOWN:
        logger.info("Starting new session for sender: %s", sender_id)
        return send_welcome_message(sender_id)
        
    # HOME STATE
    if current_state == State.HOME:
        # ACTION VIEW CATEGORIES
        if message_text == "VIEW_CATEGORIES":
            update_user_state(sender_id, "VIEW_CATEGORIES")
            try:
                products_data = fetch_table_records("mrevopwotcaj87a")
                logger.debug("Products: %s", products_data)
            except Exception as e:
                logger.error("Error fetching products: %s", e)
                return send_welcome_message(sender_id, "Error fetching product info. Please try again later.")

            products = []
            for product_data in products_data['list']:
                products.append(int(product_data['product_id']))
            
            product_info = get_products_info(products)
            # products_info = get_products_info_async(products)
            # products_info_to_send = "\n".join(
            #     f"{i+1}. Name: {truncate(product['name'])}\nCategory: {product['category']}\nImage URL: {product['image_url']}"
            #     for i, product in enumerate(product_info)
            # )
            products_info_to_send = "\n".join(
                f"{i+1}. Name: {truncate(product['name'])}\nCategory: {product['category']}"
                for i, product in enumerate(product_info)
            )
            print(f"\n\n\n\n\n\n\n\n {products_info_to_send}")
            # print(products)
            # print(products_info)
            # print(product_info)
            # print(', '.join(products))
            send_whatsapp_interactive_message(
                sender_id,
                products_info_to_send,
                "HOME",  # payload that we'll check on button click
                "Back"
            )
            return jsonify({"status": "prompt for product link sent"}), 200
        # ACTION FIND BEST DEAL
        elif message_text == "FIND_BEST_DEAL":
            # Update session to waiting for product link input
            update_user_state(sender_id, State.FIND_BEST_DEAL_AWAITING_LINK)
            # send_whatsapp_message(
            #     sender_id,
            #     "Please paste the link to the AliExpress product, and we'll find the best deal for this product!"
            # )
            send_whatsapp_interactive_message(
                sender_id,
                "אנא הדבק קישור למוצר באליאקספרס, אני אמצא את הדיל הכי משתלם עבור המוצר!",
                "HOME",  # payload that we'll check on button click
                "חזרה"
            )
            return jsonify({"status": "prompt for product link sent"}), 200
        elif message_text == "HOME":
            return send_welcome_message(sender_id)
        else:
            return send_welcome_message(sender_id)
        
        
    # BEST DEAL STATE
    elif current_state == State.FIND_BEST_DEAL_AWAITING_LINK:
        if message_text == "HOME":
            return send_welcome_message(sender_id)
        
        # Check if the message text contains what looks like a valid AliExpress link.
        if message_text.startswith("http") and "aliexpress.com" in message_text:
            # For now, we call the AliExpress service synchronously.
            try:
                product_info = get_product_info(message_text)
                send_whatsapp_message(sender_id, f"Product info: {product_info}")
            except Exception as e:
                logger.error("Error fetching product info: %s", e)
                return send_welcome_message(sender_id, "אירעה שגיאה בשליפת נתוני המוצר. אנא נסה שנית.")
            # Clear the session once done.
            update_user_state(sender_id, State.UNKNOWN)
            return jsonify({"status": "product info sent"}), 200
        else:
            send_whatsapp_interactive_message(
                sender_id,
                "הקישור לא מכיל מוצר מאליאקספרס. אנא בדוק את הקישור ונסה שנית.",
                "HOME",  # payload that we'll check on button click
                "חזרה"
            )
            return jsonify({"status": "invalid link"}), 200

    # Default fallback if the session state is unknown.
    send_whatsapp_message(sender_id, "לא הבנתי את הבקשה. אנא נסה שנית.")
    return jsonify({"status": "unknown state"}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception: %s", e)
    # Optionally, return a generic message to the client.
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
