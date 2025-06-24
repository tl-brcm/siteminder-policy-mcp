"""Entry point to run the MCP server using stdio transport."""

import logging
from dotenv import load_dotenv

load_dotenv()

from tooling import mcp

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp.log", mode="w"),
        logging.StreamHandler()
    ]
)

logging.debug("✅ Starting MCP Server (stdio mode)")

if __name__ == "__main__":
    mcp.run(transport="stdio")
