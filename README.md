# bangla-text-toolkit

[![CI](https://github.com/Mouly22/bangla-text-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/Mouly22/bangla-text-toolkit/actions)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square)](https://pypi.org/project/bangla-text-toolkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)](pyproject.toml)

Zero-dependency Python library for Bangla (Bengali) NLP text preprocessing.

Built in public as a 12-week engineering roadmap. Each day adds one well-tested component to a growing pipeline — from raw Unicode to ML-ready TF-IDF vectors.

---

## Components

| Module | Class | What it does |
|--------|-------|--------------|
| `normalizer.py` | `BanglaTextNormalizer` | Unicode NFC, ZWJ/ZWNJ, whitespace, punctuation, digit normalisation |
| `cleaner.py` | `BanglaTextCleaner` | Strip URLs, HTML, emails, emojis, digits, mentions, hashtags |
| `pipeline.py` | `Pipeline` | Chainable step runner — compose any callables |
| `tokenizer.py` | `BanglaTokenizer` | Word and sentence tokenisation with Bangla-aware regex |
| `stopwords.py` | — | 150+ curated Bangla stopwords with filter helpers |
| `romanization.py` | `BanglaRomanizer` | Rule-based Bangla → Roman transliteration |
| `stemmer.py` | `BanglaStemmer` | Suffix-stripping stemmer (plurals, case markers, tense suffixes) |
| `vectorizer.py` | `BanglaVectorizer` | TF-IDF vectorizer for pre-tokenised Bangla text |
| `keyword_extractor.py` | `BanglaKeywordExtractor` | Top-k keyword extraction per document using TF-IDF scores |
| `sequence_labeler.py` | `BanglaSequenceLabeler` | Rule-based token labelling (NUM, PUNCT, STOP, WORD + custom rules) |

---

## Installation

```bash
pip install bangla-text-toolkit
```

Or install from source:

```bash
git clone https://github.com/Mouly22/bangla-text-toolkit.git
cd bangla-text-toolkit
pip install -e ".[dev]"
```

---

## Quick start

```python
from bangla_text_toolkit import (
    BanglaTextNormalizer,
    BanglaStemmer,
    BanglaVectorizer,
    BanglaKeywordExtractor,
    BanglaSequenceLabeler,
)
from bangla_text_toolkit.tokenizer import BanglaTokenizer

# 1. Normalise
normalizer = BanglaTextNormalizer()
text = normalizer.normalize("আমি  বাংলায়  গান  গাই!")

# 2. Tokenise
tok = BanglaTokenizer()
tokens = tok.tokenize(text)
# -> ["আমি", "বাংলায়", "গান", "গাই"]

# 3. Label tokens
labeler = BanglaSequenceLabeler()
print(labeler.label(tokens))
# -> [('আমি', 'STOP'), ('বাংলায়', 'STOP'), ('গান', 'WORD'), ('গাই', 'WORD')]

# 4. Extract keywords (TF-IDF)
corpus = [tok.tokenize(t) for t in ["আমি বাংলায় গান গাই", "সে বাংলায় কথা বলে"]]
kex = BanglaKeywordExtractor(top_k=3)
for doc_kws in kex.fit_extract(corpus):
    print(doc_kws)
```

---

## API reference

### BanglaTextNormalizer

```python
from bangla_text_toolkit import BanglaTextNormalizer

n = BanglaTextNormalizer(digit_mode="ascii")
n.normalize("আমি ০১২ বাংলা")  # -> "আমি 012 বাংলা"
```

### BanglaTextCleaner

```python
from bangla_text_toolkit.cleaner import BanglaTextCleaner

c = BanglaTextCleaner(remove_urls=True, remove_emojis=True)
c.clean("দেখো https://example.com 😊")  # -> "দেখো"
```

### Pipeline

```python
from bangla_text_toolkit.pipeline import Pipeline

pipe = Pipeline()
pipe.add_step(lambda t: t.strip())
pipe.add_step(BanglaTextNormalizer().normalize)
result = pipe.run("  আমি বাংলা  ")
```

### BanglaTokenizer

```python
from bangla_text_toolkit.tokenizer import BanglaTokenizer, remove_stopwords

tok = BanglaTokenizer()
tok.tokenize("আমি বাংলায় গান গাই।")
# -> ["আমি", "বাংলায়", "গান", "গাই"]

tok.sent_tokenize("আমি গান গাই। সে কথা বলে।")
# -> ["আমি গান গাই।", "সে কথা বলে।"]
```

### BanglaRomanizer

```python
from bangla_text_toolkit.romanization import BanglaRomanizer

r = BanglaRomanizer()
r.romanize("বাংলা")  # -> "bangla"
```

### BanglaStemmer

```python
from bangla_text_toolkit import BanglaStemmer

s = BanglaStemmer(min_stem_length=2)
s.stem("বাংলাদের")   # -> "বাংলা"
s.stem_tokens(["বাংলাদের", "গানগুলো"])  # -> ["বাংলা", "গান"]
```

### BanglaVectorizer

```python
from bangla_text_toolkit import BanglaVectorizer

corpus = [["আমি", "বাংলা"], ["সে", "বাংলা", "বলে"]]
vec = BanglaVectorizer(max_features=500, min_df=1, use_idf=True)
matrix = vec.fit_transform(corpus)
vec.get_feature_names()
```

### BanglaKeywordExtractor

```python
from bangla_text_toolkit import BanglaKeywordExtractor

corpus = [["আমি", "বাংলায়", "গান", "গাই"], ["সে", "বাংলায়", "কথা", "বলে"]]
kex = BanglaKeywordExtractor(top_k=3, min_df=1, smooth_idf=True)
kex.fit(corpus)
kex.extract(corpus[0])
# -> [('গাই', 0.57...), ('গান', 0.40...), ('আমি', 0.40...)]
```

### BanglaSequenceLabeler

```python
from bangla_text_toolkit import BanglaSequenceLabeler

tokens = ["আমি", "১২৩", "বাংলায়", "গান", "গাই", "।"]
labeler = BanglaSequenceLabeler()
labeler.label(tokens)
# -> [('আমি', 'STOP'), ('১২৩', 'NUM'), ('বাংলায়', 'STOP'),
#     ('গান', 'WORD'), ('গাই', 'WORD'), ('।', 'PUNCT')]

# Add a custom rule (highest priority)
labeler.add_rule(r"[A-Za-z]+", "LATIN")
labeler.label(["hello", "গান"])
# -> [('hello', 'LATIN'), ('গান', 'WORD')]
```

---

## Testing

```bash
pytest tests/ -v
# 213 tests, 0 failures, 0 dependencies
```

---

## Roadmap

12-week build log — one component per session, all tested and CI-green.

| Day | Component | Status |
|-----|-----------|--------|
| 1 | Package scaffold, pyproject.toml, CI | ✅ |
| 2 | `BanglaTextNormalizer` + 36 tests | ✅ |
| 3 | `Pipeline` + 14 tests | ✅ |
| 4 | `BanglaTextCleaner`, `BanglaTokenizer`, stopwords + tests | ✅ |
| 5 | `BanglaRomanizer`, GitHub Actions CI | ✅ |
| 6 | `BanglaStemmer` + 35 tests | ✅ |
| 7 | `BanglaVectorizer` (TF-IDF) + 30 tests | ✅ |
| 8 | `BanglaKeywordExtractor` (top-k TF-IDF keywords) + 29 tests | ✅ |
| 9 | `BanglaSequenceLabeler` (rule-based token labelling) + 33 tests | ✅ |
| 10–12 | Embeddings, demo notebook, PyPI publish | 🔜 |

---

## Why this exists

Standard NLP tools silently break on Bangla text. Python's `\w` regex doesn't match Bangla combining vowel signs (Unicode category `Mc`/`Mn`), and most tokenisers treat matras as noise:

```python
import re
re.findall(r'\w+', 'বাংলা')   # ['ব', 'ল']  ← drops 'া', 'ং'
```

This library handles the full Bangla Unicode block (`U+0980–U+09FF`) correctly, with no external dependencies.

---

## License

MIT © [Umme Abira Azmary](https://github.com/Mouly22)
