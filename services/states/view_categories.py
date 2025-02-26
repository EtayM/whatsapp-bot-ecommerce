from services.state import State
from services.nocodb import update_user_state, get_sub_categories
from services.wacloud_api import send_whatsapp_message_image_and_buttons
# from services.helpers import extract_product_ids
from services.aliexpress import get_products_info

def handle_view_categories(user_id, message):
    print("handling view categories")
    if message.lower() == 'back':
        return handle_back(user_id)
        
    try:
        # Get sub-categories/products for selected category
        category_id = message.strip()
        product_ids = get_sub_categories(category_id)
        
        # Get product details from AliExpress
        products = get_products_info(product_ids)
        
        # Send product cards with images and details
        for product in products:
            send_whatsapp_message_image_and_buttons(
                user_id=user_id,
                image_url=product['image'],
                message=f"{product['name']}\nPrice: ${product['price']}",
                buttons=[]
            )
            
        # Return to categories list
        update_user_state(user_id, State.HOME)
        
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "handle_view_categories", "get_sub_categories", message)
        send_error_message(user_id)
        raise

def handle_back(user_id):
    update_user_state(user_id, State.HOME)
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url="https://example.com/back-image.jpg",
        message="Returning to main menu",
        buttons=[]
    )

def send_error_message(user_id):
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url="https://example.com/error-image.jpg",
        message="⚠️ Error loading categories. Please try again.",
        buttons=[]
    )