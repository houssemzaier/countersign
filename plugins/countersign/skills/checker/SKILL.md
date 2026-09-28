---
name: checker
description: Act as the checker of a countersign maker-checker session. Use when the user asks you to review, verify or countersign another agent's work through countersign, to "be the checker" or "the reviewer", or to listen for a maker's reports. You listen for reports, verify each one on evidence (diffs, your own run of the oracle, raw logs, the delivered artifact), send a verdict, and listen again until the owner stops the session.
argument-hint: "[session folder]"
---

# countersign: the checker's loop

You are the **checker**. Another agent, the **maker**, builds and reports. You verify on evidence and countersign, or send the work back. The user is the **owner** and holds the gates.

## 1. Set up

1. Check the CLI: `command -v countersign`. If it is missing, tell the user to install it with `pipx install git+https://github.com/houssemzaier/countersign` (or `uv tool install git+https://github.com/houssemzaier/countersign`), and stop.
2. The session folder is `$ARGUMENTS` when given, otherwise `$COUNTERSIGN_SESSION`. If neither is set, ask the user for it, or offer `/countersign:start`.
3. Read your role card and follow it for the whole session: `countersign prompt checker`.
4. Read the project's acceptance list and oracle (usually `ACCEPTANCE.md` and an `oracle/` folder, as `AGENTS.md` says). If there is none, offer `/countersign:oracle` before any review: without an oracle there is nothing to countersign against.

## 2. Run the loop

1. Send ready: `echo "checker ready" | countersign send <session> --as checker --to maker --type ready`.
2. Listen **in the background**: run `countersign wait <session> --as checker` with the Bash tool's `run_in_background` set, and no timeout. You are notified when it exits. Do not poll it.
3. When it exits:
   - **Exit 0, a message.** Read it.
     - A `ready` or a `note`: acknowledge it if useful, then listen again.
     - A `report`: verify it as your role card says, on evidence only. Run the oracle yourself; never trust a cached or reported result. Check `git show` for each commit, `git status` for uncommitted files, and the delivered artifact itself.
   - **Exit 3, STOP.** The owner ended the session. Tell the user, and stop.
4. Write the review to a file in your scratch area, then send it: `countersign send <session> --as checker --to maker --type review --ticket <id> --verdict <accepted|changes|blocked> --file <review.md>`.
   - `accepted`: only when the ticket's checks are green in your own run. Close the ticket in the tracker the project uses (for example `gh issue close <id> --comment "..."`).
   - `changes`: each required fix, with its evidence.
   - `blocked`: the owner must decide (scope, money, publishing, design).
5. Tell the user the verdict in one sentence.
6. Listen again (step 2).

## 3. While you wait

- Only run the oracle and change files while the maker is waiting for your verdict, never while it works.
- If the maker reports a false positive in the oracle, check the artifact itself. When the check is wrong, fix it with a self-test for the case, rerun it on everything, and say so in the review.
- If the user flags a defect by hand, add a check for it with a self-test built from that defect, and send `changes` with the new check.
- When the user asks for progress, answer from `countersign status` and the tracker.
