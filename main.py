"""Entry point to run the MCP server using stdio transport."""

import warnings
# Suppress noisy deprecation warnings from libraries before they are imported
warnings.filterwarnings("ignore", category=DeprecationWarning)

import logging
from dotenv import load_dotenv

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
async def discovery_endpoint(request):
    """Expose MCP discovery metadata."""
    auth_servers = os.getenv("MCP_AUTHORIZATION_SERVERS", "").split(",")
    resource = os.getenv("MCP_RESOURCE_URL", "http://localhost:3123/mcp")
    scopes = os.getenv("MCP_SCOPES_SUPPORTED", "").split(",")
    
    metadata = {
        "authorization_servers": [s.strip() for s in auth_servers if s.strip()],
        "bearer_methods_supported": ["header"],
        "resource": resource,
        "scopes_supported": [s.strip() for s in scopes if s.strip()]
    }
    return JSONResponse(metadata)

# Create ASGI application
app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    # Run the server on 0.0.0.0:8000
    # The discovery URL will be accessible at http://localhost:8000/sse (or similar depending on client)
    # and metadata at /.well-known/mcp if applicable in future versions or with Auth.
    uvicorn.run(app, host="0.0.0.0", port=3123)
