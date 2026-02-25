# SiteMinder MCP Server - Project Summary

This project implements a Model Context Protocol (MCP) server that provides a natural language interface to the Broadcom SiteMinder (Symantec SiteMinder) Policy Management REST API.

## Core Architecture
- **Framework:** Built using `FastMCP` (Python).
- **API Client:** Asynchronous `httpx` client with custom TLS handling and session management.
- **Security:** 
  - Supports OIDC/OAuth2 proxying for secure access.
  - TLS termination and reverse proxying provided via an integrated Nginx configuration.
- **Caching:** Implements `TTLCache` for object details and `TimedCache` for session tokens to reduce API load and improve response times.

## Implemented Features

### 1. Dynamic Object Discovery & Tooling
- **Registry-Driven:** Object types (Realms, Domains, Agents, etc.) are defined in `sm_registry.json`.
- **Automatic Tool Generation:** The server dynamically registers `list_<type>_summary` and `search_<type>` tools for every object type in the registry.
- **Smart Formatting:** Results are automatically formatted into human-readable summaries with core fields extracted (Name, ID, Path, Description).

### 2. Deep Object Inspection
- **Child Retrieval:** `get_children_of_object` to navigate policy hierarchies.
- **Dependency Tracking:** `get_usedby_of_object` to identify where a policy object is referenced.
- **Expanded Views:** `get_expanded_of_object` for full nested details in a single call.
- **Schema Info:** `get_classinfo_of_object` and `get_editinfo_of_object` for metadata and valid attribute ranges.

### 3. Policy Management (CRUD)
- **Agent Creation:** Dedicated `create_sm_agent` tool for provisioning new Web Agents.
- **Generic Retrieval:** `get_object_by_id` for fetching any object by its SiteMinder UID.

### 4. Robust API Interaction
- **Token Auto-Refresh:** Automatically detects 401 Unauthorized responses and refreshes the SiteMinder session token without failing the user's request.
- **URL Normalization:** (Recently Added) A robust middleware layer that rewrites internal API links (which may contain inaccessible ports like :8443) to match the configured public API gateway.
- **Insecure TLS Support:** Configurable SSL verification to support development environments with self-signed certificates.

## Technical Configuration
- **Environment:** Managed via `.env` file for API endpoints, credentials, and OIDC settings.
- **Infrastructure:** Includes PowerShell/Shell scripts for managing the Nginx proxy.
- **Logging:** Structured logging with DEBUG levels for troubleshooting API handshakes and tool executions.

## Usage in LLMs
The server allows an LLM (like ChatGPT or Claude via Cursor/MCP) to:
- "Find all realms protecting the /voonair path."
- "Show me what objects are using this specific Agent Configuration."
- "Create a new Web Agent named 'TestAgent' for my domain."
- "Explore the children of the 'Production' domain."
