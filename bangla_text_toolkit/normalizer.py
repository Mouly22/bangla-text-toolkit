"""
normalizer.py
~~~~~~~~~~~~~
Unicode-aware normalizer for Bangla (Bengali) text.

Handles:
- NFC Unicode normalization
- Zero-width character removal (ZWJ, ZWNJ, ZWSP, BOM, soft-hyphen)
- Whitespace normalization (tabs, multiple spaces, NBSP, ideographic space)
- Bangla punctuation normalization (danda, double-danda, abbreviation sign)
- Optional Bangla <-> ASCII digit conversion
- Hasanta (virama) artifact removal
"""

from __future__ import annotations

import re
import unicodedata


# Unicode constants
_NBSP = " "  # Non-Breaking Space
_IDEOSPC = "ã"  # Ideographic Space

_ZERO_WIDTH = re.compile(
    r"[â-ââª-â®â -â¤ï»¿Â­]"
)

# Bangla digits to ASCII and back
_BANGLA_DIGIT_TABLE = str.maketrans("à§¦à§§à§¨à§©à§ªà§«à§¬à§­à§®à§¯", "0123456789")
_ASCII_DIGIT_TABLE = str.maketrans("0123456789", "à§¦à§§à§¨à§©à§ªà§«à§¬à§­à§®à§¯")

_PUNCT_MAP = str.maketrans({
    "'": "'",   # LEFT SINGLE QUOTATION MARK
    "'": "'",   # RIGHT SINGLE QUOTATION MARK
    "â": '"',   # LEFT DOUBLE QUOTATION MARK
    "â": '"',   # RIGHT DOUBLE QUOTATION MARK
    "â": "-",   # EN DASH
    "â": "-",   # EM DASH
    "à¥°": "à¥¤",  # Devanagari abbreviation sign -> danda
})

_HASANTA_SPACE = re.compile(r"à§\s")


class BanglaTextNormalizer:
    """Normalize Bangla (Bengali) Unicode text for NLP pipelines.

    Parameters
    ----------
    unicode_form : str
        Unicode normalization form: ``"NFC"`` (default), ``"NFKC"``, ``"NFD"``,
        or ``"NFKD"``.
    digit_mode : str or None
        ``"bangla"``  -- convert ASCII digits 0-9 to Bangla
        ``"ascii"``   -- convert Bangla digits to ASCII
        ``None``      -- leave digits unchanged (default)
    remove_hasanta_space : bool
        Remove hasanta followed by space (encoding artifact). Default ``True``.

    Examples
    --------
    >>> n = BanglaTextNormalizer()
    >>> n.normalize("à¦à¦®à¦¿  à¦¬à¦¾à¦à¦²à¦¾à¦¯à¦¼  à¦à¦¾à¦¨ à¦à¦¾à¦à¥¤")
    'à¦à¦®à¦¿ à¦¬à¦¾à¦à¦²à¦¾à¦¯à¦¼ à¦à¦¾à¦¨ à¦à¦¾à¦à¥¤'
    """

    def __init__(
        self,
        unicode_form: str = "NFC",
        digit_mode: str | None = None,
        remove_hasanta_space: bool = True,
    ) -> None:
        if unicode_form not in {"NFC", "NFKC", "NFD", "NFKD"}:
            raise ValueError(f"Invalid unicode_form: {unicode_form!r}")
        if digit_mode not in {None, "bangla", "ascii"}:
            raise ValueError(
                f"Invalid digit_mode: {digit_mode!r}. Use 'bangla', 'ascii', or None."
            )
        self.unicode_form = unicode_form
        self.digit_mode = digit_mode
        self.remove_hasanta_space = remove_hasanta_space

    def normalize(self, text: str) -> str:
        """Apply the full normalization pipeline to *text*."""
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")
        text = self.normalize_unicode(text)
        text = self.remove_zero_width(text)
        text = self.normalize_punctuation(text)
        if self.remove_hasanta_space:
            text = self._fix_hasanta_space(text)
        text = self.normalize_whitespace(text)
        if self.digit_mode:
            text = self.normalize_digits(text, target=self.digit_mode)
        return text

    def normalize_unicode(self, text: str) -> str:
        """Apply Unicode normalization."""
        return unicodedata.normalize(self.unicode_form, text)

    def remove_zero_width(self, text: str) -> str:
        """Remove invisible zero-width and directional control characters."""
        return _ZERO_WIDTH.sub("", text)

    def normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation variants to canonical forms."""
        return text.translate(_PUNCT_MAP)

    def normalize_whitespace(self, text: str) -> str:
        """Collapse multiple whitespace characters into a single space and strip."""
        text = text.replace(_NBSP, " ").replace(_IDEOSPC, " ").replace("\t", " ")
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    def normalize_digits(self, text: str, target: str = "ascii") -> str:
        """Convert digits between Bangla and ASCII."""
        if target == "ascii":
            return text.translate(_BANGLA_DIGIT_TABLE)
        if target == "bangla":
            return text.translate(_ASCII_DIGIT_TABLE)
        raise ValueError(f"target must be 'ascii' or 'bangla', got {target!r}")

    def _fix_hasanta_space(self, text: str) -> str:
        """Replace hasanta + space (encoding artifact) with just a space."""
        return _HASANTA_SPACE.sub(" ", text)

    def __repr__(self) -> str:
        return (
            f"BanglaTextNormalizer("
            f"unicode_form={self.unicode_form!r}, "
            f"digit_mode={self.digit_mode!r}, "
            f"remove_hasanta_space={self.remove_hasanta_space})"
        )
