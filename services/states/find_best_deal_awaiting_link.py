from services.state import State
from services.nocodb import update_user_state
from services.wacloud_api import send_whatsapp_message_image_and_buttons
from services.aliexpress import get_products_info, extract_product_id_from_link
# from services.helpers import extract_product_id

def handle_find_best_deal_awaiting_link(user_id, message):
    print("handling find best deal")
    # Handle back button
    if message.lower() == 'back':
        update_user_state(user_id, State.HOME)
        send_whatsapp_message_image_and_buttons(
            user_id=user_id,
            image_url="https://example.com/home-image.jpg",  # TODO: Replace with actual image
            message="Returning to main menu",
            buttons=[]
        )
        return

    # Validate product link
    # if not validate_product_link(message):
    #     send_invalid_link_message(user_id)
    #     return

    try:
        # Extract and validate product ID
        product_id = extract_product_id_from_link(message)
        if not product_id:
            send_invalid_link_message(user_id)
            return

        # Get product details
        products = get_products_info([product_id])
        if not products:
            send_no_results_message(user_id)
            return

        # Send product details to user
        send_product_details(user_id, products[0])
        update_user_state(user_id, State.HOME)

    except Exception as e:
        from services.helpers import handle_api_error
        handle_api_error(e, "handle_find_best_deal_awaiting_link", "get_products_info", message)
        send_error_message(user_id)
        raise

def send_invalid_link_message(user_id):
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url="https://example.com/error-image.jpg",  # TODO: Replace with actual image
        message="❌ Invalid AliExpress link. Please send a valid product URL.",
        buttons=[]
    )

def send_no_results_message(user_id):
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url="https://example.com/error-image.jpg",  # TODO: Replace with actual image
        message="⚠️ No matching products found. Please try a different link.",
        buttons=[]
    )

def send_product_details(user_id, product):
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url=product.get('image', 'https://example.com/placeholder.jpg'),
        message=f"🏷️ {product['name']}\n💵 Price: ${product['price']}\n⭐ Rating: {product['rating']}",
        buttons=[
            {"type": "reply", "reply": {"id": "buy_now", "title": "🛒 Buy Now"}},
            {"type": "reply", "reply": {"id": "back", "title": "🔙 Back"}}
        ]
    )

def send_error_message(user_id):
    send_whatsapp_message_image_and_buttons(
        user_id=user_id,
        image_url="https://example.com/error-image.jpg",  # TODO: Replace with actual image
        message="⚠️ Error processing your request. Please try again.",
        buttons=[]
    )