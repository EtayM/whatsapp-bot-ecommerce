from config import WELCOME_MESSAGE_MEDIA_ID
from services.nocodb import get_sub_categories, fetch_table_records
from services.wacloud_api import send_whatsapp_message_image_and_buttons
from services.aliexpress import get_products_info
from services.helpers import truncate

def handle_view_sub_category(user_id, subcategory_id, message_text):
    print(f"handling view sub category state for subcategory_id: {subcategory_id}")

    try:
        products_data = fetch_table_records("mrevopwotcaj87a")
        print("Products: %s", products_data)

        products = []
        for product_data in products_data['list']:
            products.append(int(product_data['product_id']))
        
        product_info = get_products_info(products)
        products_info_to_send = "\n".join(
            f"{i+1}. Name: {truncate(product['name'])}\nCategory: {product['category']}"
            for i, product in enumerate(product_info)
        )
        print(f"\n\n\n\n\n\n\n\n {products_info_to_send}")
        # print(products)
        # print(products_info)
        # print(product_info)
        # print(', '.join(products))

        buttons = [
            ("VIEW_CATEGORIES", "👀 המומלצים"),
            ("FIND_BEST_DEAL", "🤝 מצא דיל הכי משתלם")
        ]
        send_whatsapp_message_image_and_buttons(
            user_id,
            products_info_to_send,
            WELCOME_MESSAGE_MEDIA_ID,
            buttons=buttons
        )

        return
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