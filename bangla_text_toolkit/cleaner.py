"""
bangla_text_toolkit/cleaner.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Rule-based text cleaning utilities for Bangla text.
"""
from __future__ import annotations

import re

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_HTML_RE = re.compile(r"<[^>]+>")
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"#\w+")
_EMOJI_RE = re.compile(
      "[\U00010000-\U0010ffff"
      "\U0001F600-\U0001F64F"
      "\U0001F300-\U0001F5FF"
      "\U0001F680-\U0001F6FF"
      "\U0001F1E0-\U0001F1FF"
      "\U00002600-\U000027BF"
      "]+",
      flags=re.UNICODE,
)
_PUNCT_RE = re.compile(r"[!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~।॥]+")
_DIGIT_RE = re.compile(r"[0-9০-৯]+")
_EXTRA_SPACE_RE = re.compile(r" {2,}")


class BanglaTextCleaner:
      """
          Rule-based cleaner for Bangla (and mixed) text.

              Each cleaning step can be toggled via constructor flags.

                  Usage::

                          cleaner = BanglaTextCleaner(remove_urls=True, remove_emoji=True)
                                  clean = cleaner.clean("Visit https://example.com 😊 আমি")
                                          # 'আমি'
                                              """

    def __init__(
              self,
              remove_urls: bool = True,
              remove_emails: bool = True,
              remove_html: bool = True,
              remove_mentions: bool = False,
              remove_hashtags: bool = False,
              remove_emoji: bool = False,
              remove_punctuation: bool = False,
              remove_digits: bool = False,
    ) -> None:
              self.remove_urls = remove_urls
              self.remove_emails = remove_emails
              self.remove_html = remove_html
              self.remove_mentions = remove_mentions
              self.remove_hashtags = remove_hashtags
              self.remove_emoji = remove_emoji
              self.remove_punctuation = remove_punctuation
              self.remove_digits = remove_digits

    def clean(self, text: str) -> str:
              """Apply all enabled cleaning steps and return the result."""
              if not isinstance(text, str):
                            raise TypeError(f"Input must be str, got {type(text).__name__!r}")
                        if self.remove_html:
                                      text = _HTML_RE.sub(" ", text)
                                  if self.remove_urls:
                                                text = _URL_RE.sub(" ", text)
                                            if self.remove_emails:
                                                          text = _EMAIL_RE.sub(" ", text)
                                                      if self.remove_mentions:
                                                                    text = _MENTION_RE.sub(" ", text)
                                                                if self.remove_hashtags:
                                                                              text = _HASHTAG_RE.sub(" ", text)
                                                                          if self.remove_emoji:
                                                                                        text = _EMOJI_RE.sub(" ", text)
                                                                                    if self.remove_punctuation:
                                                                                                  text = _PUNCT_RE.sub(" ", text)
                                                                                              if self.remove_digits:
                                                                                                            text = _DIGIT_RE.sub(" ", text)
                                                                                                        return _EXTRA_SPACE_RE.sub(" ", text).strip()

    def __repr__(self) -> str:
              flags = [
                  k for k, v in {
                                    "urls": self.remove_urls,
                                    "emails": self.remove_emails,
                                    "html": self.remove_html,
                                    "mentions": self.remove_mentions,
                                    "hashtags": self.remove_hashtags,
                                    "emoji": self.remove_emoji,
                                    "punctuation": self.remove_punctuation,
                                    "digits": self.remove_digits,
                  }.items() if v
    ]
        return f"BanglaTextCleaner(removing={flags!r})"
