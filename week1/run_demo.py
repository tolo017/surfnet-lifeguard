#!/usr/bin/env python3
"""
WEEK 1 RECAP DEMO
=================
Run the 5 scenarios that test what you learned:
  1. Legit support, small refund               → ALLOW
  2. Attacker CLAIMS admin, big refund         → BLOCK (confused deputy defeated)
  3. Real admin, big refund                    → BLOCK (needs human)
  4. Customer tries to write to CRM            → BLOCK
  5. Support tries to write 'role' field       → BLOCK (allowlist defends)
"""

from tide import do_refund, do_write_crm


def run(name, fn):
    print("\n" + "=" * 60)
    print("SCENARIO:", name)
    print("=" * 60)
    result = fn()
    status = "✅ ALLOWED" if result["ok"] else "🛡️ BLOCKED"
    print(f"   {status}: {result.get('reason', '')}")
    if result.get("requires_human"):
        print("   👤 Waiting for human approval...")


if __name__ == "__main__":
    run("1. Legit support, $50 refund",
        lambda: do_refund("C-100", 50, "support@surfnet.com", "support"))

    run("2. Attacker CLAIMS to be admin",
        lambda: do_refund("C-100", 5000, "attacker@evil.com", "admin"))

    run("3. Real admin, $1000 refund (needs human)",
        lambda: do_refund("C-100", 1000, "admin@surfnet.com", "admin"))

    run("4. Customer tries CRM write",
        lambda: do_write_crm("C-100", "notes", "pwned", "customer@ex.com", "customer"))

    run("5. Support tries to write 'role' field",
        lambda: do_write_crm("C-100", "role", "admin", "support@surfnet.com", "support"))

    print("\n" + "=" * 60)
    print("AUDIT LOG: guardian_audit.jsonl has every decision.")
    print("Open it with: cat guardian_audit.jsonl | python -m json.tool --json-lines")
    print("=" * 60)
