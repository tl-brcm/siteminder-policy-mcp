import warnings
import sys
import logging
from dotenv import load_dotenv

# Suppress noisy deprecation warnings from libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

from sm_mcp.tools.tooling import mcp

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp.log", mode="w", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.debug("Starting MCP Server (HTTP mode)")

import os
from starlette.responses import JSONResponse

@mcp.custom_route("/.well-known/mcp", methods=["GET"])
@mcp.custom_route("/.well-known/oauth-protected-resource/mcp", methods=["GET"])
async def discovery_endpoint(request):
    """Expose MCP discovery metadata."""
    auth_servers = os.getenv("MCP_AUTHORIZATION_SERVERS", "").split(",")
    resource = os.getenv("MCP_RESOURCE_URL", "http://localhost:3123/mcp")
    scopes = os.getenv("MCP_SCOPES_SUPPORTED", "openid profile email siteminder:access").split()
    app_name = os.getenv("MCP_APP_NAME", "siteminder-policy-assistant")
    
    metadata = {
        "authorization_servers": [s.strip() for s in auth_servers if s.strip()],
        "bearer_methods_supported": ["header"],
        "resource": resource,
        "name": app_name,
        "resource_name": app_name,  # Redundant for compatibility
        "scopes_supported": [s.strip() for s in scopes if s.strip()]
    }
    return JSONResponse(metadata)

# Create ASGI application
app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    # Run the server on 0.0.0.0:3123
    uvicorn.run(app, host="0.0.0.0", port=3123)