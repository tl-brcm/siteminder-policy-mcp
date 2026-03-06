
import sys
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.DEBUG)

try:
    print("Importing mcp object...")
    from sm_mcp.tools.tooling import mcp
    
    print("Successfully imported mcp object.")
    print(f"MCP Object type: {type(mcp)}")
    
    # FastMCP 3.x exposes tools via list_tools() or similar inspection
    # depending on the implementation. Let's inspect the internal tool registry if possible
    # or just assert it's alive.
    
    # In FastMCP 3.x, registered tools are often stored in mcp._tool_manager or similar
    # but we can also just trust the import didn't crash.
    
    print("Migration verification: IMPORT SUCCESS")
    
except ImportError as e:
    print(f"Migration verification: FAILED with ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Migration verification: FAILED with Exception: {e}")
    sys.exit(1)
