## countersign: how agents work in this example

1. **One ticket at a time**, in the order of `TICKETS.md`.
2. **One ticket per commit**, with `Refs #N` in the message. Only the checker closes a ticket.
3. **The oracle belongs to the checker.** `oracle/` and `ACCEPTANCE.md` are written by the checker only. The maker changes `slugify.py`, never the checks. If a check looks wrong, say so in the report, with the evidence.
4. **Reports state facts:** the `git show --stat` of each commit, the output of `python3 oracle/run.py`, and a clean `git status`.
5. **Nothing is done until it is countersigned.**
