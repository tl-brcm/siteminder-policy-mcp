# SiteMinder Policy MCP Assistant

> **Disclaimer:** This is a sample project and is not intended for production use. It is offered as-is as a starting point for the community.

This project implements a Model Contextual Protocol (MCP) server for Broadcom SiteMinder using **FastMCP 3.0**. It allows AI assistants (like Cursor) to interact with a SiteMinder policy environment through a secure, OIDC-protected interface.

## ✨ Features

- **OAuth 2.0 / OIDC Integration:** Built-in support for Broadcom Identity Security Platform (IDSP) acting as a Resource Server.
- **Dynamic Tool Generation:** Automatically creates `list` and `search` tools for all registered SiteMinder object types.
- **Secure Reverse Proxy:** Includes a portable Nginx configuration for local HTTPS support with custom hostnames.
- **Persistent Sessions:** Client registrations and tokens are persisted locally in `oauth_storage`.
- **Intelligent Caching:** Performance-optimized fetching with multi-level caching for SiteMinder objects.

## 📂 Project Structure

```
/
├── sm_mcp/              # Main source package
│   ├── api/             # SiteMinder API client
│   ├── core/            # Config & Logging
│   └── tools/           # MCP Tooling & OIDC Logic
├── nginx-scripts/       # Portable Nginx management
├── oauth_storage/       # Persistent client registrations (local)
├── cert.pem / key.pem   # Self-signed SSL certificates
├── generate_cert.py     # SSL certificate generator
├── main.py              # Server entry point (HTTP/SSE)
└── requirements.txt     # Python dependencies
```

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10+
- Access to a Broadcom SiteMinder REST API.
- Broadcom IDSP account for OIDC authentication.

### 2. Local Hostname Setup

To use the custom development hostname, add the following to your `C:\Windows\System32\drivers\etc\hosts` file:
```text
127.0.0.1  mcp.vm.demo
```

### 3. Installation & SSL Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Generate SSL certificates for mcp.vm.demo
python generate_cert.py

# Trust the certificate (Windows)
Import-Certificate -FilePath "cert.pem" -CertStoreLocation Cert:\CurrentUser\Root
```

### 4. Configuration

Create a `.env` file from the example:

```ini
# SiteMinder API
SITE_MINDER_BASE_URL="https://ps8:8443"
SITE_MINDER_USERNAME="siteminder"
SITE_MINDER_PASSWORD="your_password"
VERIFY_SSL="false"

# OIDC Proxy Configuration (Broadcom IDSP)
IDSP_OIDC_URL="https://ssp-215.demo-broadcom.com/default"
IDSP_CLIENT_ID="your-idsp-app-client-id"
IDSP_CLIENT_SECRET="your-idsp-app-secret"
IDSP_AUDIENCE="https://mcp.vm.demo:8443/sm-policy/mcp"
IDSP_SCOPES="openid phone profile offline_access groups siteminder:access email"

# FastMCP Security
MCP_BASE_URL="https://mcp.vm.demo:8443/sm-policy"
JWT_SIGNING_KEY="generate-a-random-string-here"
LOG_LEVEL="DEBUG"
```

### 5. Running the Server

You need to run two components: the Python backend and the Nginx proxy.

**A) Start the Backend**
```bash
python main.py
```

**B) Start Nginx Proxy**
```powershell
cd nginx-scripts
.\run_nginx.ps1
```

## 🤖 Cursor Configuration

Add the server to Cursor under **Settings -> MCP**:

- **Name:** SiteMinder Policy
- **Type:** `SSE`
- **URL:** `https://mcp.vm.demo:8443/sm-policy/mcp`

Upon connection, Cursor will detect the security requirement and prompt you to sign in via your browser through Broadcom IDSP.

## 🛠️ Available Tools

- `list_<object_type>_summary`: Summary of all objects (Domains, Realms, etc.).
- `search_<object_type>`: Search using filter expressions (e.g., `Name contains 'login'`).
- `get_object_by_id`: Full JSON detail for a specific ID.
- `get_children_of_object`: Explore child relationships.
- `get_usedby_of_object`: Identify dependencies.

## 🧠 Agent Skills (Experimental)

This server provides **Agent Skills** to help LLMs navigate complex SiteMinder workflows more effectively.

### 1. What are Agent Skills?
Agent Skills are structured instructions (`SKILL.md`) and technical references (`REFERENCE.md`) that provide "procedural memory" to the AI. They define specific workflows for:
- Mapping Realms to Domains.
- Inspecting ACO/HCO attributes.
- Performing safety checks before modifications.

### 2. How to Synchronize Skills
Clients can verify and update their local skill files using the following tools:

- **Check Version:** Call `get_skill_info` to see the latest version and hash of the server-side skill.
- **Download Package:** Call `get_skill_sync_package` to retrieve the full content of `SKILL.md` and `REFERENCE.md`.

### 3. Client Installation (Manual)
To install the skill in your local environment (e.g., for Gemini CLI or Cursor):
1. Call `get_skill_sync_package`.
2. Create a folder named `siteminder-policy` in your local agent skills directory.
3. Save the `SKILL.md` and `REFERENCE.md` content into that folder.

## 🔒 Security Note

This server implements the **OIDC Proxy** pattern. It handles Dynamic Client Registration (DCR) locally for the LLM client and proxies the authentication to your upstream Broadcom IDSP. This ensures your SiteMinder environment remains protected by enterprise-grade identity management while providing a seamless experience for the AI assistant.