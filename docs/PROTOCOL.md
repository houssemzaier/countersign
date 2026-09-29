# The countersign protocol

Version 1. Two agents and a human exchange files in one folder. No server, no network, no API key: any agent that can run a shell command can take part.

## Roles

| Role | Plays | Sends |
|---|---|---|
| `maker` | builds: an agent that writes code | `ready`, `report`, `note` |
| `checker` | verifies on evidence and countersigns: an agent that reviews | `ready`, `review`, `note` |
| `owner` | holds the gates: a human | `approval`; `countersign stop` ends the session |

## The session folder

```
<session>/
  state.json      turn, sequence, rounds per ticket, heartbeats, settings
  messages/       0001-maker-ready.md, 0002-checker-ready.md, ...
  tmp/            atomic writes and the lock
  STOP            written by `countersign stop`; its text is the owner's note
```

Keep sessions outside the repository they work on, for example `~/countersign-sessions/<project>/<session>`. Set `COUNTERSIGN_SESSION` to avoid repeating the path.

## Messages

A message is a Markdown file written once and never edited. It is written to `tmp/`, then renamed into `messages/`, so a reader never sees half a message. Its front matter:

```
---
protocol: 1
seq: 3
from: maker
to: checker
type: report
ticket: 12
round: 1
created: 2026-09-28T09:30:38
requires_owner: false
verdict:
---
<body>
```

| Type | From | Meaning |
|---|---|---|
| `ready` | maker, checker | the agent is listening |
| `report` | maker | a ticket is ready for verification; needs `--ticket` |
| `review` | checker | a verdict on a report; needs `--verdict` |
| `note` | anyone | information, no action required |
| `approval` | owner | a gate is open |

| Verdict | Meaning |
|---|---|
| `accepted` | countersigned: the checker's own run of the oracle is green for the ticket's checks, and the ticket is closed |
| `changes` | the review lists each required fix, with its evidence; the maker reports again |
| `blocked` | the owner must decide; the message is an owner gate |

## Turns and gates

- `state.json` records whose turn it is (`maker`, `checker`, `owner`, or `any` before the first message) and the session status (`running`, `waiting_owner`, `stopped`).
- **Round limit.** Each report increments the ticket's round. The report past `--max-rounds` (4 by default) becomes an owner gate: the loop cannot run forever on one ticket.
- **Owner gates.** A `blocked` review, a report past the round limit, or any message sent with `--owner` sets the turn to `owner`. `countersign approve` answers it.
- **The checker is the hub.** The maker writes only to the checker; the CLI refuses anything else. When the maker needs the owner, it sends the checker a message with `--owner`. The checker asks the owner, then relays the owner's answer with `approve`.
- **STOP.** `countersign stop` writes `STOP`. Every later `wait` exits with code 3, and every `send` is refused.

## Listening

`countersign wait --as <role>` returns the next message addressed to that role, once, in sequence order.

| Exit code | Meaning |
|---|---|
| 0 | a message was printed |
| 2 | usage error |
| 3 | STOP: the session is over |
| 4 | timeout (`--timeout` seconds); run `wait` again |

Each `wait` records the role's `lastSeen` time in `state.json`, a heartbeat the owner can read with `countersign status`.

## Notifications

`countersign new --notify '<shell command>'` stores a command that runs when both agents are ready, a ticket is accepted, an owner gate opens, or the session stops. The text arrives on stdin and in `COUNTERSIGN_MESSAGE`. `COUNTERSIGN_NOTIFY` overrides it, and `COUNTERSIGN_NOTIFY=off` silences it. A failing command never blocks the protocol.

Examples:
```bash
--notify 'curl -s -d @- https://ntfy.sh/<your-topic>'
--notify 'osascript -e "display notification \"$COUNTERSIGN_MESSAGE\" with title \"countersign\""'
--notify 'curl -s -X POST -H "Content-Type: application/json" -d "{\"text\": \"$COUNTERSIGN_MESSAGE\"}" "$SLACK_WEBHOOK_URL"'
```

## Concurrency

`state.json` is changed under a lock file created with `O_EXCL`. A lock older than 30 seconds is considered left by a killed process and is removed. Messages are immutable, so readers never need the lock.
