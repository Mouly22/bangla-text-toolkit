"""
bangla_text_toolkit/sequence_labeler.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Rule-based sequence labeler for pre-tokenised Bangla text.

Assigns a string label to each token using an ordered list of (regex, label)
rules.  The first matching rule wins; unmatched tokens receive the default
label (``"WORD"``).

Built-in rules handle the most common structural categories:

* ``NUM``   — tokens that are entirely Bangla (০–৯) or ASCII (0–9) digits.
* ``PUNCT`` — tokens that consist only of punctuation characters.
* ``STOP``  — tokens found in the built-in Bangla stopword list.

Custom rules can be prepended (high priority) or appended (lower priority).
All custom rules still run before the built-in NUM / PUNCT / STOP checks.

Example::

    from bangla_text_toolkit.tokenizer import BanglaTokenizer
    from bangla_text_toolkit.sequence_labeler import BanglaSequenceLabeler

    tok = BanglaTokenizer()
    tokens = tok.tokenize("আমি ১২৩ বাংলায় গান গাই।")
    labeler = BanglaSequenceLabeler()
    print(labeler.label(tokens))
    # [('আমি', 'STOP'), ('১২৩', 'NUM'), ('বাংলায়', 'STOP'),
    #  ('গান', 'WORD'), ('গাই', 'WORD'), ('।', 'PUNCT')]
"""

from __future__ import annotations

import re

from .stopwords import get_stopwords as _get_stopwords

_STOPWORDS = _get_stopwords()


class BanglaSequenceLabeler:
    """Rule-based sequence labeler for pre-tokenised Bangla text.

    Parameters
    ----------
    default_label:
        Label returned when no rule matches.  Defaults to ``"WORD"``.
    use_stopwords:
        If ``True`` (default), tokens in the built-in Bangla stopword list
        receive the label ``"STOP"`` before falling through to
        *default_label*.
    """

    #: Tokens consisting entirely of Bangla (০–৯) or ASCII (0–9) digits.
    _RE_NUM: re.Pattern[str] = re.compile(r"^[০১২৩৪৫৬৭৮৯0-9]+$")

    #: Tokens that consist only of punctuation characters.
    _RE_PUNCT: re.Pattern[str] = re.compile(
        r"^[।॥,.;:!?()\[\]{}\"\'\-–—…·৷]+$"
    )

    def __init__(
        self,
        default_label: str = "WORD",
        use_stopwords: bool = True,
    ) -> None:
        self.default_label = default_label
        self._use_stopwords = use_stopwords
        # Ordered list of (compiled_pattern, label); checked before built-ins.
        # add_rule() prepends (highest priority); append_rule() appends.
        self._rules: list[tuple[re.Pattern[str], str]] = []

    # ------------------------------------------------------------------
    # Rule management
    # ------------------------------------------------------------------

    def add_rule(self, pattern: str, label: str) -> "BanglaSequenceLabeler":
        """Prepend a custom rule so it takes highest priority.

        Parameters
        ----------
        pattern:
            Regular-expression string matched against the full token via
            ``re.fullmatch``.
        label:
            The label to assign when *pattern* matches.

        Returns
        -------
        self
        """
        self._rules.insert(0, (re.compile(pattern), label))
        return self

    def append_rule(self, pattern: str, label: str) -> "BanglaSequenceLabeler":
        """Append a custom rule at the lowest priority among custom rules.

        Custom rules still run before built-in NUM / PUNCT / STOP checks.

        Parameters
        ----------
        pattern:
            Regular-expression string matched against the full token via
            ``re.fullmatch``.
        label:
            The label to assign when *pattern* matches.

        Returns
        -------
        self
        """
        self._rules.append((re.compile(pattern), label))
        return self

    @property
    def rules(self) -> list[tuple[str, str]]:
        """Return a snapshot of current custom rules as ``(pattern, label)`` pairs."""
        return [(p.pattern, lbl) for p, lbl in self._rules]

    # ------------------------------------------------------------------
    # Labelling API
    # ------------------------------------------------------------------

    def label(self, tokens: list[str]) -> list[tuple[str, str]]:
        """Label each token in *tokens*.

        Parameters
        ----------
        tokens:
            A single pre-tokenised document (list of strings).

        Returns
        -------
        List of ``(token, label)`` pairs in the same order as *tokens*.
        """
        return [(tok, self._label_one(tok)) for tok in tokens]

    def label_corpus(
        self,
        corpus: list[list[str]],
    ) -> list[list[tuple[str, str]]]:
        """Apply :meth:`label` to every document in *corpus*.

        Parameters
        ----------
        corpus:
            List of pre-tokenised documents.

        Returns
        -------
        List of labelled documents (same length as *corpus*).
        """
        return [self.label(doc) for doc in corpus]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _label_one(self, token: str) -> str:
        """Return the label for a single *token*."""
        # Custom rules run first (prepended = highest priority).
        for pattern, lbl in self._rules:
            if pattern.fullmatch(token):
                return lbl
        # Built-in: numeric tokens.
        if self._RE_NUM.fullmatch(token):
            return "NUM"
        # Built-in: punctuation-only tokens.
        if self._RE_PUNCT.fullmatch(token):
            return "PUNCT"
        # Built-in: stopwords.
        if self._use_stopwords and token in _STOPWORDS:
            return "STOP"
        return self.default_label
