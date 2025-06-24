"""Registry of SiteMinder object types and their metadata."""

from sm_utils import default_formatter  

OBJECT_CLASSES = {
    "SmRealm": {
        "description": "Defines a realm object",
        "attributes": [
            "Name", "Desc", "ProtectAll", "SessionType", "IdleTimeout",
            "MaxTimeout", "SyncAudit", "ProcessAuthEvents", "ProcessAzEvents",
            "ResourceFilter", "MinUserConfidenceLevel", "SessionDrift"
        ],
    },
    "SmAuthScheme": {
        "description": "Defines an authentication scheme",
        "attributes": [
            "Name", "Desc", "AuthSchemeType", "Level", "IsTemplate",
            "AllowSaveCreds", "IsRadius", "SupportsValidateIdentity",
            "AllowAuthLevelOverride", "IgnorePwCheck", "IPCheck",
            "PersistSessionVars", "Library", "Param", "Secret", "ExprString"
        ],
    },
    "SmAgent": {
        "description": "Defines a Web Agent",
        "attributes": ["Name", "Desc"],
    },
    "SmAgentConfig": {
        "description": "Agent Configuration Object",
        "attributes": ["Name", "Desc"],
    },
    "SmAgentGroup": {
        "description": "Defines an agent group",
        "attributes": ["Name", "Desc"],
    },
    "SmAgentType": {
        "description": "Defines an agent type",
        "attributes": ["Name", "Desc", "VendorType", "ResourceType"],
    },
    "SmDomain": {
        "description": "Defines a policy domain",
        "attributes": ["Name", "Desc", "IsAffiliate"],
    },
    "SmRule": {
        "description": "Defines a rule object",
        "attributes": ["Name", "Desc", "Actions", "Resource"],
    },
    "SmResponse": {
        "description": "Defines a response object",
        "attributes": ["Name", "Desc", "AccessAccept", "AccessReject"],
    },
    "SmUserDirectory": {
        "description": "User directory configuration",
        "attributes": ["Name", "Desc", "Namespace", "Server", "Username"],
    },
    "SmPolicy": {
        "description": "Defines a policy object",
        "attributes": ["Name", "Desc", "IsEnabled", "AllowAccess"],
    },
    "SmTrustedHost": {
        "description": "Defines a trusted host",
        "attributes": ["Name", "Desc", "IpAddr"],
    },
}

# Attach a default formatter and help text to each object type entry.
for name, obj in OBJECT_CLASSES.items():
    obj["formatter"] = default_formatter
    obj["help"] = (
        f"Search SiteMinder {name} objects using a filter expression.\n\n"
        f"Supported attributes:\n- " + "\n- ".join(obj["attributes"]) + "\n\n"
        "Examples:\n"
        "- Name contains 'login'\n"
        "- Desc != null\n"
        "- IsEnabled = true\n"
        "- Level > 500\n"
    )
