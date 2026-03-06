import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Resolve the absolute path to the .env file in the project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"

# Load environment variables
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    load_dotenv(override=True)

# SiteMinder Configuration
SITE_MINDER_BASE_URL = os.getenv("SITE_MINDER_BASE_URL")
SITE_MINDER_USERNAME = os.getenv("SITE_MINDER_USERNAME")
SITE_MINDER_PASSWORD = os.getenv("SITE_MINDER_PASSWORD")
VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"

# Logging & MCP Metadata
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
MCP_BASE_URL = os.getenv("MCP_BASE_URL", "https://mcp.vm.demo:8443/sm-policy")
MCP_AUTH_DISABLED = os.getenv("MCP_AUTH_DISABLED", "false").lower() == "true"

# IDSP OIDC Configuration
IDSP_OIDC_URL = os.getenv("IDSP_OIDC_URL")
IDSP_CLIENT_ID = os.getenv("IDSP_CLIENT_ID")
IDSP_SCOPES = os.getenv("IDSP_SCOPES", "openid profile email").split()
IDSP_AUDIENCE = os.getenv("IDSP_AUDIENCE")
JWT_SIGNING_KEY = os.getenv("JWT_SIGNING_KEY", "change-me-in-production")