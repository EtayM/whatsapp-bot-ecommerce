from config import WELCOME_MESSAGE_MEDIA_ID
from services.state import State
from services.nocodb import update_user_state
from services.wacloud_api import send_whatsapp_message_image_and_buttons

def handle_unknown(user_id, message):
    print("handling unknown")
    # Send welcome message with image and buttons
    welcome_message = "Welcome to AliExpress Affiliate Bot! 🛍️"
    buttons = [
        ("VIEW_CATEGORIES", "👀 המומלצים"),
        ("FIND_BEST_DEAL", "🤝 מצא דיל הכי משתלם")
    ]

    send_whatsapp_message_image_and_buttons(
        user_id,
        welcome_message,
        WELCOME_MESSAGE_MEDIA_ID,
        buttons
    )
    
    update_user_state(user_id, State.HOME)