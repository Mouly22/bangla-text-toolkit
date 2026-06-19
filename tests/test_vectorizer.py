"""
tests/test_vectorizer.py
~~~~~~~~~~~~~~~~~~~~~~~~
Tests for BanglaVectorizer.
"""

from __future__ import annotations

import math

import pytest
from bangla_text_toolkit.vectorizer import BanglaVectorizer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CORPUS = [
    ["আমি", "বাংলায়", "গান", "গাই"],
    ["সে", "বাংলায়", "কথা", "বলে"],
    ["তুমি", "গান", "শোনো"],
]


@pytest.fixture()
def vec() -> BanglaVectorizer:
    return BanglaVectorizer()


@pytest.fixture()
def fitted(vec: BanglaVectorizer) -> BanglaVectorizer:
    return vec.fit(CORPUS)


# ---------------------------------------------------------------------------
# Vocabulary building
# ---------------------------------------------------------------------------

class TestVocabulary:
    def test_all_tokens_in_vocab(self, fitted):
        all_terms = {t for doc in CORPUS for t in doc}
        assert all_terms == set(fitted.vocabulary_.keys())

    def test_vocab_indices_contiguous(self, fitted):
        indices = sorted(fitted.vocabulary_.values())
        assert indices == list(range(len(fitted.vocabulary_)))

    def test_vocab_sorted_alphabetically(self, fitted):
        terms = fitted.get_feature_names()
        assert terms == sorted(terms)

    def test_n_features_equals_vocab_size(self, fitted):
        assert fitted.n_features == len(fitted.vocabulary_)

    def test_get_feature_names_order(self, fitted):
        names = fitted.get_feature_names()
        for term, idx in fitted.vocabulary_.items():
            assert names[idx] == term


# ---------------------------------------------------------------------------
# min_df filtering
# ---------------------------------------------------------------------------

class TestMinDf:
    def test_min_df_2_removes_rare_terms(self):
        vec = BanglaVectorizer(min_df=2)
        vec.fit(CORPUS)
        # "বাংলায়" appears in 2 docs, "গান" in 2 docs; others appear in 1
        assert "বাংলায়" in vec.vocabulary_
        assert "গান" in vec.vocabulary_
        assert "আমি" not in vec.vocabulary_

    def test_min_df_3_keeps_only_universal_terms(self):
        corpus = [["ক", "খ"], ["ক", "গ"], ["ক", "ঘ"]]
        vec = BanglaVectorizer(min_df=3)
        vec.fit(corpus)
        assert list(vec.vocabulary_.keys()) == ["ক"]

    def test_min_df_larger_than_corpus_gives_empty_vocab(self):
        vec = BanglaVectorizer(min_df=10)
        vec.fit(CORPUS)
        assert vec.n_features == 0


# ---------------------------------------------------------------------------
# max_features
# ---------------------------------------------------------------------------

class TestMaxFeatures:
    def test_max_features_limits_vocab(self):
        vec = BanglaVectorizer(max_features=3)
        vec.fit(CORPUS)
        assert vec.n_features == 3

    def test_max_features_keeps_highest_df(self):
        # "বাংলায়" (df=2) and "গান" (df=2) should be preferred over singletons
        vec = BanglaVectorizer(max_features=2)
        vec.fit(CORPUS)
        assert "বাংলায়" in vec.vocabulary_
        assert "গান" in vec.vocabulary_

    def test_max_features_none_keeps_all(self):
        vec = BanglaVectorizer(max_features=None)
        vec.fit(CORPUS)
        assert vec.n_features == len({t for doc in CORPUS for t in doc})


# ---------------------------------------------------------------------------
# Transform output shape & values
# ---------------------------------------------------------------------------

