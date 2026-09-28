# Contributing

Issues and pull requests are welcome.

## Develop

```bash
python3 -m unittest discover -s tests       # the protocol's tests
bash scripts/demo.sh                        # a whole loop, no model needed
python3 examples/slugify/oracle/selftest.py # the example oracle proves its checks can fail
claude plugin validate plugins/countersign --strict   # if you change the plugin
```

The CLI has no dependencies beyond the Python standard library, and should stay that way: both agents must be able to install it anywhere.

## Changing the protocol

The message format is versioned (`protocol: 1` in every message). A change that an older CLI cannot read needs a new version number, and an entry in `docs/PROTOCOL.md` and `CHANGELOG.md`.

## Style

- Every rule in the docs comes with the failure that motivated it.
- Tests describe behaviour in their names.
