# SiteMinder Technical Reference

This document provides technical details for the `siteminder-policy-management` skill.

## 🗂 Object Registry & Attributes

| Object Type | Core Attributes for Filters | Description |
| :--- | :--- | :--- |
| **SmRealm** | `Name`, `ResourceFilter`, `Desc` | Defines protected URL paths. |
| **SmDomain** | `Name`, `Desc`, `IsAffiliate` | Container for policy objects. |
| **SmAgent** | `Name`, `Desc` | Web Agent definition. |
| **SmAgentConfig** | `Name`, `Desc` | ACO (Agent Configuration Object). |
| **SmPolicy** | `Name`, `IsEnabled`, `Desc` | Links Rules to User Directories. |
| **SmAuthScheme** | `Name`, `Level`, `Library` | Authentication logic. |

## 🔍 Filter Expression Syntax

The MCP server uses a SQL-like syntax for the `filter_expression` parameter in all `search_` tools.

- **Equality:** `Name = 'Marketing_Domain'`
- **Partial Match:** `ResourceFilter contains '/login'`
- **Inequality:** `IsEnabled != false`
- **Numeric:** `Level > 5`
- **Logic:** `Name contains 'prod' AND Desc != null`

## 🔗 Endpoint Suffixes (Reference)

When using `get_children_of_object` or `get_usedby_of_object`, the server automatically appends the following suffixes to the object's base URL:

- `children`: Retrieves child objects (e.g., Rules in a Realm).
- `usedby`: Retrieves objects that reference the target (e.g., Policy using a Rule).
- `classinfo`: Schema information.
- `?op=expanded`: Full nested detail view.