class TestTransform:
    def test_output_length_equals_corpus_length(self, fitted):
        matrix = fitted.transform(CORPUS)
        assert len(matrix) == len(CORPUS)

    def test_each_vector_has_n_features_elements(self, fitted):
        matrix = fitted.transform(CORPUS)
        for row in matrix:
            assert len(row) == fitted.n_features

    def test_unseen_tokens_are_ignored(self, fitted):
        matrix = fitted.transform([["অজানা", "শব্দ"]])
        assert all(v == 0.0 for v in matrix[0])

    def test_empty_doc_gives_zero_vector(self, fitted):
        matrix = fitted.transform([[]])
        assert all(v == 0.0 for v in matrix[0])

    def test_known_token_has_positive_score(self, fitted):
        idx = fitted.vocabulary_["আমি"]
        matrix = fitted.transform([["আমি"]])
        assert matrix[0][idx] > 0.0

    def test_repeated_token_has_higher_tf(self, fitted):
        idx = fitted.vocabulary_["গান"]
        # Use mixed docs: TF("গান") = 1/2 vs 2/3 — avoids equal-TF edge case
        single = fitted.transform([["গান", "আমি"]])[0][idx]
        double = fitted.transform([["গান", "গান", "আমি"]])[0][idx]
        assert double > single

    def test_non_present_token_is_zero(self, fitted):
        idx = fitted.vocabulary_["আমি"]
        matrix = fitted.transform([["সে", "বলে"]])
        assert matrix[0][idx] == 0.0


# ---------------------------------------------------------------------------
# IDF values
# ---------------------------------------------------------------------------

class TestIdf:
    def test_rare_term_has_higher_idf(self, fitted):
        # "আমি" appears in 1 doc; "বাংলায়" in 2 docs
        assert fitted.idf_["আমি"] > fitted.idf_["বাংলায়"]

    def test_smooth_idf_all_positive(self, fitted):
        assert all(v > 0 for v in fitted.idf_.values())

    def test_no_smooth_idf(self):
        vec = BanglaVectorizer(smooth_idf=False)
        vec.fit(CORPUS)
        # log(3/1)+1 for a term in 1 doc
        expected = math.log(3 / 1) + 1
        assert abs(vec.idf_["আমি"] - expected) < 1e-9

    def test_smooth_idf_formula(self):
        vec = BanglaVectorizer(smooth_idf=True)
        vec.fit(CORPUS)
        n = len(CORPUS)
        df_ami = 1  # "আমি" in 1 doc
        expected = math.log((n + 1) / (df_ami + 1)) + 1
        assert abs(vec.idf_["আমি"] - expected) < 1e-9


# ---------------------------------------------------------------------------
# use_idf=False (plain TF)
# ---------------------------------------------------------------------------

class TestUseTfOnly:
    def test_use_idf_false_gives_tf_only(self):
        vec = BanglaVectorizer(use_idf=False)
        vec.fit(CORPUS)
        matrix = vec.transform([["গান", "গান", "আমি"]])
        idx_gan = vec.vocabulary_["গান"]
        # TF("গান") = 2/3
        assert abs(matrix[0][idx_gan] - 2 / 3) < 1e-9

    def test_use_idf_false_all_idf_unused(self):
        vec = BanglaVectorizer(use_idf=False)
        vec.fit([["ক", "ক", "খ"]])
        matrix = vec.transform([["ক", "খ"]])
        idx_ka = vec.vocabulary_["ক"]
        # TF("ক") in ["ক","খ"] = 1/2; idf multiplier = 1.0
        assert abs(matrix[0][idx_ka] - 0.5) < 1e-9


# ---------------------------------------------------------------------------
# fit_transform convenience
# ---------------------------------------------------------------------------

class TestFitTransform:
    def test_fit_transform_same_as_fit_then_transform(self):
        v1 = BanglaVectorizer()
        v2 = BanglaVectorizer()
        m1 = v1.fit_transform(CORPUS)
        m2 = v2.fit(CORPUS).transform(CORPUS)
        assert m1 == m2

    def test_fit_transform_returns_list_of_lists(self):
        result = BanglaVectorizer().fit_transform(CORPUS)
        assert isinstance(result, list)
        assert all(isinstance(row, list) for row in result)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrors:
    def test_transform_before_fit_raises(self, vec):
        with pytest.raises(RuntimeError, match="not fitted"):
            vec.transform(CORPUS)

    def test_fit_empty_corpus(self, vec):
        vec.fit([])
        assert vec.n_features == 0
        assert vec._fitted

    def test_transform_after_empty_fit(self, vec):
        vec.fit([])
        matrix = vec.transform([["আমি"]])
        assert matrix == [[]]
