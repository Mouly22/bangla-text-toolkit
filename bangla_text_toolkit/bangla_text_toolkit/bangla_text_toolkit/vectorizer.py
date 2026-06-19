"""
bangla_text_toolkit/vectorizer.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TF-IDF vectorizer for pre-tokenised Bangla (or any) text.

Works on lists of tokens produced by BanglaTokenizer (or any tokenizer).
Zero dependencies — pure Python 3.9+.

Example::

    from bangla_text_toolkit.tokenizer import BanglaTokenizer
    from bangla_text_toolkit.vectorizer import BanglaVectorizer

    tok = BanglaTokenizer()
    corpus = [tok.tokenize(t) for t in ["আমি বাংলায় গান গাই", "সে বাংলায় কথা বলে"]]

    vec = BanglaVectorizer()
    matrix = vec.fit_transform(corpus)
    print(vec.vocabulary_)   # {'আমি': 0, 'গান': 1, ...}
"""

from __future__ import annotations

import math
from collections import Counter


class BanglaVectorizer:
    """TF-IDF vectorizer for pre-tokenised text.

    Parameters
    ----------
    max_features:
        Keep only the *max_features* most-frequent terms (by document
        frequency). ``None`` keeps all terms.
    min_df:
        Minimum number of documents a term must appear in to be included.
    use_idf:
        When ``True`` (default) weight TF by inverse document frequency.
        When ``False`` returns plain term-frequency vectors.
    smooth_idf:
        Add 1 to numerator and denominator of IDF (avoids division-by-zero
        and dampens the effect of very rare terms).  Default ``True``.
    """

    def __init__(
        self,
        max_features: int | None = None,
        min_df: int = 1,
        use_idf: bool = True,
        smooth_idf: bool = True,
    ) -> None:
        self.max_features = max_features
        self.min_df = min_df
        self.use_idf = use_idf
        self.smooth_idf = smooth_idf

        self.vocabulary_: dict[str, int] = {}
        self.idf_: dict[str, float] = {}
        self._fitted: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fit(self, corpus: list[list[str]]) -> "BanglaVectorizer":
        """Learn vocabulary and IDF from *corpus*.

        Parameters
        ----------
        corpus:
            List of documents, each document being a list of tokens.

        Returns
        -------
        self
        """
        df: Counter[str] = Counter()
        for doc in corpus:
            df.update(set(doc))

        # filter by min_df
        terms = [t for t, cnt in df.items() if cnt >= self.min_df]

        # limit to top-N by document frequency, then sort for stable order
        terms.sort(key=lambda t: (-df[t], t))
        if self.max_features is not None:
            terms = terms[: self.max_features]
        terms.sort()  # alphabetical for stable vocab indices

        self.vocabulary_ = {t: i for i, t in enumerate(terms)}

        n = len(corpus)
        if self.smooth_idf:
            self.idf_ = {
                t: math.log((n + 1) / (df[t] + 1)) + 1 for t in terms
            }
        else:
            self.idf_ = {
                t: math.log(n / df[t]) + 1 for t in terms
            }

        self._fitted = True
        return self

    def transform(self, corpus: list[list[str]]) -> list[list[float]]:
        """Transform *corpus* to TF-IDF matrix.

        Parameters
        ----------
        corpus:
            List of documents (lists of tokens).  Tokens not seen during
            ``fit`` are silently ignored.

        Returns
        -------
        List of float vectors, one per document.
        """
        if not self._fitted:
            raise RuntimeError(
                "BanglaVectorizer is not fitted. Call fit() first."
            )

        n_features = len(self.vocabulary_)
        result: list[list[float]] = []

        for doc in corpus:
            vec = [0.0] * n_features
            tf = Counter(doc)
            doc_len = len(doc) or 1
            for term, cnt in tf.items():
                if term not in self.vocabulary_:
                    continue
                idx = self.vocabulary_[term]
                tf_val = cnt / doc_len
                idf_val = self.idf_[term] if self.use_idf else 1.0
                vec[idx] = tf_val * idf_val
            result.append(vec)

        return result

    def fit_transform(self, corpus: list[list[str]]) -> list[list[float]]:
        """Fit then transform in one call."""
        return self.fit(corpus).transform(corpus)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def n_features(self) -> int:
        """Number of features (vocabulary size)."""
        return len(self.vocabulary_)

    def get_feature_names(self) -> list[str]:
        """Return terms in vocabulary index order."""
        return [t for t, _ in sorted(self.vocabulary_.items(), key=lambda x: x[1])]
