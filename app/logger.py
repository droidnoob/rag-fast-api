import logging

from app.resources import app_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(app_settings.app_name)
