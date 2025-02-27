import sys
from flask import Flask, request, jsonify
from config import META_VERIFY_TOKEN, WELCOME_MESSAGE_MEDIA_ID
#from services.state import State # No longer needed
from services.nocodb import get_user_state
from services.wacloud_api import parse_incoming_message, send_whatsapp_message_image_and_buttons
from tasks.celery_app import process_message_task, app as celery_app
import logging
from services.state import StateManager
import importlib

# Basic configuration that logs to stdout. Adjust level and format as needed.
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose logging
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize StateManager
state_manager = StateManager()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook_handler():
    if request.method == 'GET':
        return verify_webhook(request)
    
    try:
        payload = request.json
        sender_id, message_text, message_id = parse_incoming_message(payload)
        
        # Get or initialize user state
        phone_number, state_name, _ = get_user_state(sender_id)
        if not state_name:
            state_name = "UNKNOWN" # Default state

        # Queue task for async processing
        process_message_task.delay(
            sender_id=sender_id,
            message_text=message_text,
            state_name=state_name,
            message_id=message_id
        )
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify(status='error'), 500
    
    return jsonify(status='ok'), 200

def verify_webhook(request):
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == META_VERIFY_TOKEN:
        return challenge, 200
    return 'Verification failed', 403

if __name__ == "__main__":
    app.run(port=5000, debug=True)
