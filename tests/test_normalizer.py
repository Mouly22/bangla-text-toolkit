"""
tests/test_normalizer.py
~~~~~~~~~~~~~~~~~~~~~~~~
Tests for bangla_text_toolkit.normalizer.BanglaTextNormalizer.
"""

import pytest
from bangla_text_toolkit.normalizer import BanglaTextNormalizer


@pytest.fixture
def n():
      return BanglaTextNormalizer()


@pytest.fixture
def n_ascii():
      return BanglaTextNormalizer(digit_mode="ascii")


@pytest.fixture
def n_bangla():
      return BanglaTextNormalizer(digit_mode="bangla")


class TestNormalize:
      def test_empty_string(self, n):
                assert n.normalize("") == ""

      def test_plain_bangla(self, n):
                assert n.normalize("আমি বাংলায় গান গাই।") == "আমি বাংলায় গান গাই।"

      def test_strips_leading_trailing_spaces(self, n):
                assert n.normalize("  আমি  ") == "আমি"

      def test_collapses_multiple_spaces(self, n):
                assert n.normalize("আমি  বাংলায়  গান") == "আমি বাংলায় গান"

      def test_removes_zero_width_joiner(self, n):
                text = "গান‍গাই"  # ZWJ between words
        assert "‍" not in n.normalize(text)

    def test_removes_zero_width_non_joiner(self, n):
              text = "বাংলা‌দেশ"  # ZWNJ
        assert "‌" not in n.normalize(text)

    def test_removes_bom(self, n):
              assert n.normalize("﻿আমি") == "আমি"

    def test_curly_quotes_normalized(self, n):
              assert n.normalize("‘hello’") == "'hello'"
              assert n.normalize("“hello”") == '"hello"'

    def test_em_dash_to_hyphen(self, n):
              assert n.normalize("এক—দুই") == "এক-দুই"

    def test_type_error_on_non_string(self, n):
              with pytest.raises(TypeError):
                            n.normalize(123)

          def test_mixed_bangla_english(self, n):
                    assert n.normalize("  Hello বাংলা  ") == "Hello বাংলা"


class TestNormalizeUnicode:
      def test_nfc_default(self, n):
                import unicodedata
                text = "আমি"
                assert n.normalize_unicode(text) == unicodedata.normalize("NFC", text)

    def test_invalid_form_raises(self):
              with pytest.raises(ValueError, match="Invalid unicode_form"):
                            BanglaTextNormalizer(unicode_form="XYZ")


class TestRemoveZeroWidth:
      def test_removes_zwj(self, n):
                assert n.remove_zero_width("গান‍গাই") == "গানগাই"

    def test_removes_zwnj(self, n):
              assert n.remove_zero_width("বাংলা‌দেশ") == "বাংলাদেশ"

    def test_no_op_on_clean_text(self, n):
              text = "আমি বাংলায় গান গাই।"
              assert n.remove_zero_width(text) == text


class TestNormalizeWhitespace:
      def test_collapse_spaces(self, n):
                assert n.normalize_whitespace("ক  খ   গ") == "ক খ গ"

    def test_nbsp_to_space(self, n):
              assert n.normalize_whitespace("ক খ") == "ক খ"

    def test_tab_to_space(self, n):
              assert n.normalize_whitespace("ক\tখ") == "ক খ"

    def test_strip(self, n):
              assert n.normalize_whitespace("  ক  ") == "ক"


class TestNormalizePunctuation:
      def test_danda_preserved(self, n):
                assert "।" in n.normalize_punctuation("আমি গাই।")

    def test_devanagari_abbreviation_to_danda(self, n):
              result = n.normalize_punctuation("ড॰ আজিজ")
              assert "।" in result
              assert "॰" not in result


class TestNormalizeDigits:
      def test_bangla_to_ascii(self, n):
                assert n.normalize_digits("০১২৩৪৫৬৭৮৯", target="ascii") == "0123456789"

    def test_ascii_to_bangla(self, n):
              assert n.normalize_digits("0123456789", target="bangla") == "০১২৩৪৫৬৭৮৯"

    def test_digit_mode_ascii_via_constructor(self, n_ascii):
              result = n_ascii.normalize("আমার ০৩টি বই।")
              assert "03" in result

    def test_digit_mode_bangla_via_constructor(self, n_bangla):
              result = n_bangla.normalize("আমার 3টি বই।")
              assert "৩" in result

    def test_invalid_digit_mode_raises(self, n):
              with pytest.raises(ValueError, match="target must be"):
                            n.normalize_digits("০", target="roman")

          def test_invalid_digit_mode_constructor_raises(self):
                    with pytest.raises(ValueError, match="Invalid digit_mode"):
                                  BanglaTextNormalizer(digit_mode="roman")

                def test_no_digit_change_when_mode_none(self, n):
                          assert "০" in n.normalize("০১২")


class TestRepr:
      def test_repr(self, n):
                assert "BanglaTextNormalizer" in repr(n)
                assert "NFC" in repr(n)
        
