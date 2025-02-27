from config import WELCOME_MESSAGE_MEDIA_ID
from services.helpers import get_localized_string, get_user_lang
from services.nocodb import update_user_state, get_categories
from services.wacloud_api import send_whatsapp_message_image_and_buttons

def handle_home(user_id, message_text):
    print("handling home state")

    lang=get_user_lang(user_id)

    if message_text.lower() == 'view_categories':
        handle_home_view_categories(user_id, lang)
    elif message_text.lower() == 'get_best_deal':
        handle_home_get_best_deal(user_id, lang)
    else:
        send_invalid_option_message(user_id, lang)

def handle_home_view_categories(user_id, lang):
    print("handling home_view_categories")
    try:
        categories = get_categories(lang)
        buttons = [("CAT_"+str(cat['Id']), cat['Name']) for cat in categories]
        buttons.append(("BACK", get_localized_string(lang, 'button.back')))
        
        send_whatsapp_message_image_and_buttons(
            user_id,
            get_localized_string(lang, 'view_categories.select_category'),
            WELCOME_MESSAGE_MEDIA_ID,
            buttons=buttons
        )
        update_user_state(user_id, "VIEW_CATEGORIES")
        
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "handle_home_view_categories", "get_categories")
        send_error_message(user_id)
        raise

def handle_home_get_best_deal(user_id, lang):
    print("handling home_get_best_deal")

    message = get_localized_string(lang, 'find_best_deal.instructions')
    send_whatsapp_message_image_and_buttons(
        user_id,
        message,
        WELCOME_MESSAGE_MEDIA_ID,
        buttons=[]
    )
    update_user_state(user_id, "FIND_BEST_DEAL_AWAITING_LINK")

def send_invalid_option_message(user_id, lang):
    lang=get_user_lang(user_id)

    message = get_localized_string(lang, 'view_categories.invalid_choice')
    buttons = [
        ("VIEW_CATEGORIES", get_localized_string(lang, 'button.recommended')),
        ("FIND_BEST_DEAL", get_localized_string(lang, 'button.find_best_deal'))
    ]
    send_whatsapp_message_image_and_buttons(
        user_id,
        message,
        WELCOME_MESSAGE_MEDIA_ID,
        buttons=buttons
    )

def send_error_message(user_id):
    lang=get_user_lang(user_id)
    message = get_localized_string(lang, 'unknown_error')
    buttons = [
        ("VIEW_CATEGORIES", get_localized_string(lang, 'button.recommended')),
        ("FIND_BEST_DEAL", get_localized_string(lang, 'button.find_best_deal'))
    ]
    
    send_whatsapp_message_image_and_buttons(
        user_id,
        message,
        WELCOME_MESSAGE_MEDIA_ID,
        buttons
    )