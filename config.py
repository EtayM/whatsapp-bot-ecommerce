import os

# Replace these with your actual values or pull them from environment variables
META_WHATSAPP_TOKEN = os.environ.get("META_WHATSAPP_TOKEN")
META_VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

# For scheduling
SCHEDULER_TIMEZONE = os.environ.get("SCHEDULER_TIMEZONE")

# Celery config (using Redis as the broker)
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")

#AliExpress API
ALIEXPRESS_API_KEY = os.environ.get("ALIEXPRESS_API_KEY")
ALIEXPRESS_API_URL = os.environ.get("ALIEXPRESS_API_URL")