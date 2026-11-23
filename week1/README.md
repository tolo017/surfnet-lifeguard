# Week 1 — Action Gate + Audit Log + Process Isolation

## What this week covers

1. Attack surfaces & threat modeling (OWASP LLM Top 10, STRIDE)
2. Direct vs. indirect prompt injection; encoding evasion
3. MCP tool poisoning; schema validation
4. The Confused Deputy problem; principal vs. deputy
5. Recap: Tide + Guardian integrated, running end-to-end

## Files

| File | What it is |
|------|------------|
| `guardian.py` | The security agent — policy engine, separate process |
| `tide.py` | The AI agent — calls Guardian before every privileged action |
| `run_demo.py` | Runs 5 scenarios against the pair |
| `drills.py` | Python practice — 5 concepts from the lessons |
| `encoder.py` | Day 2 — Base64, ROT13, payload splitting |
| `mcp_server.py` | Day 3 — Pydantic-validated MCP server |
| `threat_model.md` | Day 1 — STRIDE table + top-3 scenarios |

## Run it

```bash
cd week1
python run_demo.py
python drills.py
cat guardian_audit.jsonl | python -m json.tool --json-lines
