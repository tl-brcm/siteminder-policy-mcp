# SiteMinder MCP Server

This project implements a Model Contextual Protocol (MCP) server for Broadcom SiteMinder. It allows AI assistants or automation tools to interact with SiteMinder policy configurations and audit logs via standardized APIs and structured tooling.

## 🧩 Components

- **sm_policy_mcp/** (in another repo) MCP service that connects to SiteMinder's policy store via REST API. Enables querying and inspection of objects such as Realms, Rules, Policies, Agents, etc.

## 🚀 Getting Started

Each component runs independently using its own Python virtual environment.

### Running Policy MCP
```bash
cd sm_policy_mcp
uvicorn dev:app --reload --port 3123 --host 0.0.0.0
```

## 📚 Python Modules Overview

The repository consists of several standalone Python modules. Their roles are:

- **`config.py`** – Loads environment variables such as the SiteMinder base URL and credentials. This module centralizes configuration for the other modules.
- **`tls.py`** – Provides `create_insecure_httpx_client`, which creates an `httpx.AsyncClient` configured according to SSL verification settings.
- **`cache_util.py`** – Implements a small time-based cache (`TimedCache`) and exposes `object_detail_cache` used to store retrieved SiteMinder object details.
- **`siteminder_api.py`** – Wraps the REST API calls to SiteMinder. It manages authentication tokens, fetches and searches for objects, and retrieves detail data, while caching responses where possible.
- **`sm_registry.py`** – Defines the list of supported SiteMinder object classes and generates default help text and formatting callbacks for each class.
- **`sm_utils.py`** – Contains helper utilities for formatting objects and extracting core fields from API responses.
- **`tooling.py`** – Creates the `FastMCP` instance and registers tools that leverage the API wrappers. These tools provide search, list and detail retrieval commands to the MCP server.
- **`dev.py`** – An ASGI app used for local development. It wires the MCP server into Starlette and exposes a Server Sent Events (SSE) endpoint.
- **`main.py`** – Minimal entry point that runs the MCP server on standard I/O. Useful when integrating with other tooling.

These modules together provide a lightweight interface for exploring and interrogating SiteMinder policies via the MCP protocol.
