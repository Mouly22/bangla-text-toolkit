"""
tests/test_stemmer.py
~~~~~~~~~~~~~~~~~~~~~
Tests for BanglaStemmer.
"""

from __future__ import annotations

import pytest
from bangla_text_toolkit.stemmer import BanglaStemmer


@pytest.fixture()
def stemmer() -> BanglaStemmer:
    return BanglaStemmer()


# ---------------------------------------------------------------------------
# Plural markers
# ---------------------------------------------------------------------------

class TestPlurals:
    def test_ra_vowel_stem(self, stemmer):
        assert stemmer.stem("ছেলেরা") == "ছেলে"

    def test_ra_vowel_stem_2(self, stemmer):
        assert stemmer.stem("মেয়েরা") == "মেয়ে"

    def test_gulo_plural(self, stemmer):
        assert stemmer.stem("বইগুলো") == "বই"

    def test_guli_plural(self, stemmer):
        assert stemmer.stem("গাছগুলি") == "গাছ"

    def test_gulo_with_case(self, stemmer):
        assert stemmer.stem("বইগুলোর") == "বই"


# ---------------------------------------------------------------------------
# Case / postposition markers
# ---------------------------------------------------------------------------

class TestCaseMarkers:
    def test_ke_dative(self, stemmer):
        assert stemmer.stem("ছেলেকে") == "ছেলে"

    def test_r_genitive(self, stemmer):
        assert stemmer.stem("বাড়ির") == "বাড়ি"

    def test_te_locative(self, stemmer):
        assert stemmer.stem("বাড়িতে") == "বাড়ি"

    def test_theke_ablative(self, stemmer):
        assert stemmer.stem("বাড়িথেকে") == "বাড়ি"

    def test_der_gen_plural(self, stemmer):
        assert stemmer.stem("ছেলেদের") == "ছেলে"

    def test_derke_dat_plural(self, stemmer):
        assert stemmer.stem("ছেলেদেরকে") == "ছেলে"


# ---------------------------------------------------------------------------
# Verb: present continuous
# ---------------------------------------------------------------------------

class TestPresentContinuous:
    def test_first_person(self, stemmer):
        assert stemmer.stem("করছি") == "কর"

    def test_third_person(self, stemmer):
        assert stemmer.stem("করছে") == "কর"

    def test_honorific(self, stemmer):
        assert stemmer.stem("করছেন") == "কর"


# ---------------------------------------------------------------------------
# Verb: present perfect
# ---------------------------------------------------------------------------

class TestPresentPerfect:
    def test_first_person(self, stemmer):
        assert stemmer.stem("করেছি") == "কর"

    def test_third_person(self, stemmer):
        assert stemmer.stem("করেছে") == "কর"

    def test_honorific(self, stemmer):
        assert stemmer.stem("করেছেন") == "কর"


# ---------------------------------------------------------------------------
# Verb: simple past
# ---------------------------------------------------------------------------

class TestSimplePast:
    def test_first_person(self, stemmer):
        assert stemmer.stem("করলাম") == "কর"

    def test_honorific(self, stemmer):
        assert stemmer.stem("করলেন") == "কর"

    def test_second_person(self, stemmer):
        assert stemmer.stem("করলে") == "কর"


# ---------------------------------------------------------------------------
# Verb: past continuous
# ---------------------------------------------------------------------------

class TestPastContinuous:
    def test_first_person(self, stemmer):
        assert stemmer.stem("করছিলাম") == "কর"

    def test_honorific(self, stemmer):
        assert stemmer.stem("করছিলেন") == "কর"


# ---------------------------------------------------------------------------
# Short / boundary tokens
# ---------------------------------------------------------------------------

class TestShortTokens:
    def test_at_min_length_unchanged(self, stemmer):
        assert stemmer.stem("আম") == "আম"

    def test_single_char_unchanged(self, stemmer):
        assert stemmer.stem("আ") == "আ"

    def test_two_char_unchanged(self, stemmer):
        assert stemmer.stem("রা") == "রা"  # stripping "া" gives 1-char stem; blocked by min_stem_length


# ---------------------------------------------------------------------------
# No-match tokens
# ---------------------------------------------------------------------------

class TestNoMatch:
    def test_consonant_final_noun(self, stemmer):
        assert stemmer.stem("ফুল") == "ফুল"

    def test_ascii_token_unchanged(self, stemmer):
        assert stemmer.stem("hello") == "hello"

    def test_digit_token_unchanged(self, stemmer):
        assert stemmer.stem("১২৩") == "১২৩"


# ---------------------------------------------------------------------------
# stem_tokens
# ---------------------------------------------------------------------------

class TestStemTokens:
    def test_basic_list(self, stemmer):
        result = stemmer.stem_tokens(["ছেলেরা", "মেয়েরা", "বইগুলো"])
        assert result == ["ছেলে", "মেয়ে", "বই"]

    def test_empty_list(self, stemmer):
        assert stemmer.stem_tokens([]) == []

    def test_mixed_list(self, stemmer):
        result = stemmer.stem_tokens(["ফুল", "করছি", "বইগুলো"])
        assert result[0] == "ফুল"
        assert result[1] == "কর"
        assert result[2] == "বই"

    def test_preserves_order(self, stemmer):
        tokens = ["করছি", "করছে", "করছেন"]
        stems = stemmer.stem_tokens(tokens)
        assert stems == ["কর", "কর", "কর"]


# ---------------------------------------------------------------------------
# Custom min_stem_length
# ---------------------------------------------------------------------------

class TestMinStemLength:
    def test_custom_length_allows_longer_stem(self):
        stemmer = BanglaStemmer(min_stem_length=3)
        assert stemmer.stem("বাড়ির") == "বাড়ি"

    def test_custom_length_blocks_short_stem(self):
        stemmer = BanglaStemmer(min_stem_length=4)
        assert stemmer.stem("করছি") == "করছি"

    def test_default_is_two(self):
        stemmer = BanglaStemmer()
        assert stemmer.min_stem_length == 2
