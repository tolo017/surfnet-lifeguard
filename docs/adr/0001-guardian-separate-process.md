# ADR 0001: Guardian runs as a separate process

## Status
Accepted (Week 1)

## Context
Guardian enforces security policy on all privileged actions taken by Tide
(the AI agent). Tide may be compromised by prompt injection. If Guardian
runs in the same process, a compromised Tide can alter Guardian's memory,
monkey-patch its functions, or edit its files.

## Decision
Guardian runs as a separate Python process. Tide communicates with it via
JSON over stdin/stdout using `subprocess`.

## Consequences
- (+) Compromise of Tide does not compromise Guardian
- (+) Guardian can be fuzzed independently
- (+) Guardian crashes do not crash Tide (Tide fails closed)
- (−) ~10ms added latency per action
- (−) Two processes to manage
- (−) Requires fail-closed error handling in Tide's `ask_guardian()`

## Alternatives considered
1. **In-process import** — rejected: shared memory, shared globals,
   shared file handles, monkey-patchable.
2. **HTTP microservice** — deferred to Week 12: complexity unjustified
   until we have >100 agents per host.
3. **OS-level container** — future: adds ops complexity without
   meaningful isolation improvement at our scale.
