# Acceptance: slugify v1

**Status:** frozen by the owner. The checker owns this file and `oracle/`; the maker never edits them.

## Rules

- **R1. The list is frozen.** Review against it. A new finding goes to a later backlog, unless it is a factual error.
- **R2. The machine decides.** `python3 oracle/run.py` prints the acceptance report; reports quote it.
- **R3. Every check proves it can fail.** `python3 oracle/selftest.py` gives each check a known-bad slugify that must fail and a known-good one that must pass. A check that examined 0 titles fails.
- **R7. Stop rule.** The same check failing twice in a row for the same reason stops the loop: describe the design problem.

## Checks

| ID | Check | Self-test (must FAIL) |
|---|---|---|
| C1 | **Characters.** Every slug uses only `a-z`, `0-9` and `-`. | `"Hello, World!"` kept as `"hello,-world!"` |
| C2 | **Separators.** No repeated dash, and no dash at either end. | `"a  b"` gives `"a--b"`; `" a"` gives `"-a"` |
| C3 | **Accents.** Accented Latin letters become their base letter: `"Café crème"` gives `"cafe-creme"`. | accents dropped or kept |
| C4 | **Stable.** `slugify(slugify(t)) == slugify(t)` for every title. | a slugify that appends a dash |
