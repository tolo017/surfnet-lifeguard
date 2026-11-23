#!/usr/bin/env python3
"""
GUARDIAN — The Security Agent
=============================
Runs as a SEPARATE process. Tide calls it before every privileged action.

Contract:
  - Reads ONE JSON action from stdin
  - Writes ONE JSON decision to stdout
  - Appends every decision to guardian_audit.jsonl

Guardian is deterministic code — NOT an LLM. That's the whole point.
"""

import sys
import json
import datetime

# ─────────────────────────────────────────────────────────────
# 1. THE TRUTH TABLE — who is allowed to be who?
#    We NEVER trust what the caller claims. We look it up here.
# ─────────────────────────────────────────────────────────────
VERIFIED_ROLES = {
    "support@surfnet.com": "support",
    "admin@surfnet.com":   "admin",
    # Anyone NOT listed is treated as "customer" by default.
}

def verify_role(email, claimed_role):
    """
    Return the TRUE role for this email, from OUR records.
    We ignore 'claimed_role' on purpose — that's the confused deputy fix.
    """
    return VERIFIED_ROLES.get(email, "customer")


# ─────────────────────────────────────────────────────────────
# 2. SMALL HELPERS — make decisions readable
# ─────────────────────────────────────────────────────────────
def allow(action_id, reason="ok"):
    return {
        "action_id": action_id,
        "allow": True,
        "reason": reason,
        "requires_human": False,
    }

def block(action_id, reason, human=False):
    return {
        "action_id": action_id,
        "allow": False,
        "reason": reason,
        "requires_human": human,
    }


# ─────────────────────────────────────────────────────────────
# 3. THE RULE ENGINE — one rule per action type.
#    Each rule is a function that returns a decision dict.
# ─────────────────────────────────────────────────────────────
def decide(action):
    action_id = action.get("action_id", "unknown")
    action_type = action.get("action_type", "")
    params = action.get("params", {})
    email = action.get("requested_by_email", "")

    # ⭐ VERIFIED role, not the claimed one
    role = verify_role(email, action.get("requested_by_role", "customer"))

    # ---- RULE: refund ----
    if action_type == "refund":
        if role == "customer":
            return block(action_id, "customers cannot issue refunds")
        amount = params.get("amount", 0)
        if not isinstance(amount, int):
            return block(action_id, "amount must be an integer")
        if amount < 0:
            return block(action_id, "amount cannot be negative")
        if amount > 500:
            return block(action_id, "refund > $500 requires human approval", human=True)
        return allow(action_id)

    # ---- RULE: write_crm ----
    if action_type == "write_crm":
        if role == "customer":
            return block(action_id, "customers cannot write to CRM")
        field = params.get("field", "")
        # ALLOWLIST — not blocklist. We list the safe fields explicitly.
        if field not in ("phone", "email", "notes"):
            return block(action_id, f"field '{field}' not in allowlist")
        value = params.get("value", "")
        if not isinstance(value, str) or len(value) > 500:
            return block(action_id, "value too long or wrong type")
        return allow(action_id)

    # ---- RULE: read_crm ----
    if action_type == "read_crm":
        return allow(action_id)

    # ---- RULE: send_email ----
    if action_type == "send_email":
        if role == "customer":
            return block(action_id, "customers cannot send emails")
        return allow(action_id)

    # ---- UNKNOWN ACTION — default deny (allowlist principle) ----
    return block(action_id, f"unknown action_type: '{action_type}'")


# ─────────────────────────────────────────────────────────────
# 4. MAIN — read, decide, log, respond
# ─────────────────────────────────────────────────────────────
def main():
    raw = sys.stdin.read()

    try:
        action = json.loads(raw)
    except json.JSONDecodeError as e:
        # Malformed input = fail closed
        print(json.dumps({
            "allow": False,
            "reason": "bad_json: " + str(e),
            "requires_human": False,
        }))
        return

    decision = decide(action)

    # Append-only audit trail — one JSON per line (JSONL format)
    log_entry = {
        "time": datetime.datetime.now().isoformat(),
        "action": action,
        "decision": decision,
    }
    with open("guardian_audit.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Send the decision back to Tide via stdout
    print(json.dumps(decision))


if __name__ == "__main__":
    main()
