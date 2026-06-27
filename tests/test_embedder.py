"""
tests/test_embedder.py
~~~~~~~~~~~~~~~~~~~~~~~~
Tests for BanglaEmbedder.
"""

from __future__ import annotations

import math
import pytest
from bangla_text_toolkit.embedder import BanglaEmbedder


DIM = 32
TOKEN = "বাংলা"
CORPUS = [
    ["আমি", "বাংলায়", "গান", "গাই"],
    ["সে", "বাংলায়", "কথা", "বলে"],
    ["তুমি", "গান", "শোনো"],
]


@pytest.fixture()
def emb() -> BanglaEmbedder:
    return BanglaEmbedder(dim=DIM)


def _norm(vec: list[float]) -> float:
    return math.sqrt(sum(x * x for x in vec))


# ---------------------------------------------------------------------------
# Constructor / params
# ---------------------------------------------------------------------------

class TestInit:
    def test_default_dim(self):
        assert BanglaEmbedder().dim == 64

    def test_custom_dim(self):
        assert BanglaEmbedder(dim=16).dim == 16

    def test_ngram_range_stored(self):
        emb = BanglaEmbedder(ngram_range=(3, 5))
        assert emb.ngram_range == (3, 5)

    def test_invalid_dim_raises(self):
        with pytest.raises(ValueError):
            BanglaEmbedder(dim=0)

    def test_invalid_ngram_min_gt_max_raises(self):
        with pytest.raises(ValueError):
            BanglaEmbedder(ngram_range=(4, 2))

    def test_invalid_ngram_min_zero_raises(self):
        with pytest.raises(ValueError):
            BanglaEmbedder(ngram_range=(0, 3))


# ---------------------------------------------------------------------------
# _extract_ngrams
# ---------------------------------------------------------------------------

class TestExtractNgrams:
    def test_bigrams_from_three_char_token(self, emb):
        emb_2 = BanglaEmbedder(dim=DIM, ngram_range=(2, 2))
        ngrams = emb_2._extract_ngrams("abc")
        assert ngrams == ["ab", "bc"]

    def test_trigrams_from_four_char_token(self, emb):
        emb_3 = BanglaEmbedder(dim=DIM, ngram_range=(3, 3))
        ngrams = emb_3._extract_ngrams("abcd")
        assert ngrams == ["abc", "bcd"]

    def test_empty_token_gives_no_ngrams(self, emb):
        assert emb._extract_ngrams("") == []

    def test_token_shorter_than_min_n_gives_no_ngrams(self):
        emb_3 = BanglaEmbedder(dim=DIM, ngram_range=(3, 4))
        assert emb_3._extract_ngrams("আ") == []

    def test_bangla_token_produces_ngrams(self, emb):
        ngrams = emb._extract_ngrams(TOKEN)
        assert len(ngrams) > 0


# ---------------------------------------------------------------------------
# _hash_ngram
# ---------------------------------------------------------------------------

class TestHashNgram:
    def test_hash_in_range(self, emb):
        assert 0 <= emb._hash_ngram("বাং") < DIM

    def test_hash_deterministic(self, emb):
        assert emb._hash_ngram("গান") == emb._hash_ngram("গান")

    def test_different_dims_give_different_ranges(self):
        e8 = BanglaEmbedder(dim=8)
        e16 = BanglaEmbedder(dim=16)
        idx8 = e8._hash_ngram("বাংলা")
        idx16 = e16._hash_ngram("বাংলা")
        assert 0 <= idx8 < 8
        assert 0 <= idx16 < 16


# ---------------------------------------------------------------------------
# embed_token
# ---------------------------------------------------------------------------

class TestEmbedToken:
    def test_returns_correct_length(self, emb):
        assert len(emb.embed_token(TOKEN)) == DIM

    def test_normalized_has_unit_norm(self, emb):
        vec = emb.embed_token(TOKEN)
        assert abs(_norm(vec) - 1.0) < 1e-9

    def test_not_normalized_values_non_negative(self):
        emb = BanglaEmbedder(dim=DIM, normalize=False)
        vec = emb.embed_token(TOKEN)
        assert all(v >= 0 for v in vec)

    def test_empty_token_returns_zero_vector(self, emb):
        vec = emb.embed_token("")
        assert all(v == 0.0 for v in vec)

    def test_same_token_gives_same_vector(self, emb):
        assert emb.embed_token(TOKEN) == emb.embed_token(TOKEN)

    def test_different_tokens_can_differ(self, emb):
        v1 = emb.embed_token("গান")
        v2 = emb.embed_token("কথা")
        assert v1 != v2

    def test_bangla_token_non_zero_embedding(self, emb):
        vec = emb.embed_token(TOKEN)
        assert any(v != 0.0 for v in vec)


# ---------------------------------------------------------------------------
# embed_tokens
# ---------------------------------------------------------------------------

class TestEmbedTokens:
    def test_returns_list_of_length_tokens(self, emb):
        tokens = ["গান", "বলে", "আমি"]
        result = emb.embed_tokens(tokens)
        assert len(result) == len(tokens)

    def test_each_embedding_correct_length(self, emb):
        result = emb.embed_tokens(["গান", "কথা"])
        assert all(len(v) == DIM for v in result)

    def test_empty_list_returns_empty(self, emb):
        assert emb.embed_tokens([]) == []


# ---------------------------------------------------------------------------
# embed_document
# ---------------------------------------------------------------------------

class TestEmbedDocument:
    def test_returns_correct_length(self, emb):
        assert len(emb.embed_document(CORPUS[0])) == DIM

    def test_empty_tokens_returns_zero_vector(self, emb):
        vec = emb.embed_document([])
        assert len(vec) == DIM
        assert all(v == 0.0 for v in vec)

    def test_normalized_doc_has_unit_norm(self, emb):
        vec = emb.embed_document(CORPUS[0])
        assert abs(_norm(vec) - 1.0) < 1e-9

    def test_different_docs_can_differ(self, emb):
        v1 = emb.embed_document(CORPUS[0])
        v2 = emb.embed_document(CORPUS[1])
        assert v1 != v2

    def test_single_token_doc_matches_embed_token(self):
        emb = BanglaEmbedder(dim=DIM, normalize=False)
        assert emb.embed_document(["গান"]) == emb.embed_token("গান")


# ---------------------------------------------------------------------------
# embed_corpus
# ---------------------------------------------------------------------------

class TestEmbedCorpus:
    def test_returns_list_of_length_corpus(self, emb):
        result = emb.embed_corpus(CORPUS)
        assert len(result) == len(CORPUS)

    def test_each_doc_embedding_correct_length(self, emb):
        result = emb.embed_corpus(CORPUS)
        assert all(len(v) == DIM for v in result)

    def test_empty_corpus_returns_empty(self, emb):
        assert emb.embed_corpus([]) == []

    def test_empty_doc_in_corpus_gives_zero_vector(self, emb):
        result = emb.embed_corpus([[]])
        assert all(v == 0.0 for v in result[0])
