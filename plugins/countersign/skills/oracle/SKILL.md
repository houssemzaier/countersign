---
name: oracle
description: Write or extend the checker-owned oracle of a countersign project, the frozen acceptance list and the automated checks that decide when a ticket is done. Use when the user wants to define "done", write acceptance checks, turn a defect they found into a check, or fix a check that gave a false positive.
argument-hint: "[what to add or fix]"
---

# countersign: the checker's oracle

The oracle decides "done". The checker writes it and owns it; the maker never edits it. Work with the user, and keep these rules.

## Rules

1. **Freeze the list.** Start from `countersign template ACCEPTANCE`. Write checks as measurable outcomes, get the user's approval, then review only against the list. New findings go to a later backlog, unless they are factual errors.
2. **Every check proves it can fail.** Each check has a self-test with a known-bad input that must fail and a known-good input that must pass. The self-test runs as part of the oracle, so a broken check turns the report red.
3. **Zero items examined fails.** Every report line states how many items it examined.
4. **Measure what users get**: the delivered artifact, at the moment that matters. For anything that moves, read consecutive frames, not one still.
5. **No masking.** Code that hides, clips, drops or truncates content to pass must throw instead.
6. **Protect it.** Add the countersign rules to `AGENTS.md` (`countersign template AGENTS`), and, if the project has git hooks, a pre-commit guard that refuses changes to the oracle unless the checker commits them.

## Layout

```
oracle/
  checks.py     pure functions: data in, one acceptance line out (id, status, items examined, evidence)
  selftest.py   each check: the known-bad input must FAIL, the known-good one must PASS
  run.py        runs every check on the real artifacts, prints the report, exits 0 only when all green
ACCEPTANCE.md   the frozen list, its rules, and its changelog
```

Adapt it to the project's language and tools. The countersign repository has a complete, runnable example in `examples/slugify/`.

## What the user asked: $ARGUMENTS

- **A new oracle:** draft `ACCEPTANCE.md` with the user, then the checks, the self-tests and the runner. Run the self-test and the runner, and show both outputs.
- **A defect the user found:** add a check that fails on that defect, with a self-test built from it. Record it in the acceptance changelog. Run it on every existing artifact: it must fail where the defect is, and only there.
- **A false positive:** look at the artifact itself first. If the check is wrong, fix it, add a self-test for the case it misread, and rerun it on every artifact: a fix that removes one false positive and adds another is not done.
