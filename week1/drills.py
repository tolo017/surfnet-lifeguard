#!/usr/bin/env python3
"""
WEEK 1 PYTHON DRILLS
Five concepts, each in a runnable form.

Run: python drills.py
"""

import json
import hashlib
import datetime


# ─────────────────────────────────────────────────────────────
# DRILL 1 — Dictionaries
# ─────────────────────────────────────────────────────────────
TOOL_MIN_ROLE = {
    "read_crm":        "customer",
    "write_crm":       "support",
    "refund":          "support",
    "delete_customer": "admin",
}


def drill_1():
    print("\n── Drill 1: Tools requiring admin ──")
    for tool, min_role in TOOL_MIN_ROLE.items():
        if min_role == "admin":
            print(f"  - {tool}")


# ─────────────────────────────────────────────────────────────
# DRILL 2 — Functions with type hints (role hierarchy)
# ─────────────────────────────────────────────────────────────
ROLE_LEVEL = {"customer": 1, "support": 2, "admin": 3}


def role_can(role: str, tool: str) -> bool:
    """True if `role` has enough privilege to call `tool`."""
    if tool not in TOOL_MIN_ROLE:
        return False
    required = TOOL_MIN_ROLE[tool]
    return ROLE_LEVEL.get(role, 0) >= ROLE_LEVEL.get(required, 99)


def drill_2():
    print("\n── Drill 2: role_can ──")
    print("  support  → refund: ", role_can("support", "refund"))
    print("  customer → refund: ", role_can("customer", "refund"))
    print("  admin    → delete: ", role_can("admin", "delete_customer"))
    print("  customer → unknown:", role_can("customer", "no_such_tool"))


# ─────────────────────────────────────────────────────────────
# DRILL 3 — Guard clauses (early return)
# ─────────────────────────────────────────────────────────────
def validate(data: dict) -> bool:
    if "email" not in data:
        return False
    email = data["email"]
    if not isinstance(email, str):
        return False
    if "@" not in email:
        return False
    if len(email) >= 100:
        return False
    return True


def drill_3():
    print("\n── Drill 3: Guard clauses ──")
    print("  {'email': 'a@b.com'} :", validate({"email": "a@b.com"}))
    print("  {'email': 'bad'}     :", validate({"email": "bad"}))
    print("  {}                   :", validate({}))


# ─────────────────────────────────────────────────────────────
# DRILL 4 — Try/except (fail closed)
# ─────────────────────────────────────────────────────────────
def safe_load(path: str) -> dict:
    """Load JSON from disk, or return {} on ANY error."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def drill_4():
    print("\n── Drill 4: Try/except ──")
    print("  missing file →", safe_load("/no/such/file.json"))


# ─────────────────────────────────────────────────────────────
# DRILL 5 — with statement + JSONL append
# ─────────────────────────────────────────────────────────────
def append_log(path: str, entry: dict) -> None:
    """Append one JSON object as a line. Never overwrites."""
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def drill_5():
    print("\n── Drill 5: append_log ──")
    append_log("drill_log.jsonl", {
        "time": datetime.datetime.now().isoformat(),
        "event": "drill_5_ran",
    })
    print("  wrote drill_log.jsonl")


# ─────────────────────────────────────────────────────────────
# BONUS — content-hash binding (defense against TOCTOU)
# ─────────────────────────────────────────────────────────────
def action_hash(action: dict) -> str:
    """Canonical fingerprint of an action. Change one byte → hash changes."""
    canonical = json.dumps(action, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def bonus():
    print("\n── Bonus: content-hash binding ──")
    a1 = {"customer_id": "C-100", "amount": 1}
    a2 = {"customer_id": "C-100", "amount": 5000}
    print("  hash($1)    :", action_hash(a1)[:16] + "...")
    print("  hash($5000) :", action_hash(a2)[:16] + "...")
    print("  same?       :", action_hash(a1) == action_hash(a2))


if __name__ == "__main__":
    drill_1()
    drill_2()
    drill_3()
    drill_4()
    drill_5()
    bonus()
