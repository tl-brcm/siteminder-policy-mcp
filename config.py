"""Configuration values loaded from environment variables."""

import os
import logging
from dotenv import load_dotenv

# Load values from a local ``.env`` file if present.
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Credentials and connection info for the SiteMinder REST endpoints.
SITE_MINDER_BASE_URL = os.getenv("SITE_MINDER_BASE_URL")
SITE_MINDER_USERNAME = os.getenv("SITE_MINDER_USERNAME")
SITE_MINDER_PASSWORD = os.getenv("SITE_MINDER_PASSWORD")

# When running in environments with self-signed certificates this can be set to
# ``false`` to disable SSL verification.
VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"

