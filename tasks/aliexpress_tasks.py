# tasks/aliexpress_tasks.py
from tasks.celery_app import celery_app
from services.aliexpress import get_product_info

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def fetch_aliexpress_product_info(self, product_link):
    try:
        product_info = get_product_info(product_link)
        return product_info
    except Exception as e:
        # Log and retry the task
        self.retry(exc=e)