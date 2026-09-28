# Role: owner

You are the **owner** of a countersign session. Two agents work without you relaying their messages: the **maker** builds, the **checker** verifies and countersigns. You decide what they cannot: scope, money, publishing, design questions, and when a video, a screen or a feature is good enough for real users.

## Commands

- `countersign status <session>`: where the session stands, and the last messages.
- `countersign approve <session> --to maker --note "..."`: open a gate.
- `countersign stop <session> --note "..."`: end the session. Both agents stop at their next wait.

## When you are asked to decide

The session pings you, through the notify command set at `countersign new --notify`, when:
- both agents are ready;
- a ticket is countersigned;
- a review is `blocked`;
- a ticket passes the round limit;
- the session stops.

## Your last word

The oracle measures what can be measured. Watch, try or read the result yourself before you call it done. Anything you flag becomes a new check in the oracle, and the loop runs again until it is green.
