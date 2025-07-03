"""Entry point to run the MCP server over SSE."""

import logging
import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route, Mount
from mcp.server.sse import SseServerTransport
from sm_agent.tools.tooling import mcp
from mcp.server import Server

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp.log", mode="w"),
        logging.StreamHandler()
    ]
)

mcp_server: Server = mcp._mcp_server  # type: ignore[attr-defined]

sse = SseServerTransport("/messages/")

async def handle_sse(request: Request) -> Response:
    """Handle the ``/sse`` endpoint to run the MCP server over SSE."""

    async with sse.connect_sse(request.scope, request.receive, request._send) as (reader, writer):
        await mcp_server.run(reader, writer, mcp_server.create_initialization_options())
            
    return Response(status_code=204)

async def health_check(request: Request) -> Response:
    """Simple health check endpoint."""
    return JSONResponse({"status": "ok"})

app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
        Route("/health", endpoint=health_check),
    ],
)

logging.info("🚀 Starting MCP Server (SSE mode)")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3123)