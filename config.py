import os
from dotenv import load_dotenv
import logging

load_dotenv()  # should load from .env in current dir
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SITE_MINDER_BASE_URL = os.getenv("SITE_MINDER_BASE_URL")
SITE_MINDER_USERNAME = os.getenv("SITE_MINDER_USERNAME")
SITE_MINDER_PASSWORD = os.getenv("SITE_MINDER_PASSWORD")
VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"

