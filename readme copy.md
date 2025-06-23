# SiteMinder MCP Server

This project implements a Model Contextual Protocol (MCP) server for Broadcom SiteMinder. It allows AI assistants or automation tools to interact with SiteMinder policy configurations and audit logs via standardized APIs and structured tooling.

## 🧩 Components

- **sm_policy_mcp/** (In antoher repo) MCP service that connects to SiteMinder's policy store via REST API. Enables querying and inspection of objects such as Realms, Rules, Policies, Agents, etc.

## 🚀 Getting Started

Each component runs independently using its own Python virtual environment.


### Running Policy MCP
```bash
cd sm_policy_mcp
uvicorn dev:app --reload --port 3123 --host 0.0.0.0
```
