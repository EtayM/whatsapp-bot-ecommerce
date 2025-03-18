import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# Import everything else after loading env vars
from celery import Celery
import redis
from config import CELERY_BROKER_URL
#from services.state import State # No longer needed
import logging
#import services.states as state_handlers # No longer needed
from services.state import StateManager
import importlib

logger = logging.getLogger(__name__)

app = Celery('tasks')
app.conf.update(
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_BROKER_URL,
    broker_connection_retry_on_startup=True,
    worker_pool_restarts=True,
    worker_pool='solo'  # Use solo pool for Windows compatibility
)

# Configure Redis connection for idempotency
redis_client = redis.from_url(CELERY_BROKER_URL)

# Initialize StateManager
state_manager = StateManager()

@app.task(name='process_message_task')
def process_message_task(sender_id, message_text, state_name, message_id):
    """Process WhatsApp message with deduplication"""
    logger.debug(f"process_message_task called with sender_id: {sender_id}, message_text: {message_text}, state_name: {state_name}, message_id: {message_id}") # Add logging
    try:
        # Check if we've already processed this message
        if redis_client.get(f"msg:{message_id}"):
            logger.warning(f"Duplicate message detected: {message_id}")
            return

        # Store message ID with 24h expiration (WhatsApp's retry window)
        redis_client.setex(f"msg:{message_id}", 86400, "1")

        # Reload states to ensure they are up-to-date
        state_manager.load_states()

        # Get state object from StateManager
        state = state_manager.get_state(state_name)
        if not state:
            logger.error(f"State '{state_name}' not found.")
            return

        # Dynamically import and call the state handler function
        handler_module = importlib.import_module(state['handler_module'])
        handler_function = getattr(handler_module, state['handler_function'])

        # Extract parameter value if needed
        parameter_name = state.get('parameter_name')
        parameter_value = None
        if parameter_name == "subcategory_id":
            # Retrieve from database
            from services.nocodb import get_user_state
            user_state = get_user_state(sender_id)
            parameter_value = user_state['subcategory_id']

        # Call the handler function with or without the parameter
        if parameter_value:
            handler_function(sender_id, parameter_value, message_text)
        else:
            handler_function(sender_id, message_text)

    except Exception as e:
        logger.error(f"Error processing message {message_id}: {str(e)}")
        raise