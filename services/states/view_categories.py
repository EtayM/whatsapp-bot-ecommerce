from config import WELCOME_MESSAGE_MEDIA_ID
#from services.state import State # No longer needed
from services.nocodb import update_user_state, get_sub_categories
from services.wacloud_api import send_whatsapp_message_image_and_buttons
from services.helpers import get_user_lang, get_localized_string
from .view_sub_category import handle_view_sub_category
from .home import handle_home_view_categories

def handle_view_categories(user_id, message_text):
    print("handling view categories state")

    lang=get_user_lang(user_id)
    if message_text.lower() == 'back':
        return handle_back(user_id, lang)
        
    try:
        # Get sub-categories/products for selected category
        message_text = message_text.strip()
        if message_text.startswith("CAT_"):
            category_id = message_text[4:]  # Extract the ID after "CAT_"
            sub_categories = get_sub_categories(category_id, lang)

            buttons = [("SUB_CAT_"+str(sub_cat['Id']), sub_cat['Name']) for sub_cat in sub_categories]
            buttons.append(("BACK", get_localized_string(lang, 'button.back')))
            
            send_whatsapp_message_image_and_buttons(
                user_id,
                get_localized_string(lang, 'view_categories.select_sub_category'),
                WELCOME_MESSAGE_MEDIA_ID,
                buttons=buttons
            )
            #update_user_state(user_id, State.VIEW_CATEGORIES) # Keep in view categories state
            return # Keep in view categories state
        elif message_text.startswith("SUB_CAT_"):
            subcategory_id = message_text[8:]  # Extract the ID after "SUB_CAT_"
            handle_view_sub_category(user_id, subcategory_id, message_text)
            update_user_state(user_id, "VIEW_SUB_CATEGORY", subcategory_id)
            return
        else:
            send_invalid_option_message(user_id, lang)
            return #update_user_state(user_id, State.VIEW_CATEGORIES)
        
        
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "handle_view_categories", "get_sub_categories", message_text)
        send_error_message(user_id, lang)
        raise

def handle_back(user_id, lang):
    pass
    # send_whatsapp_message_image_and_buttons(
    #     user_id=user_id,
    #     image_url="https://example.com/back-image.jpg",
    #     message="Returning to main menu",
    #     buttons=[]
    # )

    # update_user_state(user_id, "HOME")

def send_invalid_option_message(user_id, lang):
    return handle_home_view_categories(user_id, lang)

def send_error_message(user_id):
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url="https://example.com/error-image.jpg",
        message="⚠️ Error loading categories. Please try again.",
        buttons=[]
    )