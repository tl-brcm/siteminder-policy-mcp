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

print("[DEBUG] Loaded config:")
print("SITE_MINDER_BASE_URL =", SITE_MINDER_BASE_URL)
print("SITE_MINDER_USERNAME =", SITE_MINDER_USERNAME)
print("VERIFY_SSL =", VERIFY_SSL)

logger.debug(f"BASE_URL = {SITE_MINDER_BASE_URL}")
logger.debug(f"USERNAME = {SITE_MINDER_USERNAME}")
logger.debug(f"PASSWORD = {bool(SITE_MINDER_PASSWORD)}")
logger.debug(f"VERIFY_SSL = {VERIFY_SSL}") 