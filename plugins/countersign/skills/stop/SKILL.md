---
name: stop
description: Stop a countersign session as its owner, so that both the maker and the checker stop at their next wait.
argument-hint: "[session folder] [note]"
---

# countersign: stop the session

Stopping ends the loop for both agents. Confirm with the user first, unless they asked for it in these words.

1. The session is the first word of `$ARGUMENTS`, or `$COUNTERSIGN_SESSION`.
2. Run `countersign stop <session> --note "<the user's reason, or: stopped by the owner>"`.
3. Run `countersign status <session>` and tell the user the final state: the tickets countersigned, and any ticket still open.
