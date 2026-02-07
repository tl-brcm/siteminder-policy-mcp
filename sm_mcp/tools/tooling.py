"""Tool registration for interacting with SiteMinder via FastMCP."""

import json
import logging
import urllib.parse
from typing import Optional

from fastmcp import FastMCP, Context
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier, JWTVerifier
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from sm_mcp.api.siteminder_api import (
    get_token,
    fetch_objects,
    search_objects,
    get_object_details_from_href,
    get_object_by_id,
    build_object_id_url,
    show_detail_cache,
    clear_detail_cache,
)
import os
from .sm_utils import default_formatter, extract_core_fields

# Load object classes from JSON
registry_path = os.path.join(os.path.dirname(__file__), 'sm_registry.json')
with open(registry_path, 'r') as f:
    OBJECT_CLASSES = json.load(f)

# Attach a default formatter and help text to each object type entry.
for name, obj in OBJECT_CLASSES.items():
    obj["formatter"] = default_formatter
    obj["help"] = (
        f"Search SiteMinder {name} objects using a filter expression.\n\n"
        f"Supported attributes:\n- " + "\n- ".join(obj["attributes"]) + "\n\n"
        "Examples:\n"
        "- Name contains 'login'\n"
        "- Desc != null\n"
        "- IsEnabled = true\n"
        "- Level > 500\n"
    )
    if "examples" in obj:
        obj["help"] += "\n" + "\n".join(obj["examples"])

    if name == "SmAgentConfig":
        obj["help"] += "\n\nExamples:\n- Name contains 'aco_test'\n- Desc contains 'test'"

# Configure authentication
# Priority: IDSP (OIDC) > IDSP (JWT) > Local (Static Token) > None
auth = None
idsp_oidc_url = os.getenv("IDSP_OIDC_URL")
idsp_jwks_uri = os.getenv("IDSP_JWKS_URI")
auth_token = os.getenv("MCP_AUTH_TOKEN")

if idsp_oidc_url:
    # Use OIDCProxy for full OAuth/OIDC support
    # This enables the MCP server to act as an OAuth Client to Broadcom IDSP
    config_url = f"{idsp_oidc_url}/.well-known/openid-configuration"
    # If the URL already ends with .well-known..., use it as is
    if idsp_oidc_url.endswith("openid-configuration"):
        config_url = idsp_oidc_url
        
    required_scopes = os.getenv("IDSP_SCOPES", "openid").split()
    auth = OIDCProxy(
        config_url=config_url,
        client_id=os.getenv("IDSP_CLIENT_ID"),
        client_secret=os.getenv("IDSP_CLIENT_SECRET"),
        base_url=os.getenv("MCP_BASE_URL", "http://localhost:3123"),
        required_scopes=required_scopes,
        audience=os.getenv("IDSP_AUDIENCE"),
    )
    logging.getLogger(__name__).info("Configured IDSP OIDC Authentication")

elif idsp_jwks_uri:
    auth = JWTVerifier(
        jwks_uri=idsp_jwks_uri,
        issuer=os.getenv("IDSP_ISSUER"),
        audience=os.getenv("IDSP_AUDIENCE")
    )
    logging.getLogger(__name__).info("Configured IDSP JWT Authentication")
elif auth_token:
    auth = StaticTokenVerifier(
        tokens={
            auth_token: {
                "client_id": "cursor-client",
                "scopes": ["all"]
            }
        }
    )
    logging.getLogger(__name__).info("Configured Static Token Authentication")

