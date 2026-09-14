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

if __name__ == "__main__":
    words = set()
    for line in RAW_PATH.read_text().splitlines():
        w = line.strip()
        if not w:
            continue
        if LOWER_ALPHA.match(w) and MIN_LEN <= len(w) <= MAX_LEN:
            words.add(w)
    words |= ONE_LETTER_WORDS

    word_list = sorted(words)
    OUT_PATH.write_text(json.dumps(word_list, separators=(",", ":")))
    by_len = {}
    for w in word_list:
        by_len[len(w)] = by_len.get(len(w), 0) + 1
    print(f"Wrote {len(word_list)} words to {OUT_PATH}")
    print("By length:", {k: by_len[k] for k in sorted(by_len)})
