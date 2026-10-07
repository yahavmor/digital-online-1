"""Language helpers: normalisation, Hebrew prefix handling, lexicon matching."""
from __future__ import annotations

import re

PUNCT = re.compile(r"[^\w֐-׿%$₪']+", re.UNICODE)
HE_PREFIXES = "והבלשמכ"
NUMBER_RE = re.compile(r"\d|%|\$|₪")
HE_NUMBER_WORDS = {"אחד", "אחת", "שניים", "שתיים", "שלוש", "שלושה", "ארבע", "ארבעה", "חמש", "חמישה",
                   "עשר", "עשרה", "מאה", "אלף", "אלפים", "מיליון", "מיליונים", "מיליארד", "חצי", "פי"}
EN_NUMBER_WORDS = {"one", "two", "three", "four", "five", "ten", "hundred", "thousand", "million",
                   "billion", "half", "double", "triple", "percent"}


def norm(word: str) -> str:
    return PUNCT.sub("", word).lower()


def variants(word: str) -> list[str]:
    """A normalised word plus its forms with 1–2 Hebrew prefix letters stripped (ו+ה+...)."""
    w = norm(word)
    out = [w]
    for _ in range(2):
        if len(w) > 3 and w[0] in HE_PREFIXES:
            w = w[1:]
            out.append(w)
        else:
            break
    return out


def in_lexicon(word: str, lexicon: set[str]) -> bool:
    return any(v in lexicon for v in variants(word))


def lexicon(kw: dict, lang: str, key: str) -> set[str]:
    pack = kw.get(lang) or {}
    return {norm(x) for x in pack.get(key, []) if " " not in str(x)}


def phrases(kw: dict, lang: str, key: str) -> list[list[str]]:
    pack = kw.get(lang) or {}
    return [[norm(t) for t in str(x).split()] for x in pack.get(key, [])]


def is_number(word: str) -> bool:
    return bool(NUMBER_RE.search(word)) or any(v in HE_NUMBER_WORDS | EN_NUMBER_WORDS for v in variants(word))


def contains_phrase(tokens: list[str], phrase: list[str]) -> bool:
    if not phrase:
        return False
    n = len(phrase)
    for i in range(len(tokens) - n + 1):
        if all(tokens[i + j] == phrase[j] or tokens[i + j].endswith(phrase[j]) and len(phrase[j]) > 2
               for j in range(n)):
            return True
    return False
