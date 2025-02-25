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
from services.state import State
import services.states as state_handlers
import logging

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

@app.task(name='process_message_task')
def process_message_task(sender_id, message_text, user_state, message_id):
    """Process WhatsApp message with deduplication"""
    try:
        # Check if we've already processed this message
        if redis_client.get(f"msg:{message_id}"):
            logger.warning(f"Duplicate message detected: {message_id}")
            return

        # Store message ID with 24h expiration (WhatsApp's retry window)
        redis_client.setex(f"msg:{message_id}", 86400, "1")

        # Get handler function
        handler_name = f"handle_{user_state.lower()}"
        handler = getattr(state_handlers, handler_name, None)

        if not handler:
            logger.error(f"No handler found for state: {user_state}")
            return

        # Execute state handler
        handler(sender_id, message_text)

    except Exception as e:
        logger.error(f"Error processing message {message_id}: {str(e)}")
        raise