mcp = FastMCP(
    "siteminder-policy-assistant",
    auth=auth
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# --- Helpers ---

def ensure_dict(detail: str | dict) -> dict:
    """Return ``detail`` as a dictionary, parsing JSON strings when needed."""

    if isinstance(detail, str):
        try:
            detail = json.loads(detail)
        except Exception as exc:
            raise ValueError(
                "Argument must be a dict or a JSON string representing a dict"
            ) from exc
    return detail

async def ensure_token() -> Optional[str]:
    """Helper to fetch a token and log failures."""

    token = await get_token()
    if not token:
        logger.error("Failed to get session token.")
        return None
    return token

def normalize_name(obj: dict) -> dict:
    """Attempt to derive a human readable name from an object's path."""

    if "path" in obj:
        try:
            name = (
                urllib.parse.unquote(obj["path"]).split("/")[-1].replace("+", " ")
            )
            obj["name"] = name
        except Exception:
            obj["name"] = "(unknown)"
    return obj

def format_json_detail(detail: dict) -> str:
    """Return the detail dictionary formatted as a fenced JSON block."""

    # Recursively remove any dict entries where the value starts with #
    def remove_unset_values(obj):
        if isinstance(obj, dict):
            return {k: remove_unset_values(v) for k, v in obj.items() if not (isinstance(v, str) and v.startswith("#"))}
        elif isinstance(obj, list):
            return [remove_unset_values(elem) for elem in obj]
        else:
            return obj

    return "```json\n" + json.dumps(remove_unset_values(detail), indent=2) + "\n```"

async def fetch_and_cache_details(hrefs: list[str], token: str, output: list[str]) -> None:
    """Fetch details for the first few hrefs and append to ``output``."""

    for href in hrefs[:3]:  # Only top 3 to keep responses concise
        try:
            detail = await get_object_details_from_href(href, token)
            if detail:
                output.append("\n Detail:")
                output.append(format_json_detail(detail))
        except Exception as e:
            logger.warning(f"Failed to fetch detail for href: {href}, error: {e}")

# --- Tool Registration ---

def register_object_tools(obj_type: str) -> None:
    """Register list and search tools for a specific SiteMinder object type."""

    config = OBJECT_CLASSES[obj_type]
    formatter = config["formatter"]
    help_text = config["help"]

    if obj_type == "SmAgentConfig":
        help_text = help_text.replace("Agent Configuration Object", "Agent Configuration Object (ACO)")

    list_doc = f"Show a summary of all SiteMinder {obj_type} objects."

    async def list_tool() -> str:
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

    mcp.tool(
        name=f"list_{obj_type.lower()}_summary",
        description=list_doc
    )(list_tool)

    async def search_tool(filter_expression: str, ctx: Context) -> str:
        token = await ensure_token()
        if not token:
            return " Failed to get session token."
        try:
            ctx.info(f"Searching {obj_type} with filter: {filter_expression}")
            raw_results = await search_objects(obj_type, token, filter_expression) or []
            if not raw_results:
                return f"No {obj_type} objects matched this filter."
            
            ctx.info(f"Found {len(raw_results)} results. Fetching details...")
            results = [normalize_name(dict(r)) for r in raw_results]

            output = [formatter(r) for r in results]
            hrefs = [r.get("href") for r in results if r.get("href")]
            
            # Progress reporting could be granular here, but for now just logging
            await fetch_and_cache_details(hrefs, token, output)
            
            logger.debug(f"output returned: {output}")
            return "\n\n".join(output)
        except Exception as e:
            logger.exception("Search operation failed")
            return f" Error fetching {obj_type} objects: {e}"

    mcp.tool(
        name=f"search_{obj_type.lower()}",
        description=help_text
    )(search_tool)

@mcp.tool(name="get_object_by_id", description="Fetch a SiteMinder object by its ID and return full detail.")
async def get_object_by_id_tool(id: str) -> str:
    """Return the raw JSON for a SiteMinder object by id."""

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
    mcp: FastMCP,
    name: str,
    suffix: str = "",
    description: str = ""
) -> None:
    """
    Register a tool that retrieves a specific link endpoint for an object.
    The tool accepts object ID or ObjectIDURL as input.
    """
    
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

    mcp.tool(
        name=name,
        description=(
            f"{description}\n\n"
            "Input: the object ID (e.g., 'CA.SM::Domain@03-...') **or** the full object detail URL.\n"
            "Output: JSON response from the requested endpoint.\n"
            "This tool will construct the proper URL automatically."
        )
    )(tool)

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
    """Return the current keys stored in the detail cache."""

    return "DETAIL_CACHE keys:\n" + json.dumps(show_detail_cache(), indent=2)

@mcp.tool(name="clear_detail_cache", description="Clear the SiteMinder object detail cache.")
async def clear_detail_cache_tool() -> str:
    """Remove all entries from the detail cache."""

    clear_detail_cache()
    return "DETAIL_CACHE cleared."

@mcp.resource("siteminder://objects/{obj_id}")
async def get_object_resource(obj_id: str) -> str:
    """Read a SiteMinder object's raw JSON by its ID.
    
    The obj_id should be the SiteMinder object identifier (e.g., CA.SM::Domain@...).
    """
    token = await ensure_token()
    if not token:
        raise RuntimeError("Failed to get session token")
    
    detail = await get_object_by_id(obj_id, token)
    return json.dumps(detail, indent=2)
