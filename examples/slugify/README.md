# Example: slugify

A toy project to watch a real countersign loop in about ten minutes, with two real agents.

- `slugify.py` is the maker's code, deliberately naive.
- `TICKETS.md` lists three tickets, in order.
- `ACCEPTANCE.md` is the frozen definition of done.
- `oracle/` is the checker's oracle: `run.py` prints the acceptance report, and `selftest.py` proves that every check can fail.

```bash
python3 oracle/selftest.py   # selftest: 4/4 PASS
python3 oracle/run.py        # 1/4 green: the maker has work to do
```

## Run the loop

1. **Give the example its own repository**, so that commits and `git show` mean something:
   ```bash
   cp -r examples/slugify ~/slugify-demo && cd ~/slugify-demo
   git init -q && git add -A && git commit -qm "Start: naive slugify"
   ```
2. **Create a session** (the owner):
   ```bash
   export COUNTERSIGN_SESSION=~/countersign-sessions/slugify-demo
   countersign new --notify 'osascript -e "display notification \"$COUNTERSIGN_MESSAGE\" with title \"countersign\""'
   ```
   Drop `--notify` on Linux, or use any command that reads the message on stdin.
3. **Start the checker** in a first terminal: Claude Code with the plugin installed, in `~/slugify-demo`:
   ```
   /countersign:checker ~/countersign-sessions/slugify-demo
   ```
4. **Start the maker** in a second terminal: any coding agent, in `~/slugify-demo`. Give it its role card and the session:
   ```bash
   countersign prompt maker
   ```
   Paste the card, then: "The session is `~/countersign-sessions/slugify-demo`. The tickets are in `TICKETS.md`. Start."
5. **Watch.** `countersign status` shows every message. The loop ends when the three tickets are countersigned, or when you run `countersign stop`.
