"""Runs the oracle on the maker's slugify and prints the acceptance report.
Exit code 0 only when every check is green. Run: python3 oracle/run.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import checks as C  # noqa: E402
from slugify import slugify  # noqa: E402


def main():
    results = [check(slugify) for check in C.CHECKS]
    green = sum(r['status'] == 'PASS' for r in results)
    print(f'# Acceptance: slugify\n\n**{green}/{len(results)} green**\n')
    print('| ID | Result | Items | Detail |\n|---|---|---|---|')
    for r in results:
        print(f"| {r['id']} | {r['status']} | {r['items']} | {r['detail']} |")
    for r in results:
        if r['evidence']:
            print(f"\n**{r['id']}**")
            for e in r['evidence'][:5]:
                print(f'- {e}')
    return 0 if green == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
