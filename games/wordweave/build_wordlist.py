#!/usr/bin/env python3
"""
Filters wordlist_raw.txt (a raw system dictionary dump, one word per line,
mixed case, includes possessives/acronyms/proper nouns) down to a clean
lowercase word list suitable for the WordWeave game, and writes it as a
JSON array to wordlist.json next to this script.

Build-only dependency: nltk (`pip install nltk`), used for its WordNet
lemmatizer - see inflection_base() below. Not needed at runtime; the
game itself only reads the wordlist.json this script produces.

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

import nltk
from nltk.stem import WordNetLemmatizer

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

# No inflected/derived forms allowed - plurals ("offs"->off), past tense
# ("scored"->score), -ing ("scoring"->score), comparative/superlative
# ("faster"/"fastest"->fast), adverbs ("quickly"->quick) - keeping only
# what a text-mining pipeline would treat as distinct root vocabulary.
#
# For -s/-ed/-ing/-er/-est we used to do this by pure regex (strip the
# suffix, undo e-drop/consonant-doubling, check if the result is a word
# already in the list) - but that has false positives: words that only
# coincidentally end in a shorter real word plus a suffix without
# actually being derived from it (pass/mass/bother/archer aren't
# pas/mas/both/arch + a suffix). We now require NLTK's WordNet
# lemmatizer to independently agree with the regex-derived candidate
# (see inflection_base()) before treating a word as derived, which uses
# WordNet's real morphological exception data instead of blind regex
# and eliminates that whole class of false positive without a manual
# exception list for those five suffixes.
#
# WordNet has no adverb-from-adjective derivation data, though, so -ly
# still relies on the regex-only check - keeping a manual exception list
# for it alone.
INFLECTION_KEEP_EXCEPTIONS = {
    # -ly false positives (not "adjective + ly")
    "ally", "belly", "bully", "chilly", "family", "fully", "gully",
    "holly", "jelly", "jolly", "lily", "only", "rally", "silly", "sly",
    "supply", "tally", "ugly", "apply", "imply", "reply", "early",
    "curly", "burly", "wooly",
    # -s false positives: WordNet's own lemmatizer coincidentally agrees
    # with the naive "strip the trailing s" regex candidate for these
    # (e.g. pos="n" reduces "pass" -> "pas", pos="v" reduces "buss" ->
    # "bus", pos="n" reduces "has" -> "ha") even though none of them are
    # actually derived from that shorter word - found by testing every
    # short-base candidate from the earlier regex-only pass by hand.
    "ass", "buss", "has", "pass", "puss",
    # -ing false positive: WordNet's verb lemmatizer treats "evening" as
    # a gerund of "even" (a real but minor sense), but "evening" (time
    # of day) is a common, distinct noun that shouldn't be dropped.
    "evening",
}

try:
    WordNetLemmatizer().lemmatize("cats", pos="n")
except LookupError:
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)

_LEMMATIZER = WordNetLemmatizer()

# Which WordNet POS tags are worth trying per suffix, in priority order.
_SUFFIX_POS = {
    "s": ("v", "n"),
    "ed": ("v",),
    "ing": ("v",),
    "er_est": ("a", "n"),
}


def _wordnet_confirms(word, candidate, pos_list):
    return any(_LEMMATIZER.lemmatize(word, pos=pos) == candidate for pos in pos_list)


def _candidates_s(word):
    if not word.endswith("s") or len(word) < 3:
        return
    if word.endswith("ies") and len(word) > 4:
        yield word[:-3] + "y"
    if word.endswith("es") and len(word) > 3:
        base = word[:-2]
        if base[-1] in "sxz" or base.endswith("ch") or base.endswith("sh"):
            yield base
    yield word[:-1]


def _candidates_ed(word):
    if word.endswith("ied") and len(word) > 4:
        yield word[:-3] + "y"
        return
    if not word.endswith("ed") or len(word) <= 4:
        return
    stem = word[:-2]
    yield stem            # walked -> walk
    yield stem + "e"       # scored -> score (stem "scor" + e)
    if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
        yield stem[:-1]    # stopped -> stop


def _candidates_ing(word):
    if not word.endswith("ing") or len(word) <= 5:
        return
    stem = word[:-3]
    yield stem              # walking -> walk
    yield stem + "e"        # scoring -> score
    if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
        yield stem[:-1]      # stopping -> stop


def _candidates_er_est(word):
    if word.endswith("est") and len(word) > 5:
        stem = word[:-3]
        yield stem            # fastest -> fast
        yield stem + "e"       # latest -> late
        if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            yield stem[:-1]     # biggest -> big
    if word.endswith("er") and len(word) > 4:
        stem = word[:-2]
        yield stem             # faster -> fast
        yield stem + "e"        # later -> late
        if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            yield stem[:-1]      # bigger -> big


def _candidates_ly(word):
    if word.endswith("ily") and len(word) > 5:
        yield word[:-3] + "y"   # happily -> happy
    if word.endswith("ly") and len(word) > 4:
        yield word[:-2]         # quickly -> quick, safely -> safe


# WordNet-confirmed suffixes (regex candidate must match a real lemma)
WORDNET_CHECKED_FUNCS = [
    ("s", _candidates_s), ("ed", _candidates_ed), ("ing", _candidates_ing),
    ("er_est", _candidates_er_est),
]


def inflection_base(word, words):
    """Returns the base word this is an inflected/derived form of, or None."""
    if word in INFLECTION_KEEP_EXCEPTIONS:
        return None
    for suffix_key, fn in WORDNET_CHECKED_FUNCS:
        pos_list = _SUFFIX_POS[suffix_key]
        for base in fn(word):
            if base != word and base in words and _wordnet_confirms(word, base, pos_list):
                return base
    # WordNet has no adverb-from-adjective data, so -ly stays regex-only
    for base in _candidates_ly(word):
        if base != word and base in words:
            return base
    return None


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

    derived = {w for w in words if inflection_base(w, words)}
    print(f"Dropping {len(derived)} inflected/derived forms (plurals, -ed, -ing, -er/-est, -ly)")
    words -= derived

    word_list = sorted(words)
    OUT_PATH.write_text(json.dumps(word_list, separators=(",", ":")))
    by_len = {}
    for w in word_list:
        by_len[len(w)] = by_len.get(len(w), 0) + 1
    print(f"Wrote {len(word_list)} words to {OUT_PATH}")
    print("By length:", {k: by_len[k] for k in sorted(by_len)})
