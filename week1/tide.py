#!/usr/bin/env python3
"""
TIDE — The AI Agent
===================
Runs as a SEPARATE process. Before ANY privileged action,
Tide calls Guardian (via subprocess) and asks permission.

If Guardian says no (or crashes), Tide does NOT act. Fail closed.
"""

import os
import sys
import json
import uuid
import subprocess

# Absolute path to guardian.py — works no matter where you run from
HERE = os.path.dirname(os.path.abspath(__file__))
GUARDIAN_SCRIPT = os.path.join(HERE, "guardian.py")


def ask_guardian(action):
    """
    Spawn Guardian as a subprocess, send the action on stdin,
    read the decision on stdout.

    Returns a decision dict — ALWAYS. Even on error, we fail closed.
    """
    try:
        result = subprocess.run(
            [sys.executable, GUARDIAN_SCRIPT],  # python guardian.py
            input=json.dumps(action),           # send action JSON
            capture_output=True,                # capture stdout/stderr
            text=True,                          # strings, not bytes
            timeout=5,                          # don't hang forever
        )
    except subprocess.TimeoutExpired:
        return {"allow": False, "reason": "guardian_timeout", "requires_human": False}

    if result.returncode != 0:
        # Guardian crashed → FAIL CLOSED
        return {
            "allow": False,
            "reason": "guardian_error: " + (result.stderr or "unknown"),
            "requires_human": False,
        }

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"allow": False, "reason": "guardian_bad_output", "requires_human": False}


def perform(action_type, params, sender_email, sender_claimed_role="customer"):
    """
    The one function all privileged actions go through.
    1. Build the action
    2. Ask Guardian
    3. Execute only if allowed
    """
    action = {
        "action_id": str(uuid.uuid4()),
        "action_type": action_type,
        "params": params,
        "requested_by_email": sender_email,
        "requested_by_role": sender_claimed_role,
    }

    decision = ask_guardian(action)

    if not decision.get("allow"):
        return {
            "ok": False,
            "reason": decision.get("reason"),
            "requires_human": decision.get("requires_human", False),
            "action_id": action["action_id"],
        }

    # ✅ Guardian approved — Tide can act
    print(f"   ⚡ Tide executes: {action_type} {params}")
    return {"ok": True, "action_id": action["action_id"]}


# Convenience wrappers — these are what the rest of the app calls
def do_refund(customer_id, amount, sender_email, claimed_role="customer"):
    return perform(
        "refund",
        {"customer_id": customer_id, "amount": amount},
        sender_email, claimed_role,
    )

def do_write_crm(customer_id, field, value, sender_email, claimed_role="customer"):
    return perform(
        "write_crm",
        {"customer_id": customer_id, "field": field, "value": value},
        sender_email, claimed_role,
    )
