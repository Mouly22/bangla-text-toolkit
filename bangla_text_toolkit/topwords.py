"""
bangla_text_toolkit/stopwords.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bangla stopword list and helper functions.
"""
from __future__ import annotations

from typing import FrozenSet, List, Optional

_STOPWORDS: FrozenSet[str] = frozenset({
    # pronouns
    "আমি", "আমরা", "তুমি", "তোমরা", "আপনি", "আপনারা",
    "সে", "তারা", "এটি", "এটা", "ওটা", "ওটি",
    # conjunctions
    "এবং", "ও", "বা", "কিন্তু", "তবে", "যদি", "তাহলে",
    "অথবা", "কিংবা", "তাই", "সুতরাং",
    # demonstratives
    "এই", "ঐ", "ওই", "সেই", "যে", "যা",
    # verbs
    "হয়", "হয়েছে", "আছে", "ছিল", "করে", "যায়",
    "হবে", "হতে", "করা", "করতে", "যাচ্ছে",
    # adverbs / particles
    "এখানে", "সেখানে", "এখন", "তখন", "না", "নয়",
    "আর", "তো", "কি", "কী", "হ্যাঁ",
    # question words
    "কেন", "কোথায়", "কখন", "কে", "কার", "কাকে",
    # postpositions
    "থেকে", "দিয়ে", "জন্য", "সাথে", "মধ্যে",
    "উপর", "নিচে", "পাশে", "কাছে",
    # other
    "একটি", "একটা", "কোনো", "কোন", "সব", "সকল",
    "আরও", "খুব", "অনেক", "একটু", "বেশি",
})


def get_stopwords() -> FrozenSet[str]:
    """Return the default Bangla stopword set."""
    return _STOPWORDS


def is_stopword(word: str, stopwords=None) -> bool:
    """Return True if *word* is in the stopword set."""
    if not isinstance(word, str):
        raise TypeError(f"word must be str, got {type(word).__name__!r}")
    sw = stopwords if stopwords is not None else _STOPWORDS
    return word in sw


def remove_stopwords(tokens, stopwords=None):
    """Filter stopwords from a token list."""
    if not isinstance(tokens, list):
        raise TypeError(f"tokens must be list, got {type(tokens).__name__!r}")
    sw = stopwords if stopwords is not None else _STOPWORDS
    return [t for t in tokens if t not in sw]
