"""Proves that every check can fail (R3): each check gets a known-bad slugify that must FAIL
and a known-good one that must PASS. Run: python3 oracle/selftest.py"""
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import checks as C  # noqa: E402


def good(title):
    ascii_text = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', ascii_text.lower()).strip('-')


BAD = {
    'C1': lambda t: t.lower().replace(' ', '-'),              # keeps "," and "!"
    'C2': lambda t: re.sub(r'[^a-z0-9]', '-', good(t) + ' '),  # a trailing dash
    'C3': lambda t: re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-'),  # drops accented letters
    'C4': lambda t: good(t) + ('x' if t.endswith('x') else ''),  # "...x" grows each time
}
BAD_INPUTS = {'C4': ['box', 'Hello World']}


def main():
    rows, passed = [], 0
    for check in C.CHECKS:
        cid = check.__name__.split('_')[0].upper()
        args = (BAD_INPUTS[cid],) if cid in BAD_INPUTS else ()
        must_fail = check(BAD[cid], *args)['status'] == 'FAIL'
        must_pass = check(good)['status'] == 'PASS'
        ok = must_fail and must_pass
        passed += ok
        rows.append(f"  {'PASS' if ok else 'FAIL'}  {cid}: known-bad {'fails' if must_fail else 'PASSES (broken check)'}, "
                    f"known-good {'passes' if must_pass else 'FAILS (broken check)'}")
    print(f'selftest: {passed}/{len(C.CHECKS)} PASS')
    print('\n'.join(rows))
    return 0 if passed == len(C.CHECKS) else 1


if __name__ == '__main__':
    sys.exit(main())
