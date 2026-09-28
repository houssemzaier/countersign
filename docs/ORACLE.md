# The checker's oracle

A countersign loop is only as good as the thing that decides "done". That thing is the **oracle**: a set of automated checks, written and owned by the checker, frozen before the work starts. The maker never edits it. This page is how to write one that converges.

## Why the checker must own it

When the maker writes or edits its own checks, three things happen, in this order: checks that cannot fail, checks that measure the code instead of the result, and fixes validated on synthetic tests instead of the delivered artifact. Every one of them looks green. Separating the maker from the oracle removes the incentive and the opportunity.

## The rules

1. **Freeze the list.** Write the acceptance list first (`countersign template ACCEPTANCE`), have the owner approve it, then review only against it. New findings go to a later backlog, unless they are factual errors.
2. **Every check proves it can fail.** Give each check a self-test: a known-bad input that must fail, and a known-good one that must pass. Run the self-test in the oracle itself, so a broken check turns the report red.
3. **Zero items examined is a failure.** Every line of the report states how many items it looked at. A check that found nothing to examine did not check anything.
4. **Measure what users get.** The built app, the rendered file, the deployed page: not the intermediate data it came from. Look at the moment that matters (the settled frame of a scene, the page after its scripts ran) and, for anything that moves, look at consecutive frames, not a single still.
5. **No masking.** Hiding, clipping, dropping or truncating content to make a layout or a length check pass must throw instead, naming what did not fit.
6. **One issue per commit**, so a regression points at one change.
7. **Stop rule.** The same check failing twice in a row for the same reason means the design is wrong. Stop patching and describe it.

## Growing the oracle: the ratchet

Every defect the owner finds by hand becomes a new check, with a self-test built from that defect. The list grows only this way, so the loop cannot re-introduce anything the owner has already seen. Record each addition in the acceptance changelog.

## When the oracle is wrong

It will be. A maker that says "this red line is a false positive" deserves an answer on evidence:
1. Look at the artifact itself, not at the check's output.
2. If the check is wrong, fix it, and add a self-test for the case it misread, so the fix does not quietly turn it blind.
3. Run the fixed check on every existing artifact. A fix that removes one false positive and adds another is not done: a check that reads motion can be fooled by an animation, a fade or a slide as easily as by the defect it hunts.
4. Never accept a ticket with a red line "because it is a false positive". Fix the oracle first, then accept.

## A minimal layout

```
oracle/
  checks.py     pure functions: data in, one acceptance line out
  selftest.py   each check: known-bad must FAIL, known-good must PASS
  run.py        runs the checks on the real artifacts, prints the report, exits 0 only when all green
ACCEPTANCE.md   the frozen list, its rules and its changelog
```

`examples/slugify/` is a complete, runnable example.
