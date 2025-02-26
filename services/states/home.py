from config import WELCOME_MESSAGE_MEDIA_ID
from services.state import State
from services.nocodb import update_user_state, get_categories
from services.wacloud_api import send_whatsapp_message_image_and_buttons

def handle_home(user_id, message):
    print("handling home")
    if message.lower() == 'view_categories':
        handle_view_categories(user_id)
    elif message.lower() == 'get_best_deal':
        handle_get_best_deal(user_id)
    else:
        send_invalid_option_message(user_id)

def handle_view_categories(user_id):
    print("handling view_categories")
    try:
        categories = get_categories()
        buttons = [(cat['Id'], cat['Name']) for cat in categories]
        print(buttons)
        buttons.append(("BACK", "חזרה"))
        buttonsTEMP = [
            ("VIEW_CATEGORIES", "👀 המומלצים"),
            ("FIND_BEST_DEAL", "🤝 מצא דיל הכי משתלם")
        ]
        
        print(buttons)
        print(buttonsTEMP)
        
        send_whatsapp_message_image_and_buttons(
            user_id,
            "Select Category",
            WELCOME_MESSAGE_MEDIA_ID,
            buttons=buttons
        )
        update_user_state(user_id, State.VIEW_CATEGORIES)
        
    except Exception as e:
        from services.helpers import handle_api_error
        from config import WELCOME_MESSAGE_MEDIA_ID
        handle_api_error(e, "handle_view_categories", "get_categories", WELCOME_MESSAGE_MEDIA_ID)
        send_error_message(user_id)
        raise

def handle_get_best_deal(user_id):
    print("handling get_best_deal")
    message = "Please send us the AliExpress product link you want to find the best deal for!"
    send_whatsapp_message_image_and_buttons(
        user_id,
        message,
        WELCOME_MESSAGE_MEDIA_ID,
        buttons=[]
    )
    update_user_state(user_id, State.FIND_BEST_DEAL_AWAITING_LINK)

def send_invalid_option_message(user_id):
    message = "Invalid option selected. Please choose one of the available buttons."
    buttons = [
        ("VIEW_CATEGORIES", "👀 המומלצים"),
        ("FIND_BEST_DEAL", "🤝 מצא דיל הכי משתלם")
    ]
    send_whatsapp_message_image_and_buttons(
        user_id,
        message,
        WELCOME_MESSAGE_MEDIA_ID,
        buttons=buttons
    )

def send_error_message(user_id):
    message = "⚠️ An error occurred. Please try again later."
    send_whatsapp_message_image_and_buttons(
        user_id,
        message,
        WELCOME_MESSAGE_MEDIA_ID,
        buttons=[]
    )