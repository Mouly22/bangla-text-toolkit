"""
bangla_text_toolkit/tokenizer.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Simple rule-based tokenizer for Bangla text.
"""
from __future__ import annotations

import re
from typing import List

_SENT_BOUNDARY = re.compile(r"(?<=[।॥!?.])[\s]+")
_WORD_SPLIT = re.compile(r"\s+")


class BanglaTokenizer:
      """
          Simple rule-based tokenizer for Bangla text.

              Provides sentence and word tokenization.
                  """

    def sent_tokenize(self, text: str) -> List[str]:
              """Split text into sentences on Bangla danda, ?, !, or .

                      Raises:
                                  TypeError: If text is not a str.
                                          """
              if not isinstance(text, str):
                            raise TypeError(f"Input must be str, got {type(text).__name__!r}")
                        text = text.strip()
        if not text:
                      return []
                  parts = _SENT_BOUNDARY.split(text)
        return [p.strip() for p in parts if p.strip()]

    def word_tokenize(self, text: str) -> List[str]:
              """Split text into words on whitespace.

                      Raises:
                                  TypeError: If text is not a str.
                                          """
        if not isinstance(text, str):
                      raise TypeError(f"Input must be str, got {type(text).__name__!r}")
                  text = text.strip()
        if not text:
                      return []
                  return [w for w in _WORD_SPLIT.split(text) if w]

    def __repr__(self) -> str:
              return "BanglaTokenizer()"
