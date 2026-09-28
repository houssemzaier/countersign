"""The checker's oracle for the slugify example: each check is a pure function that takes a
slugify callable and returns one acceptance line. The checker owns this file."""
import re

TITLES = [
    'Hello World', 'Hello,  World!', '  Leading and trailing  ', 'Café crème', 'Ça va à Noël',
    'naïve résumé', 'C++ & Rust: 2 languages', 'already-a-slug', 'Multiple---dashes', 'Émile Zola',
]
ACCENTED = {'Café crème': 'cafe-creme', 'Ça va à Noël': 'ca-va-a-noel', 'naïve résumé': 'naive-resume',
            'Émile Zola': 'emile-zola'}


def line(cid, failures, items, detail):
    """One acceptance line. A check that examined nothing fails (R3)."""
    ok = items > 0 and not failures
    return {'id': cid, 'status': 'PASS' if ok else 'FAIL', 'items': items,
            'detail': detail if items else f'0 items examined: {detail}', 'evidence': failures}


def c1_characters(slugify, titles=TITLES):
    bad = [f'{t!r} gives {slugify(t)!r}' for t in titles if not re.fullmatch(r'[a-z0-9-]*', slugify(t))]
    return line('C1', bad, len(titles), f'{len(titles)} titles, {len(bad)} with other characters')


def c2_separators(slugify, titles=TITLES):
    bad = [f'{t!r} gives {slugify(t)!r}' for t in titles
           if '--' in slugify(t) or slugify(t).startswith('-') or slugify(t).endswith('-')]
    return line('C2', bad, len(titles), f'{len(titles)} titles, {len(bad)} with a repeated or edge dash')


def c3_accents(slugify, expected=ACCENTED):
    bad = [f'{t!r} gives {slugify(t)!r}, expected {want!r}' for t, want in expected.items() if slugify(t) != want]
    return line('C3', bad, len(expected), f'{len(expected)} accented titles, {len(bad)} wrong')


def c4_stable(slugify, titles=TITLES):
    bad = [f'{t!r}: {slugify(t)!r} then {slugify(slugify(t))!r}' for t in titles
           if slugify(slugify(t)) != slugify(t)]
    return line('C4', bad, len(titles), f'{len(titles)} titles, {len(bad)} change when slugified twice')


CHECKS = [c1_characters, c2_separators, c3_accents, c4_stable]
