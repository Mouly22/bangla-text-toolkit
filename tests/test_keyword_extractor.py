"""
tests/test_keyword_extractor.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tests for BanglaKeywordExtractor.
"""

from __future__ import annotations

import pytest
from bangla_text_toolkit.keyword_extractor import BanglaKeywordExtractor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CORPUS = [
    ["আমি", "বাংলায়", "গান", "গাই"],
    ["সে", "বাংলায়", "কথা", "বলে"],
    ["তুমি", "গান", "শোনো"],
]


@pytest.fixture()
def kex() -> BanglaKeywordExtractor:
    return BanglaKeywordExtractor(top_k=5)


@pytest.fixture()
def fitted(kex: BanglaKeywordExtractor) -> BanglaKeywordExtractor:
    return kex.fit(CORPUS)


# ---------------------------------------------------------------------------
# Fit / vocabulary
# ---------------------------------------------------------------------------

class TestFit:
    def test_fit_sets_fitted_flag(self, kex):
        kex.fit(CORPUS)
        assert kex._fitted

    def test_fit_returns_self(self, kex):
        result = kex.fit(CORPUS)
        assert result is kex

    def test_vocabulary_populated_after_fit(self, fitted):
        assert len(fitted.vocabulary_) > 0

    def test_n_features_positive_after_fit(self, fitted):
        assert fitted.n_features > 0

    def test_n_features_equals_vocab_size(self, fitted):
        assert fitted.n_features == len(fitted.vocabulary_)

    def test_fit_empty_corpus(self, kex):
        kex.fit([])
        assert kex._fitted
        assert kex.n_features == 0


# ---------------------------------------------------------------------------
# Extract single document
# ---------------------------------------------------------------------------

class TestExtract:
    def test_returns_list_of_tuples(self, fitted):
        result = fitted.extract(CORPUS[0])
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_scores_are_positive(self, fitted):
        result = fitted.extract(CORPUS[0])
        assert all(score > 0 for _, score in result)

    def test_sorted_descending(self, fitted):
        result = fitted.extract(CORPUS[0])
        scores = [s for _, s in result]
        assert scores == sorted(scores, reverse=True)

    def test_top_k_limits_results(self, fitted):
        result = fitted.extract(CORPUS[0], top_k=2)
        assert len(result) <= 2

    def test_top_k_1_returns_one(self, fitted):
        result = fitted.extract(CORPUS[0], top_k=1)
        assert len(result) == 1

    def test_empty_doc_returns_empty(self, fitted):
        result = fitted.extract([])
        assert result == []

    def test_unseen_tokens_give_empty(self, fitted):
        result = fitted.extract(["অজানা", "শব্দ"])
        assert result == []

    def test_known_token_appears_in_keywords(self, fitted):
        # "গাই" appears only in doc 0 → high IDF → should rank highly
        kws = [term for term, _ in fitted.extract(CORPUS[0])]
        assert "গাই" in kws

    def test_top_k_override_works(self, fitted):
        full = fitted.extract(CORPUS[0], top_k=100)
        short = fitted.extract(CORPUS[0], top_k=1)
        assert len(short) == 1
        assert short[0] == full[0]

    def test_rare_term_scores_higher_than_common(self, fitted):
        # "বাংলায়" appears in 2 docs (lower IDF); "গাই" in 1 (higher IDF)
        result = fitted.extract(CORPUS[0])
        term_scores = dict(result)
        if "বাংলায়" in term_scores and "গাই" in term_scores:
            assert term_scores["গাই"] > term_scores["বাংলায়"]


# ---------------------------------------------------------------------------
# Extract corpus
# ---------------------------------------------------------------------------

class TestExtractCorpus:
    def test_returns_list_of_length_corpus(self, fitted):
        results = fitted.extract_corpus(CORPUS)
        assert len(results) == len(CORPUS)

    def test_each_result_is_list(self, fitted):
        results = fitted.extract_corpus(CORPUS)
        assert all(isinstance(r, list) for r in results)

    def test_top_k_applied_per_doc(self, fitted):
        results = fitted.extract_corpus(CORPUS, top_k=2)
        assert all(len(r) <= 2 for r in results)

    def test_empty_corpus_returns_empty(self, fitted):
        assert fitted.extract_corpus([]) == []


# ---------------------------------------------------------------------------
# fit_extract convenience
# ---------------------------------------------------------------------------

class TestFitExtract:
    def test_fit_extract_same_as_fit_then_extract_corpus(self):
        k1 = BanglaKeywordExtractor(top_k=5)
        k2 = BanglaKeywordExtractor(top_k=5)
        r1 = k1.fit_extract(CORPUS)
        r2 = k2.fit(CORPUS).extract_corpus(CORPUS)
        assert r1 == r2

    def test_fit_extract_sets_fitted(self):
        kex = BanglaKeywordExtractor()
        kex.fit_extract(CORPUS)
        assert kex._fitted

    def test_fit_extract_returns_list_of_lists(self):
        result = BanglaKeywordExtractor().fit_extract(CORPUS)
        assert isinstance(result, list)
        assert all(isinstance(r, list) for r in result)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrors:
    def test_extract_before_fit_raises(self, kex):
        with pytest.raises(RuntimeError, match="not fitted"):
            kex.extract(CORPUS[0])

    def test_extract_corpus_before_fit_raises(self, kex):
        with pytest.raises(RuntimeError, match="not fitted"):
            kex.extract_corpus(CORPUS)

    def test_fit_then_extract_works(self, kex):
        kex.fit(CORPUS)
        result = kex.extract(CORPUS[0])
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Constructor params
# ---------------------------------------------------------------------------

class TestParams:
    def test_min_df_filters_rare_terms(self):
        kex = BanglaKeywordExtractor(min_df=2)
        kex.fit(CORPUS)
        # Only "বাংলায়" (df=2) and "গান" (df=2) should be in vocab
        assert "বাংলায়" in kex.vocabulary_
        assert "গান" in kex.vocabulary_
        assert "গাই" not in kex.vocabulary_

    def test_max_features_limits_vocab(self):
        kex = BanglaKeywordExtractor(max_features=3)
        kex.fit(CORPUS)
        assert kex.n_features == 3

    def test_default_top_k_respected(self):
        kex = BanglaKeywordExtractor(top_k=2)
        kex.fit(CORPUS)
        result = kex.extract(CORPUS[0])
        assert len(result) <= 2
