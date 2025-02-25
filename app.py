import sys
from flask import Flask, request, jsonify
from config import META_VERIFY_TOKEN, WELCOME_MESSAGE_MEDIA_ID
from services.state import State
from services.nocodb import get_user_state, update_user_state
from services.wacloud_api import parse_incoming_message, send_whatsapp_message_image_and_buttons
from tasks.celery_app import process_message_task, app as celery_app
import services.states as state_handlers
import logging

# Basic configuration that logs to stdout. Adjust level and format as needed.
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose logging
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook_handler():
    if request.method == 'GET':
        return verify_webhook(request)
    
    try:
        payload = request.json
        sender_id, message_text, message_id = parse_incoming_message(payload)
        
        # Get or initialize user state
        phone_number, user_state = get_user_state(sender_id)
        if not user_state:
            user_state = State.UNKNOWN

        # Queue task for async processing
        process_message_task.delay(
            sender_id=sender_id,
            message_text=message_text,
            user_state=user_state.name,
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

def handle_unknown(user_id, message):
    from services.states.unknown import handle_unknown as unknown_handler
    unknown_handler(user_id, message)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
