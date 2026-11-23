# SurfNet Lifeguard

Runtime security for AI agents. Every privileged action passes through
a deterministic policy engine — logged, verified, blockable.

Built as part of a 12-week AI Security Engineering study at SurfNet Technologies.

## Architecture

Tide (the AI agent) and Guardian (the security agent) run as **separate
processes**. Tide can only perform privileged actions after Guardian
approves. A compromised Tide cannot reach Guardian's memory, files, or
decision logic.

See `docs/adr/` for the decisions that shaped this.

## Quick start

```bash
cd week1
python run_demo.py

Roadmap

Week	Feature	OWASP LLM Top 10 addressed
1	Action gate + audit log + process isolation ✅	LLM06, LLM07, LLM08
2	Input firewall (screen_prompt) + LLM gateway	+ LLM01
3	MCP-native proxy	(tool-layer defense)
4	RAG poisoning defense	LLM03
5	PII redaction	LLM06
6	OAuth on-behalf-of for agents	LLM08
7	Output validation	LLM02
8	CI/CD red-team integration	LLM01
9	Semantic rate-limiting	LLM10
10	Interpretability-based deception detection	LLM09
11	SOC2 / EU AI Act audit-ready logs	(governance)
12	Public CVEs + portfolio	(authority)

License
Proprietary — SurfNet Technologies.
