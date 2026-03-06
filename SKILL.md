---
name: siteminder-policy-management
description: Manages Broadcom SiteMinder policy objects, performs impact analysis, and navigates object hierarchies using the SiteMinder MCP server.
version: 1.3.0
---

# SiteMinder Policy Management

This skill provides expert procedures for administering SiteMinder policy stores. It emphasizes safety through dependency checking and precision through structured navigation.

## 🏛️ SiteMinder Object Relationship Model

This is the conceptual map of how SiteMinder objects relate to each other. Use this to trace the path from user to resource.

1.  **Domain:** The top-level application container.
    - Contains: Realms, Policies, User Directories, Responses, Variables.

2.  **Realm:** Defines a protected resource path (`ResourceFilter`).
    - Associated with: an Authentication Scheme.
    - Associated with: an Agent or Agent Group.
    - Contains: one or more Rules.

3.  **Agent:** Represents a client (e.g., a web server).
    - Associated with: an Agent Configuration Object (ACO). The `AgentName` in the ACO maps a hostname to a SiteMinder Agent object.
    - Can be a member of: an Agent Group.
    - The combination of **Agent + ResourceFilter** is how SiteMinder identifies a request's Realm.

4.  **Rule:** Defines an action for a resource (e.g., Allow/Deny, OnAuthAccept).
    - Associated with: Responses (within a Policy).

5.  **Policy:** The final enforcement point that connects users to resources.
    - Connects: A User Directory/Group...
    - With: ...a set of Rules...
    - And adds: ...Responses to those rules.
    - **CRITICAL:** A user has no access, even if a Rule allows it, until a Policy explicitly grants it to their group.

## 📚 Specialized Knowledge Resources
- **Common ACO Params:** See `ACO_REFERENCE.md` for the most critical parameters and their security impacts.
- **Full ACO Dictionary:** Use the `lookup_aco_parameter` tool to search the complete list of 150+ parameters for specific or obscure settings.
- **Technical Reference:** See `REFERENCE.md` for object attributes and filter syntax.

## 📋 Core Workflows

### 1. Object Hierarchy Navigation
When locating an object's parent (e.g., Domain for a Realm):
1. Use `search_smrealm` with a name or path filter.
2. Use `get_parent_of_object(id=REALM_ID)` to fetch the parent's full detail.
3. If the path is present in the initial search result, you can also parse it: `/SmDomains/<domain_name>/...`.
4. If the parent is not explicitly linked, use `get_usedby_of_object` to identify the containing container.

### 2. Configuration Inspection (ACO/HCO)
To inspect configuration parameters for an agent:
1. Locate the agent using `search_smagent`.
2. Extract the `AgentConfigLink` (ACO) or `HostConfigLink` (HCO).
3. Use `get_object_by_id` on the link to retrieve the full JSON.
4. Search the `Attributes` array for specific parameter names and values.

### 3. Impact Analysis (Pre-Modification)
Before any deletion or modification:
1. Run `get_usedby_of_object` on the target ID.
2. Review the list of referring objects (Policies, Groups, etc.).
3. If dependencies exist, provide a summary of the impact before proceeding.

### 4. Policy Trace
To trace a resource path to its enforcing policy:
1. `search_smrealm` using `ResourceFilter`.
2. `get_children_of_object` to identify Rules.
3. `get_usedby_of_object` on each Rule to find the linked Policies.

## 🛠 Tool Usage Guidelines
- **Filters:** Always wrap string values in single quotes (e.g., `Name = 'MyAgent'`).
- **Precision:** Use `search_<type>` instead of `list_<type>_summary` when the object name is known to reduce context noise.
- **Reference:** See `REFERENCE.md` for specific attribute names and schema details.
