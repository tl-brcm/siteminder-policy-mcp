from mcp.server.fastmcp import FastMCP
from siteminder_api import get_token, fetch_objects, search_objects, get_object_details_from_href, get_object_by_id, build_object_id_url,show_detail_cache, clear_detail_cache
from sm_registry import OBJECT_CLASSES
from typing import Optional
from sm_utils import extract_core_fields 
import urllib.parse
import logging
import json

mcp = FastMCP("siteminder-policy-assistant")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# --- Helpers ---

def ensure_dict(detail):
    if isinstance(detail, str):
        try:
            detail = json.loads(detail)
        except Exception:
            raise ValueError("Argument must be a dict or a JSON string representing a dict")
    return detail

async def ensure_token() -> Optional[str]:
    token = await get_token()
    if not token:
        logger.error(" Failed to get session token.")
        return None
    return token

def normalize_name(obj: dict) -> dict:
    if "path" in obj:
        try:
            name = urllib.parse.unquote(obj["path"]).split("/")[-1].replace("+", " ")
            obj["name"] = name
        except Exception:
            obj["name"] = "(unknown)"
    return obj

def format_json_detail(detail: dict) -> str:
    return "```json\n" + json.dumps(detail, indent=2) + "\n```"

async def fetch_and_cache_details(hrefs: list, token: str, output: list):
    for href in hrefs[:3]:  # Only top 3
        try:
            detail = await get_object_details_from_href(href, token)
            if detail:
                obj_id = detail.get("data", {}).get("id")
                output.append("\n Detail:")
                output.append(format_json_detail(detail))
        except Exception as e:
            logger.warning(f"Failed to fetch detail for href: {href}, error: {e}")

# --- Tool Registration ---

def register_object_tools(obj_type: str):
    config = OBJECT_CLASSES[obj_type]
    formatter = config["formatter"]
    help_text = config["help"]

    list_doc = f"Show a summary of all SiteMinder {obj_type} objects."

    @mcp.tool(name=f"list_{obj_type.lower()}_summary", description=list_doc)
    async def list_tool():
        token = await ensure_token()
        if not token:
            return " Failed to get session token."
        try:
            results = await fetch_objects(obj_type, token)
            if not results:
                return f"No {obj_type} objects found."
            normalized = [normalize_name(dict(r)) for r in results]
            return "\n\n".join(formatter(o) for o in normalized)
        except Exception as e:
            logger.exception("List operation failed")
            return f" Error fetching {obj_type} objects: {e}"

    @mcp.tool(name=f"search_{obj_type.lower()}", description=help_text)
    async def search_tool(filter_expression: str):
        token = await ensure_token()
        if not token:
            return " Failed to get session token."
        try:
            raw_results = await search_objects(obj_type, token, filter_expression) or []
            if not raw_results:
                return f"No {obj_type} objects matched this filter."
            results = [normalize_name(dict(r)) for r in raw_results]

            output = [formatter(r) for r in results]
            hrefs = [r.get("href") for r in results if r.get("href")]
            await fetch_and_cache_details(hrefs, token, output)
            logger.debug(f"output returned: {output}")
            return "\n\n".join(output)
        except Exception as e:
            logger.exception("Search operation failed")
            return f" Error fetching {obj_type} objects: {e}"

@mcp.tool(name="get_object_by_id", description="Fetch a SiteMinder object by its ID and return full detail.")
async def get_object_by_id_tool(id: str) -> str:
    token = await ensure_token()
    if not token:
        return " Failed to get session token."
    try:
        detail = await get_object_by_id(id, token)
        if detail:
            return format_json_detail(detail)
        else:
            return f" No object found with ID: {id}"
    except Exception as e:
        logger.exception("Error retrieving object by ID")
        return f" Error retrieving object with ID {id}: {e}"

# Register tools for all object types
for obj_type in OBJECT_CLASSES:
    register_object_tools(obj_type)

def register_object_link_tool(
    mcp,
    name: str,
    suffix: str = "",
    description: str = ""
):
    """
    Registers a tool that fetches a SiteMinder object link endpoint based on object ID.
    The tool accepts object ID or ObjectIDURL as input.
    """
    @mcp.tool(
        name=name,
        description=(
            f"{description}\n\n"
            "Input: the object ID (e.g., 'CA.SM::Domain@03-...') **or** the full object detail URL.\n"
            "Output: JSON response from the requested endpoint.\n"
            "This tool will construct the proper URL automatically."
        )
    )
    async def tool(id_or_url: str):
        token = await ensure_token()
        if not token:
            return {"error": "Failed to get session token."}

        # Build base object URL if input is just the ID
        if id_or_url.startswith("http"):
            base_url = id_or_url
        else:
            obj_id = id_or_url
            base_url = build_object_id_url(obj_id)

        # Compose the correct endpoint for this link type
        if suffix.startswith("?"):
            url = f"{base_url}{suffix}"
        elif suffix:
            url = f"{base_url}/{suffix}"
        else:
            url = base_url

        try:
            result = await get_object_details_from_href(url, token)
            # Normalize name if possible
            if isinstance(result, dict):
                normalize_name(result)
                if "data" in result and isinstance(result["data"], dict):
                    normalize_name(result["data"])
                # If the endpoint returns a list (e.g., children), normalize each item
                if "data" in result and isinstance(result["data"], list):
                    for obj in result["data"]:
                        normalize_name(obj)
            return result
        except Exception as e:
            return {"error": f"Failed to fetch detail for url: {url}, error: {e}"}

# Call this at startup to register all link tools
register_object_link_tool(
    mcp,
    name="get_children_of_object",
    suffix="children",
    description="Fetches all child objects for the given SiteMinder object ID."
)
register_object_link_tool(
    mcp,
    name="get_expanded_of_object",
    suffix="?op=expanded",
    description="Fetches expanded details for the given SiteMinder object ID."
)
register_object_link_tool(
    mcp,
    name="get_usedby_of_object",
    suffix="usedby",
    description="Fetches the list of objects that use or reference this SiteMinder object ID."
)
register_object_link_tool(
    mcp,
    name="get_classinfo_of_object",
    suffix="classinfo",
    description="Fetches the schema/class info for the given SiteMinder object ID."
)
register_object_link_tool(
    mcp,
    name="get_editinfo_of_object",
    suffix="?op=editinfo",
    description="Fetches the edit information for the given SiteMinder object ID."
)

@mcp.tool(name="show_detail_cache", description="Show the keys of the SiteMinder object detail cache.")
async def show_detail_cache_tool() -> str:
    return "DETAIL_CACHE keys:\n" + json.dumps(show_detail_cache(), indent=2)

@mcp.tool(name="clear_detail_cache", description="Clear the SiteMinder object detail cache.")
async def clear_detail_cache_tool() -> str:
    clear_detail_cache()
    return "DETAIL_CACHE cleared."