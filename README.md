# bangla-text-toolkit

[![CI](https://github.com/Mouly22/bangla-text-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/Mouly22/bangla-text-toolkit/actions)
[![PyPI version](https://badge.fury.io/py/bangla-text-toolkit.svg)](https://badge.fury.io/py/bangla-text-toolkit)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Zero dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)

Zero-dependency Python library for Bangla NLP text preprocessing.

Handles the Unicode edge cases that silently break standard NLP tools on Bangla text — combining characters, matras, ZWJ/ZWNJ conjuncts, and more.

---

## The problem

Python's `\w` regex does **not** match Bangla combining characters (vowel signs / matras, Unicode category `Mc`/`Mn`). Most preprocessing tools silently corrupt Bangla text because they treat matras as noise. This library doesn't.

```python
import re

# Standard \w misses Bangla combining vowel signs
re.findall(r'\w+', 'বাংলা')   # ['ব', 'ল']  ← wrong! drops 'া', 'ং'
```

`bangla-text-toolkit` handles the full Bangla Unicode block (`U+0980–U+09FF`) correctly.

---

## Installation

```bash
pip install bangla-text-toolkit
```

---

## Quick start

```python
from bangla_text_toolkit import Pipeline

pipe = Pipeline(remove_english=True, remove_digits=True)
pipe.process("আমি  বাংলা  ভালোবাসি!!! https://example.com 😊")
# 'আমি বাংলা ভালোবাসি!!!'
```

---

## API

### `Pipeline`

Chainable preprocessing steps. All options default to the most conservative setting.

```python
from bangla_text_toolkit import Pipeline

pipe = Pipeline(
    unicode_normalize=True,      # NFC normalization (default: True)
    remove_urls=True,            # strip HTTP/WWW/FTP URLs (default: True)
    remove_html=False,           # strip HTML tags (default: False)
    remove_emojis=False,         # remove emoji (default: False)
    remove_english=False,        # remove a-z/A-Z (default: False)
    remove_digits=False,         # remove digits (default: False)
    remove_bangla_digits=True,   # also strip ০-৯ when remove_digits=True
    remove_punctuation=False,    # remove punctuation (default: False)
    keep_bangla_punctuation=True,# preserve ।/॥ (default: True)
    fix_zwj_zwnj=True,           # remove isolated ZWJ/ZWNJ (default: True)
    normalize_whitespace=True,   # collapse whitespace (default: True)
    custom_steps=[],             # extra callables: str -> str
)

# Single string
pipe.process("আমি বাংলা ভালোবাসি")

# Batch
pipe.process_batch(["আমি বাংলা", "তুমি বাংলা"])
```

### Individual functions

```python
from bangla_text_toolkit import (
    normalize_unicode,
    normalize_whitespace,
    remove_urls,
    remove_html_tags,
    remove_emojis,
    remove_english_chars,
    remove_digits,
    remove_punctuation,
    fix_zwj_zwnj,
)
```

---

## Unicode notes

| Feature | Details |
|---------|---------|
| Block | `U+0980–U+09FF` (Bangla) |
| Combining vowel signs | `U+09BE–U+09CC` (া–ৌ) |
| Hasanta (virama) | `U+09CD` (্) |
| Bangla digits | `U+09E6–U+09EF` (০–৯) |
| ZWJ conjuncts | `্` + `U+200D` = valid conjunct |
| Isolated ZWJ | Removed by `fix_zwj_zwnj` |

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
# 78 tests, 0 dependencies
```

---

## License

MIT © [Umme Abira Azmary](https://github.com/Mouly22)
