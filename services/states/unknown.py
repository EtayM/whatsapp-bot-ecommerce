from services.helpers import get_localized_string, get_user_lang
from config import WELCOME_MESSAGE_MEDIA_ID
from services.nocodb import update_user_state
from services.wacloud_api import send_whatsapp_message_image_and_buttons

def handle_unknown(user_id, message_text):
    print("handling unknown")

    lang=get_user_lang(user_id)
    # Send welcome message with image and buttons
    welcome_message = get_localized_string(lang, 'welcome_message')
    print(welcome_message)
    buttons = [
        ("VIEW_CATEGORIES", get_localized_string(lang, 'button.recommended')),
        ("FIND_BEST_DEAL", get_localized_string(lang, 'button.find_best_deal'))
    ]

    send_whatsapp_message_image_and_buttons(
        user_id,
        welcome_message,
        WELCOME_MESSAGE_MEDIA_ID,
        buttons
    )
    
    update_user_state(user_id, "HOME")