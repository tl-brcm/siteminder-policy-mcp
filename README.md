# SiteMinder Policy MCP Assistant

This project implements a Model Contextual Protocol (MCP) server for Broadcom SiteMinder. It allows AI assistants or other automation tools to interact with a SiteMinder policy environment by exposing a powerful, intuitive set of tools for querying and analyzing policy objects.

## ✨ Features

- **Dynamic Tool Generation:** Automatically creates `list` and `search` tools for all registered SiteMinder object types (Domains, Realms, Policies, etc.).
- **Relationship Navigation:** Provides tools to explore object dependencies, such as finding all policies that use a specific realm (`get_usedby_of_object`) or viewing child objects (`get_children_of_object`).
- **Intelligent Caching:** In-memory caching for API tokens and object details to improve performance and reduce load on the SiteMinder API.
- **Flexible Deployment:** Can be run as a local development server with an SSE endpoint or as a stdio-based server for integration with other processes.

## 📂 Project Structure

The project follows a standard Python package structure to ensure modularity and scalability. All core source code resides within the `sm_agent` directory.

```
/
├── sm_agent/            # Main source package
│   ├── __init__.py
│   ├── api/             # SiteMinder API client and helpers
│   │   ├── siteminder_api.py
│   │   └── tls.py
│   ├── core/            # Cross-cutting concerns (config, cache)
│   │   ├── config.py
│   │   └── cache_util.py
│   └── tools/           # MCP tool definitions and registration
│       ├── tooling.py
│       ├── sm_registry.py
│       └── sm_utils.py
│
├── .env.example         # Example environment file
├── main.py              # Main entry point for stdio transport
├── dev.py               # Entry point for development (ASGI/SSE)
└── requirements.txt     # Python dependencies
```

### Module Overview

- **`sm_agent/api`**: Handles all direct communication with the SiteMinder REST API, including authentication, session management, and data fetching.
- **`sm_agent/core`**: Contains core application services. `config.py` loads settings from the environment, and `cache_util.py` provides caching utilities.
- **`sm_agent/tools`**: Defines and registers all the tools available to the MCP agent. `tooling.py` is the central hub, `sm_registry.py` defines the available SiteMinder object types, and `sm_utils.py` provides formatting helpers.
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

You can run the server in two modes:

**A) Development Mode (Recommended for testing)**

This mode uses the `dev.py` script to launch an ASGI server with a Server-Sent Events (SSE) endpoint for communication.

```bash
# Make sure you are in the root of the project directory
uvicorn dev:app --reload --port 3123 --host 0.0.0.0
```
The server will be available at `http://0.0.0.0:3123`.

**B) Standard I/O Mode**

This mode is for integrating the agent with other processes that communicate over `stdin` and `stdout`.

```bash
python main.py
```

## 🛠️ Available Tools

Once running, the agent provides numerous tools to interact with SiteMinder, including:

- `list_<object_type>_summary`: Shows a summary of all objects of a given type (e.g., `list_SmDomain_summary`).
- `search_<object_type>`: Searches for objects using a filter expression (e.g., `search_SmRealm(filter_expression="Name contains 'test'")`).
- `get_object_by_id`: Fetches the full details of an object by its unique ID.
- `get_children_of_object`: Lists all child objects of a given object.
- `get_usedby_of_object`: Shows which other objects depend on or use a given object.
- ...and several others for navigating object relationships and metadata.
