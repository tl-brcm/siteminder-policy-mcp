import logging
import os
from typing import Any, Optional
from urllib.parse import urlparse, urlunparse

import httpx
from cachetools import TTLCache

from ..core import config
from .tls import create_insecure_httpx_client
from ..core.cache_util import TimedCache

logger = logging.getLogger(__name__)

# Cache of object details keyed by URL.  Entries expire after 5 minutes.
DETAIL_CACHE = TTLCache(maxsize=100, ttl=300)

# Cache the login token for 15 minutes to avoid frequent re-authentication.
TOKEN_CACHE = TimedCache(ttl_seconds=900)

# Generic in-memory cache for arbitrary objects keyed by type.
OBJECT_CACHE: dict[str, dict] = {}

def get_siteminder_base_url() -> str:
    """Return the base URL for the SiteMinder REST API, ensuring no trailing slash."""
    base_url = config.SITE_MINDER_BASE_URL
    if base_url:
        return base_url.rstrip("/")
    return ""

def get_login_url() -> str:
    """Return the login URL for the SiteMinder REST API."""
    base = get_siteminder_base_url()
    return f"{base}/ca/api/sso/services/login/v1/token" if base else ""

def build_object_id_url(obj_id: str) -> str:
    """Construct the detail URL for a given object id."""
    base = get_siteminder_base_url()
    return f"{base}/ca/api/sso/services/policy/v1/objects/{obj_id}"

def normalize_url(url: str) -> str:
    """Ensure the URL uses the configured base URL's scheme and netloc."""
    base_url = get_siteminder_base_url()
    if not base_url or not url.startswith("http"):
        return url

    base_parsed = urlparse(base_url)
    url_parsed = urlparse(url)

    # SiteMinder sometimes returns hrefs with internal ports (e.g. :8443)
    # that may not be accessible. We normalize to the configured base URL.
    if "/ca/api/sso/" in url_parsed.path:
        normalized = urlunparse(url_parsed._replace(
            scheme=base_parsed.scheme,
            netloc=base_parsed.netloc
        ))
        if normalized != url:
            logger.debug(f"Normalized URL from {url} to {normalized}")
        return normalized
    return url

async def get_token() -> Optional[str]:
    """Retrieve and cache a SiteMinder session token."""
    cached_token = TOKEN_CACHE.get("bearer_token")
    if cached_token:
        return cached_token

    login_url = get_login_url()
    if not login_url:
        logger.error("SITE_MINDER_BASE_URL is not configured.")
        return None

    logger.debug(f"Attempting login to SiteMinder at {login_url}")
    auth = httpx.BasicAuth(config.SITE_MINDER_USERNAME, config.SITE_MINDER_PASSWORD)
    async with create_insecure_httpx_client() as client:
        try:
            resp = await client.post(login_url, auth=auth, timeout=15.0)
            resp.raise_for_status()
            session_key = resp.json().get("sessionkey")
            if session_key:
                TOKEN_CACHE.set("bearer_token", session_key)
                logger.debug("Successfully retrieved SiteMinder session key.")
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
    url = normalize_url(url)
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

async def http_post_with_token_refresh(
    url: str, data: dict, token: Optional[str] = None, retries: int = 1
) -> Any:
    """POST ``data`` to ``url`` using the provided token and retry on 401 responses."""
    url = normalize_url(url)
    if not token:
        token = await get_token()

    headers = get_headers(token)
    async with create_insecure_httpx_client() as client:
        for attempt in range(retries + 1):
            try:
                resp = await client.post(url, headers=headers, json=data, timeout=30.0)
                if resp.status_code == 401 and attempt < retries:
                    logger.warning("Token expired. Refreshing...")
                    token = await get_token()
                    headers = get_headers(token)
                    continue
                resp.raise_for_status()
                return resp.json()
            except Exception:
                logger.exception(f"HTTP POST failed for {url}")
                if attempt == retries:
                    return None

async def fetch_objects(class_name: str, token: Optional[str] = None) -> list[dict[str, Any]]:
    """Return a list of objects for the given class."""
    url = f"{get_siteminder_base_url()}/ca/api/sso/services/policy/v1/{class_name}"
    resp_json = await http_get_with_token_refresh(url, token, retries=1)
    return resp_json.get("data", []) if resp_json else []

async def create_object(class_name: str, data: dict, token: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Create a new object of the given class."""
    url = f"{get_siteminder_base_url()}/ca/api/sso/services/policy/v1/{class_name}"
    resp_json = await http_post_with_token_refresh(url, data, token, retries=1)
    return resp_json

async def search_objects(
    class_name: str, token: Optional[str] = None, filter_expr: str = ""
) -> list[dict[str, Any]]:
    """Search objects using a filter expression."""
    url = (
        f"{get_siteminder_base_url()}/ca/api/sso/services/policy/v1/{class_name}?filter={filter_expr}"
    )
    resp_json = await http_get_with_token_refresh(url, token, retries=1)
    return resp_json.get("data", []) if resp_json else []

async def get_object_details_from_href(
    href: str, token: Optional[str] = None
) -> dict[str, Any]:
    """Fetch object details for a direct href, using cache when possible."""
    if href in DETAIL_CACHE:
        return DETAIL_CACHE[href]

    resp_json = await http_get_with_token_refresh(href, token, retries=1)
    if resp_json:
        DETAIL_CACHE[href] = resp_json
    return resp_json if resp_json else {}

async def get_object_by_id(obj_id: str, token: Optional[str] = None) -> dict[str, Any]:
    """Convenience wrapper to fetch details for a specific object id."""
    url = build_object_id_url(obj_id)
    resp_json = await http_get_with_token_refresh(url, token, retries=1)
    return resp_json if resp_json else {}

def show_detail_cache() -> list[str]:
    """Return a list of cached hrefs."""
    return list(DETAIL_CACHE.keys())

def clear_detail_cache() -> None:
    """Clear all entries from the detail cache."""
    DETAIL_CACHE.clear()