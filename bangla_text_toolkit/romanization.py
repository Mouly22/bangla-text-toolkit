"""
bangla_text_toolkit/romanization.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Rule-based Bangla-to-Roman transliteration (simplified National Library
at Calcutta scheme).  Covers the core Unicode Bangla block (U+0980-U+09FF).
"""
from __future__ import annotations
import re
from typing import Dict

# ---------------------------------------------------------------------------
# Transliteration tables
# ---------------------------------------------------------------------------

_VOWELS: Dict[str, str] = {
    "à¦": "a",
    "à¦": "Ä",  # Ä
    "à¦": "i",
    "à¦": "Ä«",  # Ä«
    "à¦": "u",
    "à¦": "Å«",  # Å«
    "à¦": "ri",
    "à¦": "e",
    "à¦": "ai",
    "à¦": "o",
    "à¦": "au",
}

_VOWEL_SIGNS: Dict[str, str] = {
    "à¦¾": "Ä",  # à¦¾ â Ä
    "à¦¿": "i",
    "à§": "Ä«",  # à§ â Ä«
    "à§": "u",
    "à§": "Å«",  # à§ â Å«
    "à§": "ri",
    "à§": "e",
    "à§": "ai",
    "à§": "o",
    "à§": "au",
}

_CONSONANTS: Dict[str, str] = {
    "à¦": "k",
    "à¦": "kh",
    "à¦": "g",
    "à¦": "gh",
    "à¦": "á¹",  # á¹
    "à¦": "c",
    "à¦": "ch",
    "à¦": "j",
    "à¦": "jh",
    "à¦": "Ã±",  # Ã±
    "à¦": "á¹­",  # á¹­
    "à¦ ": "á¹­h", # á¹­h
    "à¦¡": "á¸",  # á¸
    "à¦¢": "á¸h", # á¸h
    "à¦£": "á¹",  # á¹
    "à¦¤": "t",
    "à¦¥": "th",
    "à¦¦": "d",
    "à¦§": "dh",
    "à¦¨": "n",
    "à¦ª": "p",
    "à¦«": "ph",
    "à¦¬": "b",
    "à¦­": "bh",
    "à¦®": "m",
    "à¦¯": "y",
    "à¦°": "r",
    "à¦²": "l",
    "à¦¶": "Å",  # Å
    "à¦·": "á¹£",  # á¹£
    "à¦¸": "s",
    "à¦¹": "h",
    "à§": "r",
    "à§": "rh",
    "à§": "y",
    "à§": "t",
}

_HASANTA = "à§"     # virama â suppresses inherent vowel
_ANUSVARA = "à¦"    # à¦
_VISARGA = "à¦"     # à¦
_CHANDRABINDU = "à¦"  # à¦

_BANGLA_DIGITS: Dict[str, str] = {
    "à§¦": "0", "à§§": "1", "à§¨": "2", "à§©": "3",
    "à§ª": "4", "à§«": "5", "à§¬": "6", "à§­": "7",
    "à§®": "8", "à§¯": "9",
}

_TABLE: Dict[str, str] = {
    **_VOWELS,
    **_VOWEL_SIGNS,
    **_CONSONANTS,
    **_BANGLA_DIGITS,
    _ANUSVARA:     "m",
    _VISARGA:      "h",
    _CHANDRABINDU: "á¹",  # á¹
}

_KNOWN = re.compile(
    "[" + "".join(re.escape(k) for k in _TABLE) + re.escape(_HASANTA) + "]"
)


def _transliterate_char(m: re.Match) -> str:
    ch = m.group(0)
    if ch == _HASANTA:
        return ""
    return _TABLE.get(ch, ch)


class BanglaRomanizer:
    """Transliterate Bangla Unicode text to a Latin script representation.

    The scheme is a simplified variant of the National Library at Calcutta
    (NLC) romanization.

    Parameters
    ----------
    keep_unknown:
        If True (default), unknown characters are passed through unchanged.
        Set to False to strip them.
    """

    def __init__(self, keep_unknown: bool = True) -> None:
        self.keep_unknown = keep_unknown

    def romanize(self, text: str) -> str:
        """Return the romanized form of text.

        Raises
        ------
        TypeError
            If text is not a str.
        """
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__!r}")
        result = _KNOWN.sub(_transliterate_char, text)
        if not self.keep_unknown:
            result = re.sub("[à¦-à§¿]", "", result)
        return result

    def __repr__(self) -> str:
        return f"BanglaRomanizer(keep_unknown={self.keep_unknown!r})"
