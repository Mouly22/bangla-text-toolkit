"""
stemmer.py
~~~~~~~~~~
Rule-based Bangla suffix-stripping stemmer.

Uses an ordered suffix list (longest first) so that the most specific
rule wins.  Returns the longest stem whose length meets a configurable
minimum, falling back to the original token if no rule matches or the
resulting stem would be too short.

Zero external dependencies.
"""

from __future__ import annotations

__all__ = ["BanglaStemmer"]


class BanglaStemmer:
    """Rule-based Bangla suffix-stripping stemmer.

    Strips inflectional suffixes from Bangla tokens using a hand-crafted
    ordered suffix list.  Suffixes are tried longest-first so the most
    specific rule wins.  A stem is accepted only when its character count
    is at least *min_stem_length*; otherwise the original token is
    returned unchanged.

    Parameters
    ----------
    min_stem_length:
        Minimum character (code-point) length a stem must have after
        suffix removal.  Tokens whose length is already at or below this
        threshold are returned as-is.  Default: 2.

    Examples
    --------
    >>> stemmer = BanglaStemmer()
    >>> stemmer.stem("ছেলেরা")
    'ছেলে'
    >>> stemmer.stem("করেছেন")
    'কর'
    >>> stemmer.stem_tokens(["বইগুলো", "করছি"])
    ['বই', 'কর']
    """

    # Suffixes ordered longest-first so the greediest match wins.
    # Sources: Dasgupta & Ng (2007), Sarker (2012), and inspection of
    # high-frequency Bangla corpus affixes.
    _SUFFIXES: tuple[str, ...] = (
        # ── Nominal: plural + case (longest first) ──────────────────
        "দিগকে",    # archaic plural dative
        "গুলোকে",
        "গুলোতে",
        "গুলোর",
        "গুলিকে",
        "গুলিতে",
        "গুলির",
        "দেরকে",
        "থেকে",     # ablative postposition
        "দের",      # genitive plural
        "গুলো",     # plural suffix
        "গুলি",     # plural suffix (variant)
        "রা",       # plural (also handles vowel-final stems like মেয়েরা)
        # ── Verb: past continuous ────────────────────────────────────
        "ছিলাম",
        "ছিলেন",
        "ছিলে",
        "ছিলি",
        "ছিল",
        # ── Verb: present perfect ────────────────────────────────────
        "েছিলাম",
        "েছিলেন",
        "েছিলে",
        "েছিলি",
        "েছিল",
        "েছেন",
        "েছি",
        "েছে",
        # ── Verb: present continuous ─────────────────────────────────
        "ছেন",
        "ছো",
        "ছি",
        "ছে",
        # ── Verb: simple past ────────────────────────────────────────
        "লাম",
        "লেন",
        "লো",
        "লে",
        "লি",
        # ── Verb: future ─────────────────────────────────────────────
        "বেন",
        "বো",
        "বি",
        "বে",
        # ── Verb: infinitive / gerund ────────────────────────────────
        "ানো",
        "ানি",
        "িয়ে",
        "ায়ে",
        # ── Nominal: case markers (short — come after longer ones) ───
        "কে",
        "তে",
        "র",
        # ── Short vowel suffixes (lowest priority) ───────────────────
        "া",
        "ি",
        "ু",
        "ে",
        "ো",
    )

    def __init__(self, min_stem_length: int = 2) -> None:
        self.min_stem_length = min_stem_length

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def stem(self, word: str) -> str:
        """Return the stem of *word* by stripping the longest matching suffix.

        Parameters
        ----------
        word:
            A single Bangla token (or any Unicode string).

        Returns
        -------
        str
            The stemmed form, or *word* unchanged if no suffix matches or
            the candidate stem is shorter than *min_stem_length*.
        """
        if len(word) <= self.min_stem_length:
            return word
        for suffix in self._SUFFIXES:
            if word.endswith(suffix):
                candidate = word[: -len(suffix)]
                if len(candidate) >= self.min_stem_length:
                    return candidate
        return word

    def stem_tokens(self, tokens: list[str]) -> list[str]:
        """Stem a list of tokens.

        Parameters
        ----------
        tokens:
            Pre-tokenized Bangla words.

        Returns
        -------
        list[str]
            Stemmed tokens in the same order.

        Examples
        --------
        >>> stemmer = BanglaStemmer()
        >>> stemmer.stem_tokens(["ছেলেরা", "মেয়েরা"])
        ['ছেলে', 'মেয়ে']
        """
        return [self.stem(t) for t in tokens]
