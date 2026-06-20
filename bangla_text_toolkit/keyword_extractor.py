"""
bangla_text_toolkit/keyword_extractor.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TF-IDF-based keyword extractor for pre-tokenised Bangla text.

Wraps BanglaVectorizer to surface the highest-scoring terms per document.

Example::

    from bangla_text_toolkit.tokenizer import BanglaTokenizer
    from bangla_text_toolkit.keyword_extractor import BanglaKeywordExtractor

    tok = BanglaTokenizer()
    corpus = [tok.tokenize(t) for t in [
        "আমি বাংলায় গান গাই",
        "সে বাংলায় কথা বলে",
    ]]

    kex = BanglaKeywordExtractor(top_k=3)
    for doc_kws in kex.fit_extract(corpus):
        print(doc_kws)
    # [('গাই', 0.57...), ('গান', 0.40...), ('আমি', 0.40...)]
"""

from __future__ import annotations

from .vectorizer import BanglaVectorizer


class BanglaKeywordExtractor:
    """Extract top-k keywords from pre-tokenised Bangla documents via TF-IDF.

    Parameters
    ----------
    top_k:
        Default number of keywords to return per document.
    max_features:
        Passed to :class:`BanglaVectorizer` — cap vocabulary size.
    min_df:
        Minimum document frequency for a term to enter the vocabulary.
    smooth_idf:
        Use smoothed IDF formula (avoids division-by-zero on rare terms).
    """

    def __init__(
        self,
        top_k: int = 10,
        max_features: int | None = None,
        min_df: int = 1,
        smooth_idf: bool = True,
    ) -> None:
        self.top_k = top_k
        self._vec = BanglaVectorizer(
            max_features=max_features,
            min_df=min_df,
            smooth_idf=smooth_idf,
        )
        self._fitted: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fit(self, corpus: list[list[str]]) -> "BanglaKeywordExtractor":
        """Learn vocabulary and IDF weights from *corpus*.

        Parameters
        ----------
        corpus:
            List of documents, each a list of tokens.

        Returns
        -------
        self
        """
        self._vec.fit(corpus)
        self._fitted = True
        return self

    def extract(
        self,
        doc: list[str],
        top_k: int | None = None,
    ) -> list[tuple[str, float]]:
        """Return ``(term, tfidf_score)`` pairs for *doc*, highest first.

        Parameters
        ----------
        doc:
            A single pre-tokenised document.
        top_k:
            Override the instance-level ``top_k`` for this call.

        Returns
        -------
        List of ``(term, score)`` tuples, sorted descending by score.

        Raises
        ------
        RuntimeError
            If :meth:`fit` has not been called yet.
        """
        if not self._fitted:
            raise RuntimeError(
                "BanglaKeywordExtractor is not fitted. Call fit() first."
            )
        k = top_k if top_k is not None else self.top_k
        vec_row = self._vec.transform([doc])[0]
        names = self._vec.get_feature_names()
        scored = [
            (names[i], score)
            for i, score in enumerate(vec_row)
            if score > 0.0
        ]
        scored.sort(key=lambda x: -x[1])
        return scored[:k]

    def extract_corpus(
        self,
        corpus: list[list[str]],
        top_k: int | None = None,
    ) -> list[list[tuple[str, float]]]:
        """Apply :meth:`extract` to every document in *corpus*."""
        return [self.extract(doc, top_k) for doc in corpus]

    def fit_extract(
        self,
        corpus: list[list[str]],
        top_k: int | None = None,
    ) -> list[list[tuple[str, float]]]:
        """Fit on *corpus* then extract keywords for every document."""
        return self.fit(corpus).extract_corpus(corpus, top_k)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def vocabulary_(self) -> dict[str, int]:
        """Expose the underlying vectorizer vocabulary."""
        return self._vec.vocabulary_

    @property
    def n_features(self) -> int:
        """Number of terms in the fitted vocabulary."""
        return self._vec.n_features
