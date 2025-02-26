from config import WELCOME_MESSAGE_MEDIA_ID
from services.nocodb import get_sub_categories
from services.wacloud_api import send_whatsapp_message_image_and_buttons
from services.aliexpress import get_products_info

def handle_view_sub_category(user_id, subcategory_id, message_text):
    print(f"handling view sub category state for subcategory_id: {subcategory_id}")

    try:
        # Get product IDs for the selected subcategory
        product_ids = get_sub_categories(subcategory_id)

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

        # Return to categories list (HOME) after displaying products
        #update_user_state(user_id, "HOME") # should go back to view categories
    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "handle_view_sub_category", "get_sub_categories", subcategory_id)
        send_error_message(user_id)
        raise

def send_error_message(user_id):
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url="https://example.com/error-image.jpg",
        message="⚠️ Error loading products. Please try again.",
        buttons=[]
    )