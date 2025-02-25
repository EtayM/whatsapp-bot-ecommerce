import os

META_WHATSAPP_TOKEN = os.environ.get("META_WHATSAPP_TOKEN")
META_VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
WELCOME_MESSAGE_MEDIA_ID = os.environ.get("WELCOME_MESSAGE_MEDIA_ID")

# Celery config (using Redis as the broker)
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")

#AliExpress API
ALIEXPRESS_API_APP_KEY = os.environ.get("ALIEXPRESS_API_APP_KEY")
ALIEXPRESS_API_APP_SECRET= os.environ.get("ALIEXPRESS_API_APP_SECRET")
ALIEXPRESS_API_URL = os.environ.get("ALIEXPRESS_API_URL")

#Database
NOCODB_API_BASE_URL = os.environ.get("NOCODB_API_BASE_URL")
NOCODB_API_KEY = os.environ.get("NOCODB_API_KEY")