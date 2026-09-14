#!/usr/bin/env python3
"""
Filters wordlist_raw.txt (a raw system dictionary dump, one word per line,
mixed case, includes possessives/acronyms/proper nouns) down to a clean
lowercase word list suitable for the Snowball game, and writes it as a
JSON array to wordlist.json next to this script.

Filtering rules:
  - keep only entries that are purely a-z (drops possessives like "AA's",
    acronyms like "ABC", and proper nouns, which are capitalized in the
    source list - lowercase-only entries are the common-noun/verb/adj
    vocabulary we want)
  - length 2-8 letters, EXCEPT a hardcoded allow-list of real 1-letter
    English words ("a", "i", "o") - the raw list contains every letter
    a-z as a standalone "word" (useful for spellcheck, not for us), so
    single letters need an explicit allow-list rather than a blanket
    length>=1 filter
"""
import json
import re
from pathlib import Path

RAW_PATH = Path(__file__).parent / "wordlist_raw.txt"
OUT_PATH = Path(__file__).parent / "wordlist.json"

MIN_LEN = 2
MAX_LEN = 8
ONE_LETTER_WORDS = {"a", "i", "o"}

LOWER_ALPHA = re.compile(r"^[a-z]+$")

# The system dictionary this is built from is a spellcheck word list, not a
# word-game dictionary - it includes lowercase unit/organization
# abbreviations ("kg", "hp", "cs", "rpm") that spellcheckers accept but
# aren't real words for a word-building game. Strip the ones spotted by
# manual review of the short (most-frequently-hit) words, plus every
# Roman numeral string, which the same dictionary also includes verbatim.
EXCLUDE_WORDS = {
    # 2-letter abbreviations / units / initialisms
    "ca", "cc", "cf", "ch", "cm", "cs", "ct", "cu", "dd", "dz", "ea", "es",
    "fl", "fr", "ft", "gm", "gr", "gs", "hp", "hr", "ht", "kc", "kg", "km",
    "ks", "lb", "ls", "mg", "ml", "pd", "pg", "pl", "pp", "pt", "qt", "rm",
    "rs", "sq", "ts", "vi", "wk", "wt", "yd", "yr",
    # 3-letter abbreviations / units / initialisms
    "adj", "adv", "amt", "avg", "bpm", "dds", "doz", "dpi", "fwd", "ftp",
    "gov", "hgt", "hrs", "hwy", "inc", "ind", "int", "lbs", "mfg", "mfr",
    "obj", "pct", "pkg", "rpm", "rps", "rte", "tbs", "tel", "tsp", "var",
    "yrs",
}


def roman_numerals(max_value=200):
    vals = [
        (1000, "m"), (900, "cm"), (500, "d"), (400, "cd"),
        (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
        (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
    ]
    out = set()
    for n in range(1, max_value + 1):
        s, rem = "", n
        for v, sym in vals:
            while rem >= v:
                s += sym
                rem -= v
        out.add(s)
    return out


EXCLUDE_WORDS |= roman_numerals()
EXCLUDE_WORDS -= ONE_LETTER_WORDS  # "i" is both a pronoun and roman numeral 1 - keep it

if __name__ == "__main__":
    words = set()
    for line in RAW_PATH.read_text().splitlines():
        w = line.strip()
        if not w:
            continue
        if LOWER_ALPHA.match(w) and MIN_LEN <= len(w) <= MAX_LEN:
            words.add(w)
    words |= ONE_LETTER_WORDS
    words -= EXCLUDE_WORDS

    word_list = sorted(words)
    OUT_PATH.write_text(json.dumps(word_list, separators=(",", ":")))
    by_len = {}
    for w in word_list:
        by_len[len(w)] = by_len.get(len(w), 0) + 1
    print(f"Wrote {len(word_list)} words to {OUT_PATH}")
    print("By length:", {k: by_len[k] for k in sorted(by_len)})
