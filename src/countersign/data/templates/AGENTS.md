## countersign: how agents work in this repository

This project runs a maker-checker loop (https://github.com/houssemzaier/countersign). One agent, the maker, builds; another, the checker, verifies on evidence and countersigns; a human, the owner, holds the gates.

1. **One ticket at a time.** The maker takes the first open ticket in the owner's order, and works on nothing else.
2. **One ticket per commit.** Each commit references its ticket (`Refs #N`), never `Closes`: only the checker closes a ticket, after verifying it.
3. **The oracle belongs to the checker.** `ORACLE_PATH` and `ACCEPTANCE.md` are written by the checker only. The maker never edits them, never bypasses a guard, and never marks a check green by hand. To pass, change the code, not the checks. If a check looks wrong, say so in the report, with the evidence.
4. **Reports state facts, not opinions.** A report contains the `git show --stat` of each commit, the oracle lines of the ticket's checks, and a clean `git status`. No claim about quality, and no limitation reported without verifying it first.
5. **Nothing is done until it is countersigned.** A ticket is done when the checker's own oracle run is green for its checks and the checker has closed it.
6. **The checker is the hub.** The maker writes only to the checker. A decision for the owner goes to the checker with `--owner`, and the checker relays it.
7. **Small tickets, loud makers.**
   - A ticket is one result that one or two checks can verify.
   - After two failed attempts on the same problem, the maker stops and reports with the evidence.
   - The maker sends a heartbeat note at least every 30 minutes, never waits passively for a timeout, and reruns only what its change touches.
