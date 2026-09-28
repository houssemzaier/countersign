# Acceptance: <project> v1

**Status:** frozen by the owner on <date>. This file is the only definition of "done" for this milestone. The checker owns it; the maker never edits it.

## Rules

- **R1. The list is frozen.** The checker reviews against it and nothing else. A new finding goes to a later backlog, unless it is a factual error, which blocks and becomes a new check.
- **R2. The machine decides.** The oracle writes the acceptance report. A report quotes it; it never replaces it with prose.
- **R3. Every check proves it can fail.** Each check has a self-test: a known-bad input that must fail and a known-good one that must pass. A check that examined 0 items fails. Every line states how many items it examined.
- **R4. Checks look at what users get.** The delivered artifact (the built app, the rendered file, the deployed page), at the moment that matters, not an intermediate step.
- **R5. No masking.** Code that hides, drops or truncates content to make a check pass must throw instead.
- **R6. One issue per commit.** Each commit's stat matches its title.
- **R7. Stop rule.** If the same check fails two rounds in a row for the same reason, stop and describe the design problem instead of patching again.

## Checks

| ID | Check | Self-test (must FAIL) |
|---|---|---|
| C1 | <what must be true, measured on the delivered artifact> | <a known-bad input> |
| C2 | ... | ... |

## Validation

The milestone is validated when the oracle's self-test passes, every check is green, and the owner has tried the result and flagged nothing. Anything the owner flags becomes a new check, and the loop runs again.

## Changelog

- **v1** (<date>): frozen.
