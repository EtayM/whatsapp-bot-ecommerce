from config import WELCOME_MESSAGE_MEDIA_ID
from services.nocodb import get_sub_categories, fetch_table_records
from services.wacloud_api import send_whatsapp_message_image_and_buttons
from services.aliexpress import get_products_info
from services.helpers import truncate, get_localized_string, get_user_lang

def handle_view_sub_category(user_id, subcategory_id, message_text):
    print(f"handling view sub category state for subcategory_id: {subcategory_id}")

    lang=get_user_lang(user_id)
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

        buttons = [
            ("VIEW_CATEGORIES", get_localized_string(lang, 'button.recommended')),
            ("FIND_BEST_DEAL", get_localized_string(lang, 'button.find_best_deal'))
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
    # TODO
    pass