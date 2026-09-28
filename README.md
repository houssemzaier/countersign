# countersign

**A maker-checker loop for AI coding agents.** One agent builds. Another verifies the work on evidence and countersigns it. You hold the gates.

[![CI](https://github.com/houssemzaier/countersign/actions/workflows/ci.yml/badge.svg)](https://github.com/houssemzaier/countersign/actions/workflows/ci.yml)

## Why

Coding agents grade their own homework. When the same agent writes the code, runs the tests and writes the report, "done" means "the agent says so". The report is confident, and it is often wrong: the fix is not in the diff, the test cannot fail, the screen looks nothing like the claim.

countersign splits the work between three roles:

- the **maker** (any coding agent) builds, and reports facts: the diff, the oracle's output, a clean working tree;
- the **checker** (Claude Code with this plugin, or any agent you trust with judgment) verifies those facts against an **oracle it owns**, then countersigns, or sends the work back with evidence;
- the **owner** (you) decides what only a human should: scope, money, publishing, and whether the result is really good.

```
             report: diff, oracle lines, clean tree
   maker  ------------------------------------------>  checker
  (builds)                                           (verifies on evidence,
     ^                                                owns the oracle)
     |      review: accepted | changes | blocked          |
     +----------------------------------------------------+
                                |
                 blocked, round limit, stop: the owner decides
```

The two agents never talk directly. They exchange immutable files in one folder, through a small CLI. Nothing else is shared.

## What makes it different

- **The checker owns the oracle.** The acceptance checks are frozen before the work starts, the maker cannot edit them, and every check carries a self-test that proves it can fail.
- **A ratchet.** Every defect the owner finds by hand becomes a new check. The loop only gets stricter.
- **Any two agents, no API key.** Plain files and a CLI: the maker and the checker can come from different model providers, and interactive sessions on a subscription work as well as headless ones.
- **Human gates.** Blocked decisions, a round limit per ticket, notifications, and a STOP.
- **Extracted from real work.** Seven tickets, more than thirty exchanges between two agents from two providers, until a human signed off. [The lessons](docs/LESSONS.md) shaped every rule.

## Install

### 1. The CLI, for both agents

```bash
pipx install git+https://github.com/houssemzaier/countersign
# or: uv tool install git+https://github.com/houssemzaier/countersign
countersign --version
```

Python 3.9 or later. No dependencies.

### 2. The Claude Code plugin, for the checker

In Claude Code:

```
/plugin marketplace add houssemzaier/countersign
/plugin install countersign@countersign
```

It adds five commands:

| Command | What it does |
|---|---|
| `/countersign:start` | sets up a session in the current project: rules, notifications, the maker's handover |
| `/countersign:checker` | runs the checker's loop: listen, verify on evidence, send verdicts, listen again |
| `/countersign:oracle` | writes the frozen acceptance list and the checks, or turns a defect into a check |
| `/countersign:status` | where the session stands |
| `/countersign:stop` | ends the session for both agents |

### 3. The maker

Nothing to install beyond the CLI. Give your coding agent its role card, `countersign prompt maker`, or reference it from your project's `AGENTS.md`. It works with any agent that can run shell commands.

### Verify the installation

```bash
git clone https://github.com/houssemzaier/countersign && cd countersign
python3 -m unittest discover -s tests   # the protocol's tests
bash scripts/demo.sh                    # a whole loop in two seconds, no model needed
```

The demo plays a scripted maker and a scripted checker: a report, a review asking for changes, a second report, a countersignature, a STOP, and the owner's notifications.

## Quickstart

1. In Claude Code, in your project: `/countersign:start`. It creates the session, adds the rules to `AGENTS.md`, and prints the text to paste into your maker agent.
2. If the project has no acceptance list yet: `/countersign:oracle`. Nothing can be countersigned without one.
3. In a second terminal, start your maker agent and paste its handover.
4. In Claude Code: `/countersign:checker`. Then watch, with `/countersign:status`, or from the notifications.

To try it on a toy project first, follow [`examples/slugify`](examples/slugify/README.md): three tickets, an oracle, about ten minutes.

## The CLI

| Command | Who | What it does |
|---|---|---|
| `countersign new [SESSION] [--max-rounds N] [--notify CMD]` | owner | create a session |
| `countersign send [SESSION] --as ROLE --to ROLE --type TYPE [--ticket ID] [--verdict V] [--file F]` | any | send a message (body from `--file` or stdin) |
| `countersign wait [SESSION] --as ROLE [--timeout S]` | maker, checker | block until a message (exit 0), STOP (3) or timeout (4) |
| `countersign status [SESSION]` | anyone | turn, rounds, heartbeats, latest messages |
| `countersign approve [SESSION] --to ROLE [--note TEXT]` | owner | open a gate |
| `countersign stop [SESSION] [--note TEXT]` | owner | end the session |
| `countersign prompt maker\|checker\|owner` | anyone | print a role card |
| `countersign template AGENTS\|ACCEPTANCE\|TICKET` | anyone | print a project template |

`SESSION` defaults to `$COUNTERSIGN_SESSION`. The full format is in [docs/PROTOCOL.md](docs/PROTOCOL.md).

## FAQ

**Which agent should be the maker, and which the checker?** Give the checker role to the model you trust most with judgment: architecture, verification, debugging, writing acceptance criteria. Give the maker role to the one that is fast and cheap at implementation. The protocol does not care; swap them when models change.

**Can both roles be Claude?** Yes, in two separate sessions. Two different model providers catch more, because their blind spots differ.

**Do I need API keys?** No. The agents run however you already run them, and they only exchange files.

**Several machines?** A session is a local folder. Install the CLI and the plugin the same way on each machine, and run each session where its two agents run.

**Why not a single agent with a test suite?** Because the same agent writes the code, the tests and the verdict. A separate checker with its own oracle is the difference between "the tests pass" and "the tests could have failed, and did not".

## Learn more

- [The protocol](docs/PROTOCOL.md): messages, verdicts, gates, exit codes, notifications.
- [The checker's oracle](docs/ORACLE.md): how to write acceptance checks that converge.
- [The pattern](docs/PATTERN.md): maker-checker, evaluator-optimizer, and when not to use this.
- [Lessons from the field](docs/LESSONS.md): the failures that shaped each rule.

## License

MIT. See [LICENSE](LICENSE).
