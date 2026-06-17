import unittest
from bangla_text_toolkit.tokenizer import BanglaTokenizer
from bangla_text_toolkit.stopwords import (
    get_stopwords,
    is_stopword,
    remove_stopwords,
)


class TestSentTokenize(unittest.TestCase):
    def setUp(self):
        self.t = BanglaTokenizer()

    def test_single_sentence(self):
        result = self.t.sent_tokenize("আমি বাড়ি যাচ্ছি।")
        self.assertEqual(len(result), 1)

    def test_two_sentences(self):
        result = self.t.sent_tokenize("আমি বাড়ি যাচ্ছি। তুমি কোথায় যাচ্ছ?")
        self.assertEqual(len(result), 2)

    def test_question_mark(self):
        result = self.t.sent_tokenize("কেমন আছো? ভালো আছি।")
        self.assertEqual(len(result), 2)

    def test_empty_string(self):
        self.assertEqual(self.t.sent_tokenize(""), [])

    def test_type_error(self):
        with self.assertRaises(TypeError):
            self.t.sent_tokenize(42)

    def test_strips_whitespace(self):
        result = self.t.sent_tokenize("  আমি যাচ্ছি।  ")
        self.assertEqual(result[0], "আমি যাচ্ছি।")


class TestWordTokenize(unittest.TestCase):
    def setUp(self):
        self.t = BanglaTokenizer()

    def test_simple(self):
        result = self.t.word_tokenize("আমি বাড়ি যাচ্ছি")
        self.assertEqual(result, ["আমি", "বাড়ি", "যাচ্ছি"])

    def test_multi_space(self):
        result = self.t.word_tokenize("আমি   বাড়ি")
        self.assertEqual(result, ["আমি", "বাড়ি"])

    def test_empty_string(self):
        self.assertEqual(self.t.word_tokenize(""), [])

    def test_single_word(self):
        self.assertEqual(self.t.word_tokenize("আমি"), ["আমি"])

    def test_type_error(self):
        with self.assertRaises(TypeError):
            self.t.word_tokenize(None)

    def test_repr(self):
        self.assertEqual(repr(self.t), "BanglaTokenizer()")


class TestStopwords(unittest.TestCase):
    def test_get_stopwords_type(self):
        self.assertIsInstance(get_stopwords(), frozenset)

    def test_get_stopwords_nonempty(self):
        self.assertGreater(len(get_stopwords()), 0)

    def test_is_stopword_true(self):
        self.assertTrue(is_stopword("আমি"))

    def test_is_stopword_false(self):
        self.assertFalse(is_stopword("বাংলা"))

    def test_is_stopword_type_error(self):
        with self.assertRaises(TypeError):
            is_stopword(123)

    def test_remove_stopwords_basic(self):
        tokens = ["আমি", "বাংলা", "ভালোবাসি"]
        result = remove_stopwords(tokens)
        self.assertNotIn("আমি", result)
        self.assertIn("বাংলা", result)

    def test_remove_stopwords_custom(self):
        custom = frozenset({"বাংলা"})
        tokens = ["আমি", "বাংলা"]
        result = remove_stopwords(tokens, stopwords=custom)
        self.assertIn("আমি", result)
        self.assertNotIn("বাংলা", result)

    def test_remove_stopwords_type_error(self):
        with self.assertRaises(TypeError):
            remove_stopwords("not a list")


if __name__ == "__main__":
    unittest.main()
