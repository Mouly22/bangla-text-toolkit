"""
bangla_text_toolkit/pipeline.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Composable text-processing pipeline for Bangla text.
"""
from __future__ import annotations

from typing import Callable, List

from .normalizer import BanglaTextNormalizer


class BanglaTextPipeline:
    """
    A composable pipeline that applies a sequence of callable steps
    to a text string in order.

    Usage::

        pipe = BanglaTextPipeline()
        pipe.add_step(BanglaTextNormalizer().normalize)
        result = pipe.run(" \u0986\u09ae\u09bf ")
        # '\u0986\u09ae\u09bf'

    Or use the convenience constructor::

        pipe = BanglaTextPipeline.default()
        result = pipe.run(text)
    """

    def __init__(self) -> None:
        self._steps: List[Callable[[str], str]] = []

    def add_step(self, fn: Callable[[str], str]) -> "BanglaTextPipeline":
        """Append a processing step. Returns *self* for method chaining."""
        if not callable(fn):
            raise TypeError(
                f"Step must be callable, got {type(fn).__name__!r}"
            )
        self._steps.append(fn)
        return self

    def run(self, text: str) -> str:
        """Apply all steps in order and return the final string."""
        if not isinstance(text, str):
            raise TypeError(
                f"Input must be str, got {type(text).__name__!r}"
            )
        for step in self._steps:
            text = step(text)
        return text

    def __len__(self) -> int:
        return len(self._steps)

    def __repr__(self) -> str:
        return f"BanglaTextPipeline(steps={len(self._steps)})"

    @classmethod
    def default(cls) -> "BanglaTextPipeline":
        """Return a pipeline pre-loaded with BanglaTextNormalizer.normalize."""
        pipe = cls()
        pipe.add_step(BanglaTextNormalizer().normalize)
        return pipe
