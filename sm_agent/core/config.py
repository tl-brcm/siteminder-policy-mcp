"""Configuration values loaded from environment variables."""

import os
import logging
import hvac
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SITE_MINDER_BASE_URL = os.getenv("SITE_MINDER_BASE_URL")
SITE_MINDER_USERNAME = os.getenv("SITE_MINDER_USERNAME")

_siteminder_password_cached = None

def get_siteminder_password():
    global _siteminder_password_cached
    if _siteminder_password_cached is not None:
        return _siteminder_password_cached

    VAULT_ADDR = os.getenv("VAULT_ADDR")
    VAULT_TOKEN = os.getenv("VAULT_TOKEN")
    SITE_MINDER_PASSWORD_VAULT_PATH = os.getenv("SITE_MINDER_PASSWORD_VAULT_PATH")

    password = None

    if VAULT_ADDR and VAULT_TOKEN and SITE_MINDER_PASSWORD_VAULT_PATH:
        try:
            client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
            if client.is_authenticated():
                try:
                    read_response = client.secrets.kv.v2.read_secret_version(
                        path=SITE_MINDER_PASSWORD_VAULT_PATH.replace("secret/", ""),
                        mount_point="secret"
                    )
                    if read_response and 'data' in read_response and 'data' in read_response['data']:
                        password = read_response['data']['data'].get('password')
                        if password:
                            logger.info("Successfully retrieved SiteMinder password from Vault.")
                        else:
                            logger.warning(f"Password key not found at Vault path: {SITE_MINDER_PASSWORD_VAULT_PATH}")
                    else:
                        logger.warning(f"No data found at Vault path: {SITE_MINDER_PASSWORD_VAULT_PATH}")
                except Exception as e:
                    logger.error(f"Error retrieving SiteMinder password from Vault: {e}")
            else:
                logger.error("Failed to authenticate with Vault.")
        except Exception as e:
            logger.error(f"Error retrieving SiteMinder password from Vault: {e}")
    
    if password is None:
        password = os.getenv("SITE_MINDER_PASSWORD")
        if password:
            logger.info("Successfully retrieved SiteMinder password from environment variable.")
        else:
            logger.warning("SiteMinder password not found in Vault or environment variables. API calls requiring password will fail.")

    _siteminder_password_cached = password
    return password

VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"

