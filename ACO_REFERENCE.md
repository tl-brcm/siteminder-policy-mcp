# SiteMinder Agent Configuration (ACO) Reference

This reference provides a summary of critical Agent Configuration Object (ACO) parameters for SiteMinder 12.9. Use this to troubleshoot agent behavior, security policies, and performance issues.

## 🛡️ Security & URL Handling

| Parameter | Purpose | Impact of Change |
| :--- | :--- | :--- |
| **BadUrlChars** | Defines characters blocked in URLs. | Prevents XSS/Injection. Adding chars may break legacy apps. |
| **BadCssChars** | Defines characters blocked in CSS content. | Prevents CSS-based attacks. |
| **IgnoreExt** | Extensions skipped by the agent. | Performance. Adding `.html` would leave pages unprotected. |
| **MaxUrlSize** | Max processing length for URLs. | Security. Default is usually 4096. |
| **CustomIpHeader** | Header for client IP (e.g., `X-Forwarded-For`). | Essential for audit accuracy behind load balancers. |

## 🍪 Session & Cookie Management

| Parameter | Purpose | Impact of Change |
| :--- | :--- | :--- |
| **CookieDomain** | Domain for `SMSESSION` cookie. | Must match the application domain for SSO to work. |
| **CookieDomainScope** | Number of domain levels for the cookie. | Controls cross-subdomain SSO breadth. |
| **PersistentCookies** | Save cookie to disk (Yes/No). | Security. If "Yes," session survives browser restart. |
| **AcceptTPCookie** | Accept 3rd-party cookies (Yes/No). | Enables cross-domain SSO via redirects. |

## ⚙️ Core Agent Behavior

| Parameter | Purpose | Impact of Change |
| :--- | :--- | :--- |
| **DefaultAgentName** | Fallback agent identity. | Used if no specific agent matches the resource. |
| **EnableWebAgent** | Master kill-switch (Yes/No). | Disabling stops all protection on that web server. |
| **LogOffUri** | URI that triggers logout. | Accessing this path clears the user's session. |
| **AllowCacheHeaders** | Allow server caching (Yes/No). | Security. If "No," prevents browser from caching sensitive pages. |

## 🚀 Performance & Logging

| Parameter | Purpose | Impact of Change |
| :--- | :--- | :--- |
| **MaxResourceCacheSize** | Number of cached resources. | Higher values reduce Policy Server round-trips. |
| **MaxSessionCacheSize** | Number of cached user sessions. | Improves performance for high-traffic sites. |
| **EnableAuditing** | Log user activity (Yes/No). | Compliance. Required for tracking "Who accessed what." |

## 📝 Troubleshooting Workflow
When asked about an ACO parameter:
1. Fetch the ACO using `get_object_by_id` or `get_expanded_of_object`.
2. Compare current values against this reference.
3. Check for conflicting parameters (e.g., `AgentName` vs `DefaultAgentName`).
