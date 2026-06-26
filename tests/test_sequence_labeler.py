"""
tests/test_sequence_labeler.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tests for BanglaSequenceLabeler.
"""

from __future__ import annotations

import pytest
from bangla_text_toolkit.sequence_labeler import BanglaSequenceLabeler


# Known stop words from the built-in list
_STOP_WORD = "আমি"   # confirmed in stopwords._STOPWORDS
_NON_STOP  = "গানবাজনা"  # not in stopwords


@pytest.fixture()
def labeler() -> BanglaSequenceLabeler:
    return BanglaSequenceLabeler()


# ---------------------------------------------------------------------------
# NUM built-in label
# ---------------------------------------------------------------------------

class TestNumLabel:
    def test_bangla_digits_labeled_num(self, labeler):
        assert labeler._label_one("০১২৩") == "NUM"

    def test_ascii_digits_labeled_num(self, labeler):
        assert labeler._label_one("123") == "NUM"

    def test_mixed_bangla_ascii_digits_labeled_num(self, labeler):
        assert labeler._label_one("১2৩") == "NUM"

    def test_alpha_not_labeled_num(self, labeler):
        assert labeler._label_one("গান") != "NUM"

    def test_digit_with_alpha_suffix_not_labeled_num(self, labeler):
        assert labeler._label_one("৩গ") != "NUM"


# ---------------------------------------------------------------------------
# PUNCT built-in label
# ---------------------------------------------------------------------------

class TestPunctLabel:
    def test_daari_labeled_punct(self, labeler):
        assert labeler._label_one("।") == "PUNCT"

    def test_comma_labeled_punct(self, labeler):
        assert labeler._label_one(",") == "PUNCT"

    def test_question_mark_labeled_punct(self, labeler):
        assert labeler._label_one("?") == "PUNCT"

    def test_exclamation_labeled_punct(self, labeler):
        assert labeler._label_one("!") == "PUNCT"

    def test_word_not_labeled_punct(self, labeler):
        assert labeler._label_one("গান") != "PUNCT"


# ---------------------------------------------------------------------------
# STOP built-in label
# ---------------------------------------------------------------------------

class TestStopLabel:
    def test_known_stop_labeled_stop(self, labeler):
        assert labeler._label_one(_STOP_WORD) == "STOP"

    def test_non_stop_word_not_labeled_stop(self, labeler):
        assert labeler._label_one(_NON_STOP) != "STOP"

    def test_use_stopwords_false_disables_stop_label(self):
        lb = BanglaSequenceLabeler(use_stopwords=False)
        assert lb._label_one(_STOP_WORD) != "STOP"

    def test_use_stopwords_false_falls_through_to_default(self):
        lb = BanglaSequenceLabeler(use_stopwords=False)
        assert lb._label_one(_STOP_WORD) == "WORD"


# ---------------------------------------------------------------------------
# Default label
# ---------------------------------------------------------------------------

class TestDefaultLabel:
    def test_unknown_token_gets_word(self, labeler):
        assert labeler._label_one(_NON_STOP) == "WORD"

    def test_custom_default_label(self):
        lb = BanglaSequenceLabeler(default_label="UNK")
        assert lb._label_one(_NON_STOP) == "UNK"


# ---------------------------------------------------------------------------
# Custom rules
# ---------------------------------------------------------------------------

class TestCustomRules:
    def test_add_rule_returns_self(self, labeler):
        result = labeler.add_rule(r".*", "TEST")
        assert result is labeler

    def test_append_rule_returns_self(self, labeler):
        lb = BanglaSequenceLabeler()
        result = lb.append_rule(r".*", "TEST")
        assert result is lb

    def test_add_rule_overrides_builtin(self):
        lb = BanglaSequenceLabeler()
        lb.add_rule(r"[০-৯]+", "CUSTOM_NUM")
        assert lb._label_one("৫") == "CUSTOM_NUM"

    def test_prepended_rule_wins_over_appended(self):
        lb = BanglaSequenceLabeler()
        lb.append_rule(r"গান", "LOW")
        lb.add_rule(r"গান", "HIGH")
        assert lb._label_one("গান") == "HIGH"

    def test_two_add_rules_last_prepended_wins(self):
        lb = BanglaSequenceLabeler()
        lb.add_rule(r"গান", "FIRST")
        lb.add_rule(r"গান", "SECOND")  # prepended → index 0
        assert lb._label_one("গান") == "SECOND"

    def test_non_matching_rule_falls_through(self):
        lb = BanglaSequenceLabeler()
        lb.add_rule(r"xyz", "LATIN")
        assert lb._label_one("গান") == "WORD"

    def test_rules_property_lists_patterns(self):
        lb = BanglaSequenceLabeler()
        lb.add_rule(r"গান", "SONG")
        patterns = [p for p, _ in lb.rules]
        assert "গান" in patterns

    def test_append_rule_appears_in_rules(self):
        lb = BanglaSequenceLabeler()
        lb.append_rule(r"গান", "SONG")
        labels = [lbl for _, lbl in lb.rules]
        assert "SONG" in labels


# ---------------------------------------------------------------------------
# label() method
# ---------------------------------------------------------------------------

class TestLabelMethod:
    def test_returns_list_of_tuples(self, labeler):
        result = labeler.label(["গান", "।"])
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_preserves_token_order_and_text(self, labeler):
        tokens = ["গান", "।", "১২৩"]
        result = labeler.label(tokens)
        assert [tok for tok, _ in result] == tokens

    def test_empty_tokens_returns_empty(self, labeler):
        assert labeler.label([]) == []

    def test_single_word_token(self, labeler):
        assert labeler.label(["গান"]) == [("গান", "WORD")]

    def test_mixed_sequence_labels_correctly(self, labeler):
        tokens = [_STOP_WORD, "১২৩", "।", "গান"]
        result = dict(labeler.label(tokens))
        assert result[_STOP_WORD] == "STOP"
        assert result["১২৩"] == "NUM"
        assert result["।"] == "PUNCT"
        assert result["গান"] == "WORD"


# ---------------------------------------------------------------------------
# label_corpus() method
# ---------------------------------------------------------------------------

class TestLabelCorpus:
    def test_returns_list_of_length_corpus(self, labeler):
        corpus = [["গান", "।"], ["১২৩", _STOP_WORD]]
        results = labeler.label_corpus(corpus)
        assert len(results) == len(corpus)

    def test_each_doc_result_is_list_of_tuples(self, labeler):
        corpus = [["গান"], ["।"]]
        results = labeler.label_corpus(corpus)
        for doc_result in results:
            assert all(isinstance(item, tuple) for item in doc_result)

    def test_empty_corpus_returns_empty(self, labeler):
        assert labeler.label_corpus([]) == []

    def test_empty_doc_in_corpus(self, labeler):
        results = labeler.label_corpus([[]])
        assert results == [[]]
