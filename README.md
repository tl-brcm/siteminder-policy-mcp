# SiteMinder Policy MCP Assistant

> **Disclaimer:** This is a sample project and is not intended for production use. It is offered as-is as a starting point for the community.

This project implements a Model Contextual Protocol (MCP) server for Broadcom SiteMinder. It allows AI assistants or other automation tools to interact with a SiteMinder policy environment by exposing a powerful, intuitive set of tools for querying and analyzing policy objects.

## ✨ Features

- **Dynamic Tool Generation:** Automatically creates `list` and `search` tools for all registered SiteMinder object types (Domains, Realms, Policies, etc.).
- **Relationship Navigation:** Provides tools to explore object dependencies, such as finding all policies that use a specific realm (`get_usedby_of_object`) or viewing child objects (`get_children_of_object`).
- **Intelligent Caching:** In-memory caching for API tokens and object details to improve performance and reduce load on the SiteMinder API.
- **Flexible Deployment:** Can be run as a local development server with an SSE endpoint or as a stdio-based server for integration with other processes.
- **Optimized Tool Helper Text:** The tool helper text is optimized to refer to "agent config" as "agent config object" or "aco", and the output of the `get_object_by_id` tool will now hide any parameters that start with "#".

## 📂 Project Structure

The project follows a standard Python package structure to ensure modularity and scalability. All core source code resides within the `sm_mcp` directory.

```
/
├── sm_mcp/            # Main source package
│   ├── __init__.py
│   ├── api/             # SiteMinder API client and helpers
│   │   ├── siteminder_api.py
│   │   └── tls.py
│   ├── core/            # Cross-cutting concerns (config, cache)
│   │   ├── config.py
│   │   └── cache_util.py
│   └── tools/           # MCP tool definitions and registration
│       ├── tooling.py
│       ├── sm_registry.json
│       └── sm_utils.py
│
├── .env.example         # Example environment file
├── main.py              # Main entry point for stdio transport
├── dev.py               # Entry point for development (ASGI/SSE)
└── requirements.txt     # Python dependencies
```

### Module Overview

- **`sm_mcp/api`**: Handles all direct communication with the SiteMinder REST API, including authentication, session management, and data fetching.
- **`sm_mcp/core`**: Contains core application services. `config.py` loads settings from the environment, and `cache_util.py` provides caching utilities.
- **`sm_mcp/tools`**: Defines and registers all the tools available to the MCP agent. `tooling.py` is the central hub, `sm_registry.json` defines the available SiteMinder object types, and `sm_utils.py` provides formatting helpers.
- **`main.py` / `dev.py`**: Entry points for running the server in different modes.

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10+
- Access to a Broadcom SiteMinder environment with the REST API enabled.

### 2. Installation

Clone the repository and install the required dependencies.

```bash
git clone <repository-url>
cd siteminder-mcp
pip install -r requirements.txt
```

### 3. Configuration

The server is configured using environment variables. Create a `.env` file in the project root by copying the `.env.example` file (if one exists) or creating it from scratch.

**`.env` file:**
```
# SiteMinder API Endpoint
SITE_MINDER_BASE_URL="https://your-siteminder-host.example.com"

# SiteMinder API Credentials
SITE_MINDER_USERNAME="your_api_user"
SITE_MINDER_PASSWORD="your_api_password"

# Set to "false" to disable SSL certificate verification (for development/testing)
VERIFY_SSL="true"
```

### 4. Running the Server

**Standard I/O Mode (Primary)**

This is the standard way to run the MCP server for integration with agents (like Claude Desktop or Gemini).

```bash
python main.py
```

**(Note: `dev.py` / SSE mode is currently undergoing migration to FastMCP 3.x and may not function as expected. Please use `main.py`.)**

## 🛠️ Available Tools

Once running, the agent provides numerous tools to interact with SiteMinder, including:

- `list_<object_type>_summary`: Shows a summary of all objects of a given type (e.g., `list_SmDomain_summary`).
- `search_<object_type>`: Searches for objects using a filter expression (e.g., `search_SmRealm(filter_expression="Name contains 'test'")`). The tool for `SmAgentConfig` objects also accepts `aco` as a valid name for the object.
- `get_object_by_id`: Fetches the full details of an object by its unique ID. The output of this tool will hide any parameters that start with "#".
- `get_children_of_object`: Lists all child objects of a given object.
- `get_usedby_of_object`: Shows which other objects depend on or use a given object.
- ...and several others for navigating object relationships and metadata.

## 📚 Available Resources

The server exposes SiteMinder objects as readable resources. This allows the agent to "read" an object directly.

- `siteminder://objects/{obj_id}`: Read the full JSON detail of a SiteMinder object by its ID (e.g., `siteminder://objects/CA.SM::Domain@03-...`).
