#!/usr/bin/env python3
"""
WEEK 1 — DAY 3: MCP server with Pydantic validation
====================================================
MCP = Model Context Protocol. Tools are the agent's hands.
If the tool accepts bad input, the agent is pwned.

This is a *teaching* version — uses plain Python validation instead of
Pydantic so you can read every check. Week 3 will upgrade to real Pydantic
+ a full JSON-RPC server.

Run: python mcp_server.py
"""

import re


# ---- Schema definitions (what a valid call looks like) ----

def validate_read_ticket(args):
    tid = args.get("ticket_id")
    if not isinstance(tid, str):
        raise ValueError("ticket_id must be a string")
    if not re.match(r"^[A-Za-z0-9]+$", tid):
        raise ValueError("ticket_id must be alphanumeric")
    if not (3 <= len(tid) <= 32):
        raise ValueError("ticket_id length 3-32")
    return {"ticket_id": tid}


def validate_write_crm(args):
    cid = args.get("customer_id")
    field = args.get("field")
    value = args.get("value")

    if not isinstance(cid, str):
        raise ValueError("customer_id must be a string")
    if not re.match(r"^[A-Z0-9\-]+$", cid):
        raise ValueError("customer_id must be uppercase alphanumeric with dashes")

    # ALLOWLIST — only these fields can be written
    if field not in ("phone", "email", "notes"):
        raise ValueError(f"field '{field}' not in allowlist")

    if not isinstance(value, str) or len(value) > 500:
        raise ValueError("value must be a string <= 500 chars")

    return {"customer_id": cid, "field": field, "value": value}


# ---- Tool registry ----

SAFE_TOOLS = {
    "read_ticket": validate_read_ticket,
    "write_crm":   validate_write_crm,
}


def validate_call(tool_name, args):
    if tool_name not in SAFE_TOOLS:
        raise PermissionError(f"❌ Tool '{tool_name}' not allowed")
    return SAFE_TOOLS[tool_name](args)


# ---- Demo ----

if __name__ == "__main__":
    tests = [
        ("read_ticket", {"ticket_id": "T123"}),
        ("read_ticket", {"ticket_id": "'; DROP TABLE tickets; --"}),
        ("write_crm",   {"customer_id": "C-100", "field": "notes", "value": "hi"}),
        ("write_crm",   {"customer_id": "C-100", "field": "role",  "value": "admin"}),
        ("delete_all",  {}),
    ]
    for name, args in tests:
        try:
            result = validate_call(name, args)
            print(f"✅ {name}: {result}")
        except (ValueError, PermissionError) as e:
            print(f"🛡️  BLOCKED {name}: {e}")
