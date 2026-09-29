# Changelog

## Unreleased

- **The checker is the hub.** The maker writes only to the checker, and the CLI refuses anything else. A maker that needs the owner sends the checker a message with `--owner`, and the checker asks the owner and relays the answer with `approve`. See lesson 12.
- **Small tickets, loud makers.** The maker card, the checker card and the `AGENTS.md` template now set the discipline:
  - a ticket is one checkable result;
  - the maker reports after two failed attempts, and sends a heartbeat at least every 30 minutes;
  - no passive waits on timeouts, and no full reruns;
  - the checker splits big tickets and chases a silent maker.

  See lesson 13.

## 0.1.0 (2026-09-28)

First release.

- `countersign` CLI: `new`, `send`, `wait`, `status`, `approve`, `stop`, `prompt`, `template`. Protocol version 1: immutable message files, atomic writes, a state lock, a round limit per ticket, owner gates, STOP, and a notify command.
- Role cards for the maker, the checker and the owner.
- Templates: the `AGENTS.md` rules, a frozen acceptance list, a ticket.
- Claude Code plugin with five commands: `start`, `checker`, `oracle`, `status`, `stop`.
- A runnable example (`examples/slugify`) with a checker-owned oracle and its self-test.
- A scripted, model-free demo of a whole loop.
