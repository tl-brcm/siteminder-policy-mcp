# dev.py
from starlette.responses import Response
import logging

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
mcp_server: Server = mcp._mcp_server  # private access is ok here
sse = SseServerTransport("/messages/")

async def handle_sse(request: Request):
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
