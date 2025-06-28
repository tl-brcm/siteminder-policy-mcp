"""Helpers for constructing HTTPX clients with relaxed TLS settings."""

import ssl
import httpx
from ..core.config import VERIFY_SSL

def create_insecure_httpx_client() -> httpx.AsyncClient:
    """Return an ``AsyncClient`` that optionally disables SSL verification."""

    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    if not VERIFY_SSL:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    transport = httpx.AsyncHTTPTransport(verify=ctx)
    return httpx.AsyncClient(transport=transport)
