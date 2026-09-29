# Lessons from the field

countersign was extracted from a real project: seven tickets and more than thirty exchanges between a maker and a checker, from two different model providers, until a human signed off. These are the failures that shaped it.

1. **Reports lie by omission, not by malice.** A report said a fix was applied; the diff did not contain it. Verify every claim against `git show`, the working tree and your own run. Never on prose.
2. **A green check can be a check that cannot fail.** A layout check scored a wall of text as fine, because it could not see what it was meant to catch. Every check needs a self-test that fails on a known-bad input.
3. **Grade the artifact, not the intermediate data.** Text read from a data file was "on screen"; the render trimmed it. Measure the delivered file.
4. **Look at motion, not only stills.** A headline flickered between two font sizes from one frame to the next. Every still looked fine. Only reading consecutive frames of the delivered video caught it.
5. **Read the raw logs behind any AI grading.** When a model grades a script, compare the recorded grade with the model's raw output, and check what it was actually shown. One judge never saw half the script.
6. **Keyword rules invert.** A loop sorted the judge's fixes by keywords: it rejected real accuracy fixes that lacked the words, and applied a style fix that contained one. Let the judge label its own fixes.
7. **An uncommitted file is not done.** The build depended on a change that was never committed. Always check `git status` in the report.
8. **Upstream changes must rerun downstream steps.** A script was fixed and judged again, but the video kept narrating the old one. Check that the artifact matches the judged source.
9. **Your own oracle will be wrong.** The checker's check misread a fade-in as a broken line. Verify false positives on the artifact, fix the oracle with a self-test, and rerun it on everything.
10. **Two sessions of the same owner can race.** Read `countersign status` and the latest messages before acting on a verdict you remember.
11. **Round limits are kindness.** A ticket that takes more than four reports has a design problem, not an effort problem. Hand it to the owner.
12. **The checker is the owner's only relay.** A maker sent a plan approval straight to the owner. The checker listened only for its own messages and never saw it, and the plan waited seven hours. The maker now writes only to the checker, and the CLI enforces it.
