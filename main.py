import warnings
import logging
from pathlib import Path
import os
from starlette.responses import JSONResponse

# Suppress noisy deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from sm_mcp.core.config import LOG_LEVEL, MCP_AUTH_DISABLED

# Configure logging
log_level = getattr(logging, LOG_LEVEL, logging.INFO)
log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

# File handler
file_handler = logging.FileHandler("mcp.log", mode="a", encoding="utf-8")
file_handler.setFormatter(log_format)

# Stream handler (Console)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)

# Root logger: set to INFO by default to silence noisy libs (httpcore, etc.)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)

# Application loggers: set to the user-defined LOG_LEVEL
for logger_name in ["sm_mcp", "main", "fastmcp"]:
    l = logging.getLogger(logger_name)
    l.setLevel(log_level)

from sm_mcp.tools.tooling import mcp

logging.info("--- MCP Server Starting ---")
logging.info(f"CWD: {os.getcwd()}")
logging.info(f"SITE_MINDER_BASE_URL: {os.getenv('SITE_MINDER_BASE_URL')}")
logging.info(f"MCP_AUTH_DISABLED: {MCP_AUTH_DISABLED}")

if not MCP_AUTH_DISABLED:
    @mcp.custom_route("/.well-known/mcp", methods=["GET"])
    @mcp.custom_route("/.well-known/oauth-protected-resource/mcp", methods=["GET"])
    @mcp.custom_route("/.well-known/oauth-protected-resource/sm-policy/mcp", methods=["GET"])
    async def discovery_endpoint(request):
        """
        Expose MCP discovery metadata. 
        Points Cursor to THIS server for authentication (Proxy mode).
        """
        logging.debug(f"Discovery metadata requested via {request.url.path}")
        
        # In Proxy mode, THIS server is the authorization server for Cursor
        base_url = os.getenv("MCP_BASE_URL", "https://mcp.vm.demo:8443/sm-policy")
        resource = os.getenv("MCP_RESOURCE_URL", f"{base_url}/mcp")
        app_name = os.getenv("MCP_APP_NAME", "siteminder-policy-assistant")
        
        # Handle both space and comma separated scopes
        raw_scopes = os.getenv("MCP_SCOPES_SUPPORTED", "openid profile email siteminder:access")
        scopes = [s.strip() for s in raw_scopes.replace(",", " ").split() if s.strip()]
        
        metadata = {
            "name": app_name,
            "resource": resource,
            "resource_name": app_name,
            "bearer_methods_supported": ["header"],
            # Cursor needs to authenticate against the MCP Server's Proxy
            "authorization_servers": [base_url],
            "registration_endpoint": f"{base_url}/register",
            "scopes_supported": scopes
        }
        return JSONResponse(metadata)

    @mcp.custom_route("/.well-known/oauth-authorization-server", methods=["GET"])
    @mcp.custom_route("/.well-known/openid-configuration", methods=["GET"])
    async def openid_configuration(request):
        """
        Expose OpenID Connect discovery metadata by mirroring the OAuth metadata.
        This is required for clients (like Cursor) that expect OIDC discovery.
        """
        base_url = os.getenv("MCP_BASE_URL", "https://mcp.vm.demo:8443/sm-policy")
        
        # Construct metadata manually since we can't easily access the internal proxy's config
        # but we know what it should be based on our proxy setup.
        metadata = {
            "issuer": base_url,
            "authorization_endpoint": f"{base_url}/authorize",
            "token_endpoint": f"{base_url}/token",
            "registration_endpoint": f"{base_url}/register",
            "jwks_uri": f"{base_url}/.well-known/jwks.json", # FastMCP might not expose this easily, but let's see
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic", "none"], # Added none for public client
            "scopes_supported": [s.strip() for s in os.getenv("MCP_SCOPES_SUPPORTED", "").replace(",", " ").split() if s.strip()],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256", "HS256"],
            "code_challenge_methods_supported": ["S256"]
        }
        return JSONResponse(metadata)
else:
    logging.info("OIDC Discovery endpoints skipped as authentication is disabled.")


# Create ASGI application
app = mcp.http_app()

@app.middleware("http")
async def log_requests(request, call_next):
    logging.debug(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logging.debug(f"Response status: {response.status_code} for {request.method} {request.url.path}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3123)
