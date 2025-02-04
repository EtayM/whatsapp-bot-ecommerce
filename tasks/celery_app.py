# tasks/celery_app.py
from celery import Celery
from config import CELERY_BROKER_URL

celery_app = Celery('tasks', broker=CELERY_BROKER_URL)
# Optionally configure a result backend:
celery_app.conf.result_backend = CELERY_BROKER_URL