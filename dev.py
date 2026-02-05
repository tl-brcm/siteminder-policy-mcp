"""Development ASGI application for running FastMCP over Streamable HTTP."""

import logging
from sm_mcp.tools.tooling import mcp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp.log", mode="w"),
        logging.StreamHandler()
    ]
)

logging.debug("dev.py logging initialized")

# Create the ASGI app using FastMCP's built-in HTTP support
app = mcp.http_app(transport="streamable-http")

