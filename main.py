"""Entry point to run the MCP server over standard I/O."""

import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

from mcp.server.stdio import stdio_server
from sm_agent.tools.tooling import mcp
from mcp.server import Server

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp.log", mode="w"),
        logging.StreamHandler()
    ]
)

async def main() -> None:
    """Run the MCP server over standard I/O."""
    logging.info("🚀 Starting MCP Server (stdio mode)")
    mcp_server: Server = mcp._mcp_server  # type: ignore[attr-defined]
    async with stdio_server() as (reader, writer):
        await mcp_server.run(reader, writer, mcp_server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
