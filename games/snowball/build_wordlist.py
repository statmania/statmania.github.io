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

# No inflected/derived forms allowed - plurals ("offs"->off), past tense
# ("scored"->score), -ing ("scoring"->score), comparative/superlative
# ("faster"/"fastest"->fast), adverbs ("quickly"->quick). If stripping a
# common suffix leaves another word already in the list, drop the longer
# form as derived - keeping only what a text-mining pipeline would treat
# as the distinct root vocabulary. This mechanical rule has false
# positives - words that only coincidentally end in a shorter real word
# plus a suffix (not actually derived from it) - found by manually
# reviewing every match whose base was <=3 letters (the riskiest case,
# most likely to collide by chance). Keep those exceptions explicitly.
INFLECTION_KEEP_EXCEPTIONS = {
    # -s/-es/-ies false positives
    "ass", "buss", "has", "his", "hiss", "mass", "mess", "moss", "pass",
    "piss", "puss", "yes",
    # -ed/-ied false positives
    "bed", "bled", "bred", "fed", "fled", "led", "red", "shed", "sled",
    "sped", "ted", "wed",
    # -ing false positives
    "bring", "cling", "ding", "fling", "king", "ping", "ring", "sing",
    "sling", "spring", "sting", "string", "swing", "thing", "wing",
    # -er/-est false positives
    "her", "over", "under", "water", "after", "amber", "anger", "answer",
    "banner", "better", "bitter", "border", "butter", "center", "corner",
    "danger", "dinner", "enter", "finger", "hammer", "hunger", "ladder",
    "letter", "master", "matter", "member", "mother", "murder", "number",
    "offer", "order", "other", "paper", "power", "proper", "rather",
    "sister", "summer", "supper", "sweater", "timber", "tower", "wander",
    "weather", "wonder", "alter", "ester", "digest", "forest", "modest",
    "attest", "sheer", "sober", "super", "copper", "batter", "zipper",
    "rubber", "manner", "meter", "peter", "inner", "cover", "hover",
    "lever", "never", "river", "silver", "clover", "cancer", "corner",
    "dinner", "singer", "finger", "wither", "bother", "archer", "twitter",
    # -s false positives (word only coincidentally ends in a shorter word + s)
    "brass",
    # -ing false positives (not "verb + ing")
    "herring", "earring", "morning", "evening", "nothing", "anything",
    "everything", "something",
    # -ly false positives (not "adjective + ly")
    "ally", "belly", "bully", "chilly", "family", "fully", "gully",
    "holly", "jelly", "jolly", "lily", "only", "rally", "silly", "sly",
    "supply", "tally", "ugly", "apply", "imply", "reply", "early",
    "curly", "burly", "wooly",
}


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


CANDIDATE_FUNCS = [_candidates_s, _candidates_ed, _candidates_ing, _candidates_er_est, _candidates_ly]


def inflection_base(word, words):
    """Returns the base word this is an inflected/derived form of, or None."""
    if word in INFLECTION_KEEP_EXCEPTIONS:
        return None
    for fn in CANDIDATE_FUNCS:
        for base in fn(word):
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
