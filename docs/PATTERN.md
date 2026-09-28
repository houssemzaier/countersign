# The pattern behind countersign

countersign is not a new idea. It is a small, strict combination of well-known patterns, applied to AI coding agents.

| Pattern | Where it comes from | What it contributes here |
|---|---|---|
| **Maker-checker** (the four-eyes principle) | banking and operations: the person who makes a change is never the one who approves it | the maker builds, a different agent countersigns |
| **Evaluator-optimizer** | "Building effective agents" (Anthropic, 2024): one model produces, another evaluates, in a loop | report, review, report again until accepted |
| **Mailbox, or blackboard** | the actor model and blackboard architectures: independent workers communicate through a shared store | immutable message files in one folder; nothing else is shared |
| **Human in the loop** | any system where some decisions must stay human | owner gates, a round limit, and a STOP |
| **Test oracle, owned by the verifier** | software testing: the oracle is what decides whether an output is correct | the checker writes the acceptance checks, and each one proves it can fail |

## What countersign adds on top

- **The oracle is the checker's.** Most maker-checker setups let the maker run and even edit the tests. Here the maker cannot touch them, and each check carries a self-test that proves it can fail.
- **The ratchet.** Every defect the owner finds becomes a check. The loop can only get stricter.
- **Vendor-neutral and key-free.** Two different tools, even from different model providers, cooperate through plain files. Interactive sessions on a subscription work as well as headless ones.

## A note on the word "handoff"

In some agent frameworks, a handoff means passing the conversation to another agent. That is a different thing: here, both agents keep their own sessions, and they exchange evidence and verdicts.

## When to use it, and when not

Use it when the result must be proven correct and a wrong "done" is expensive: production code, generated media that real users will see, data pipelines, anything with acceptance criteria.

Do not use it for exploratory prototyping, one-off scripts, or personal chores where "good enough" is fine. A single agent is faster there, and an always-on personal agent is a better fit for recurring, low-stakes tasks.

## Choosing who plays which role

Give the checker role to the model you trust most with judgment: architecture, verification, debugging, writing the acceptance list. Give the maker role to the model that is fast and cheap at implementation. The protocol does not care which is which; swap them when the models change.
