import warnings
import logging
from dotenv import load_dotenv
import os
from starlette.responses import JSONResponse

# Suppress noisy deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

from sm_mcp.tools.tooling import mcp
from sm_mcp.core.config import LOG_LEVEL

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp.log", mode="w", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.debug(f"Starting MCP Server (HTTP mode) with Log Level: {LOG_LEVEL}")

@mcp.custom_route("/.well-known/mcp", methods=["GET"])
@mcp.custom_route("/.well-known/oauth-protected-resource/mcp", methods=["GET"])
async def discovery_endpoint(request):
    """
    Expose MCP discovery metadata. 
    Values are driven strictly by environment variables for maximum configurability.
    """
    logging.debug(f"Discovery metadata requested via {request.url.path}")
    auth_servers = [s.strip() for s in os.getenv("MCP_AUTHORIZATION_SERVERS", "").split(",") if s.strip()]
    resource = os.getenv("MCP_RESOURCE_URL", "https://mcp.vm.demo:8443/sm-policy/mcp")
    
    # Handle both space and comma separated scopes
    raw_scopes = os.getenv("MCP_SCOPES_SUPPORTED", "openid profile email siteminder:access")
    scopes = [s.strip() for s in raw_scopes.replace(",", " ").split() if s.strip()]
    
    app_name = os.getenv("MCP_APP_NAME", "siteminder-policy-assistant")
    
    metadata = {
        "name": app_name,
        "resource": resource,
        "resource_name": app_name,
        "bearer_methods_supported": ["header"],
        "authorization_servers": auth_servers,
        "scopes_supported": scopes
    }
    return JSONResponse(metadata)

# Create ASGI application
app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3123)
