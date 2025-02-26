from config import WELCOME_MESSAGE_MEDIA_ID
#from services.state import State # No longer needed
from services.nocodb import update_user_state, get_sub_categories
from services.wacloud_api import send_whatsapp_message_image_and_buttons
# from services.helpers import extract_product_ids
from services.aliexpress import get_products_info

def handle_view_categories(user_id, message_text):
    print("handling view categories state")
    if message_text.lower() == 'back':
        return handle_back(user_id)
        
    try:
        # Get sub-categories/products for selected category
        message_text = message_text.strip()
        if message_text.startswith("CAT_"):
            category_id = message_text[4:]  # Extract the ID after "CAT_"
            sub_categories = get_sub_categories(category_id)

            buttons = [("SUB_CAT_"+str(sub_cat['Id']), sub_cat['Name']) for sub_cat in sub_categories]
            buttons.append(("BACK", "חזרה"))
            
            send_whatsapp_message_image_and_buttons(
                user_id,
                "Select Sub Category",
                WELCOME_MESSAGE_MEDIA_ID,
                buttons=buttons
            )
            #update_user_state(user_id, State.VIEW_CATEGORIES) # Keep in view categories state
            return # Keep in view categories state
        elif message_text.startswith("SUB_CAT_"):
            subcategory_id = message_text[8:]  # Extract the ID after "SUB_CAT_"
            #next_state_name = f"VIEW_SUBCATEGORY_{subcategory_id}"
            update_user_state(user_id, "VIEW_SUB_CATEGORY", subcategory_id)
            return
        else:
            send_invalid_option_message(user_id)
            return #update_user_state(user_id, State.VIEW_CATEGORIES)
        
        # Get product details from AliExpress
        #products = get_products_info(product_ids) # not needed here
        
        # Send product cards with images and details
        #for product in products: # not needed here
        #    send_whatsapp_message_image_and_buttons(
        #        user_id=user_id,
        #        image_url=product['image'],
        #        message=f"{product['name']}\nPrice: ${product['price']}",
        #        buttons=[]
        #    )
            
        # Return to categories list
        #update_user_state(user_id, "HOME") # not needed here
        
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "handle_view_categories", "get_sub_categories", message_text)
        send_error_message(user_id)
        raise

def handle_back(user_id):
    update_user_state(user_id, "HOME")
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url="https://example.com/back-image.jpg",
        message="Returning to main menu",
        buttons=[]
    )

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
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url="https://example.com/error-image.jpg",
        message="⚠️ Error loading categories. Please try again.",
        buttons=[]
    )