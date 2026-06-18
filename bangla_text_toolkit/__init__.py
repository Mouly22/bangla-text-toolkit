"""
bangla_text_toolkit
~~~~~~~~~~~~~~~~~~~
Zero-dependency Python library for Bangla (Bengali) NLP text preprocessing.

Quickstart::

    from bangla_text_toolkit import BanglaTextNormalizer

        normalizer = BanglaTextNormalizer()
            clean = normalizer.normalize("আমি  বাংলায়  গান গাই!")
                # -> "আমি বাংলায় গান গাই!"
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Umme Abira Azmary"
__email__ = "abiraazmary22@gmail.com"
__license__ = "MIT"

from .normalizer import BanglaTextNormalizer
from .stemmer import BanglaStemmer

__all__ = ["BanglaTextNormalizer", "BanglaStemmer", "__version__"]
