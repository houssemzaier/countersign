---
name: start
description: Set up a countersign maker-checker session for the current project, so that another coding agent builds and Claude verifies. Use when the user wants to start a countersign session, a maker-checker loop, or "another agent codes and you review".
argument-hint: "[session name]"
---

# countersign: start a session in this project

Set up a maker-checker loop for the current repository, step by step, and tell the user what each step did.

1. **The CLI.** Check `command -v countersign`. If it is missing, give the user the install command, `pipx install git+https://github.com/houssemzaier/countersign` (or the `uv tool install` equivalent), and stop.
2. **The session folder.** Use `~/countersign-sessions/<repository name>/<session name>`, the session name being `$ARGUMENTS` or today's date. Sessions stay outside the repository.
3. **Notifications.** Ask the user how the owner wants to be pinged: none, a macOS notification, ntfy, Slack, or their own command. Then create the session:
   `countersign new <session> --notify '<command>'` (omit `--notify` for none). A macOS notification is `osascript -e "display notification \"$COUNTERSIGN_MESSAGE\" with title \"countersign\""`.
4. **The rules.** Make sure the project's `AGENTS.md` (or `CLAUDE.md` if that is what the project uses) contains the countersign rules. Print them with `countersign template AGENTS`, replace `ORACLE_PATH` with the project's oracle folder, show the user the block, and add it once they agree.
5. **The oracle.** Look for a frozen acceptance list and the checker's oracle. If they are missing, say so: the loop has nothing to countersign against. Offer `/countersign:oracle` to write them with the user.
6. **The tickets.** Ask where the maker takes its tickets from: an issue tracker, a `TICKETS.md`, or a list the user gives now. Tickets state outcomes that the oracle can measure (`countersign template TICKET`).
7. **The maker's handover.** Print the text the user pastes into the maker agent (any coding agent, in its own terminal):
   - the output of `countersign prompt maker`;
   - the session folder;
   - where the tickets are;
   - "Start with the first ticket."
8. **The checker.** Offer to start listening now with `/countersign:checker <session>`.
