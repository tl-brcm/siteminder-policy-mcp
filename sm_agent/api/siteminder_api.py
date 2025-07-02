"""Async helpers for interacting with the SiteMinder REST API."""

import logging
from typing import Any, Optional

import httpx
from cachetools import TTLCache

from ..core.config import (
    SITE_MINDER_BASE_URL,
    SITE_MINDER_USERNAME,
    get_siteminder_password,
)
from .tls import create_insecure_httpx_client
from ..core.cache_util import TimedCache

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

LOGIN_URL = f"{SITE_MINDER_BASE_URL}/ca/api/sso/services/login/v1/token"
# Cache of object details keyed by URL.  Entries expire after 5 minutes.
DETAIL_CACHE = TTLCache(maxsize=100, ttl=300)

# Cache the login token for 15 minutes to avoid frequent re-authentication.
TOKEN_CACHE = TimedCache(ttl_seconds=900)

# Generic in-memory cache for arbitrary objects keyed by type.
OBJECT_CACHE: dict[str, dict] = {}

def get_siteminder_base_url() -> str:
    """Return the base URL for the SiteMinder REST API."""

    return SITE_MINDER_BASE_URL

def build_object_id_url(obj_id: str) -> str:
    """Construct the detail URL for a given object id."""

    base = get_siteminder_base_url()
    return f"{base}/ca/api/sso/services/policy/v1/objects/{obj_id}"

async def get_token() -> Optional[str]:
    """Retrieve and cache a SiteMinder session token."""

    cached_token = TOKEN_CACHE.get("bearer_token")
    if cached_token:
        return cached_token

    logger.debug(f"Attempting login to SiteMinder at {LOGIN_URL}")
    siteminder_password = get_siteminder_password()
    if not siteminder_password:
        logger.error("SiteMinder password is not available. Cannot retrieve token.")
        return None
    auth = httpx.BasicAuth(SITE_MINDER_USERNAME, siteminder_password)
    async with create_insecure_httpx_client() as client:
        try:
            resp = await client.post(LOGIN_URL, auth=auth, timeout=15.0)
            resp.raise_for_status()
            session_key = resp.json().get("sessionkey")
            logger.debug(f"Retrieved session key: {session_key}")
            if session_key:
                TOKEN_CACHE.set("bearer_token", session_key)
            return session_key
        except Exception:
            logger.exception("Failed to retrieve SiteMinder session token")
            return None

def get_headers(token: str) -> dict:
    """Construct common headers for authenticated requests."""

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

async def http_get_with_token_refresh(
    url: str, token: Optional[str] = None, retries: int = 1
) -> Any:
    """GET ``url`` using the provided token and retry on 401 responses."""

    if not token:
        token = await get_token()

    headers = get_headers(token)
    async with create_insecure_httpx_client() as client:
        for attempt in range(retries + 1):
            try:
                resp = await client.get(url, headers=headers, timeout=30.0)
                if resp.status_code == 401 and attempt < retries:
                    logger.warning("Token expired. Refreshing...")
                    token = await get_token()
                    headers = get_headers(token)
                    continue
                resp.raise_for_status()
                return resp.json()
            except Exception:
                logger.exception(f"HTTP GET failed for {url}")
                if attempt == retries:
                    return None

async def fetch_objects(class_name: str, token: Optional[str] = None) -> list[dict[str, Any]]:
    """Return a list of objects for the given class."""

    url = f"{get_siteminder_base_url()}/ca/api/sso/services/policy/v1/{class_name}"
    logger.debug(f"[FETCH] {class_name}: {url}")
    resp_json = await http_get_with_token_refresh(url, token, retries=1)
    return resp_json.get("data", []) if resp_json else []

async def search_objects(
    class_name: str, token: Optional[str] = None, filter_expr: str = ""
) -> list[dict[str, Any]]:
    """Search objects using a filter expression."""

    url = (
        f"{get_siteminder_base_url()}/ca/api/sso/services/policy/v1/{class_name}?filter={filter_expr}"
    )
    logger.debug(f"[FILTER] {class_name} filter: {filter_expr}")
    resp_json = await http_get_with_token_refresh(url, token, retries=1)
    return resp_json.get("data", []) if resp_json else []

DETAIL_CACHE = TTLCache(maxsize=100, ttl=300)  # Example: 100 items, 5 minutes
async def get_object_details_from_href(
    href: str, token: Optional[str] = None
) -> dict[str, Any]:
    """Fetch object details for a direct href, using cache when possible."""

    if href in DETAIL_CACHE:
        logger.debug(f"[CACHE HIT] get_object_details_from_href: {href}")
        return DETAIL_CACHE[href]

    logger.debug(f"[DETAIL] Fetching object from: {href}")
    resp_json = await http_get_with_token_refresh(href, token, retries=1)
    if resp_json:
        DETAIL_CACHE[href] = resp_json
        logger.debug(
            f"[CACHE WRITE] Cached href: {href} (cache size: {len(DETAIL_CACHE)})"
        )
    else:
        logger.debug(f"[CACHE SKIP] No valid response for href: {href}")
    return resp_json if resp_json else {}

async def get_object_by_id(obj_id: str, token: Optional[str] = None) -> dict[str, Any]:
    """Convenience wrapper to fetch details for a specific object id."""

    url = build_object_id_url(obj_id)
    logger.debug(f"[GET BY ID] Fetching object from: {url}")
    resp_json = await http_get_with_token_refresh(url, token, retries=1)
    return resp_json if resp_json else {}

def show_detail_cache() -> list[str]:
    """Return a list of cached hrefs."""

    return list(DETAIL_CACHE.keys())

def clear_detail_cache() -> None:
    """Clear all entries from the detail cache."""

    DETAIL_CACHE.clear()
