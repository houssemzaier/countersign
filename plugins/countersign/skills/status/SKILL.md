---
name: status
description: Show where a countersign session stands, whose turn it is, and the latest messages between the maker and the checker.
argument-hint: "[session folder]"
---

# countersign: session status

Run `countersign status <session> --last 12`, the session being `$ARGUMENTS` or `$COUNTERSIGN_SESSION`. Then tell the user, in a few lines:
- whose turn it is, and whether the owner has a decision to make (`waiting_owner`);
- which tickets are countersigned, and which one is in progress, with its round;
- when each agent last listened (`last seen`), to spot one that went silent.
