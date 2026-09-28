"""Turns a title into a URL slug. This version is deliberately naive: it is the maker's
starting point in the example, and the oracle shows what is wrong with it."""


def slugify(title):
    return title.lower().replace(' ', '-')
