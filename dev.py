"""Development ASGI application for running FastMCP over Server-Sent Events."""

import logging
from starlette.responses import Response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp.log", mode="w"),  # Log file
        logging.StreamHandler()  # Console
    ]
)

logging.debug("dev.py logging initialized")

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount
from tooling import mcp
from mcp.server import Server

# Create the actual ASGI app object
# Access the underlying ``mcp.server.Server`` instance created by ``tooling``.
mcp_server: Server = mcp._mcp_server  # type: ignore[attr-defined]

# Transport used for streaming messages back to the client.
sse = SseServerTransport("/messages/")

async def handle_sse(request: Request) -> Response:
    """Handle the ``/sse`` endpoint to run the MCP server over SSE."""

    async with sse.connect_sse(request.scope, request.receive, request._send) as (reader, writer):
        await mcp_server.run(reader, writer, mcp_server.create_initialization_options())
            
    return Response(status_code=204)

app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)
