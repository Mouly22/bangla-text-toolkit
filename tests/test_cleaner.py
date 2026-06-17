import unittest
from bangla_text_toolkit.cleaner import BanglaTextCleaner


class TestCleanerDefaults(unittest.TestCase):
    def setUp(self):
        self.c = BanglaTextCleaner()

    def test_empty_string(self):
        self.assertEqual(self.c.clean(""), "")

    def test_plain_bangla_unchanged(self):
        text = "আমি বাংলা ভাষায় কথা বলি"
        self.assertEqual(self.c.clean(text), text)

    def test_removes_url(self):
        self.assertNotIn("http", self.c.clean("visit https://example.com today"))

    def test_removes_www(self):
        self.assertNotIn("www", self.c.clean("go to www.example.com"))

    def test_removes_email(self):
        self.assertNotIn("@", self.c.clean("email me at foo@bar.com"))

    def test_removes_html(self):
        result = self.c.clean("<p>হ্যালো</p>")
        self.assertNotIn("<", result)
        self.assertIn("হ্যালো", result)

    def test_collapses_spaces(self):
        self.assertNotIn("  ", self.c.clean("আমি   তুমি"))

    def test_type_error(self):
        with self.assertRaises(TypeError):
            self.c.clean(123)

    def test_repr(self):
        self.assertIn("BanglaTextCleaner", repr(self.c))


class TestCleanerOptions(unittest.TestCase):
    def test_remove_mentions(self):
        c = BanglaTextCleaner(remove_mentions=True)
        self.assertNotIn("@user", c.clean("hello @user world"))

    def test_keep_mentions_by_default(self):
        c = BanglaTextCleaner()
        self.assertIn("@user", c.clean("hello @user world"))

    def test_remove_hashtags(self):
        c = BanglaTextCleaner(remove_hashtags=True)
        self.assertNotIn("#tag", c.clean("hello #tag world"))

    def test_remove_emoji(self):
        c = BanglaTextCleaner(remove_emoji=True)
        result = c.clean("আমি 😀 হাসছি")
        self.assertNotIn("😀", result)

    def test_remove_punctuation(self):
        c = BanglaTextCleaner(remove_punctuation=True)
        self.assertNotIn("।", c.clean("আমি বলি।"))

    def test_remove_digits(self):
        c = BanglaTextCleaner(remove_digits=True)
        self.assertNotIn("5", c.clean("I have 5 apples"))

    def test_remove_bangla_digits(self):
        c = BanglaTextCleaner(remove_digits=True)
        self.assertNotIn("৫", c.clean("আমার ৫টি বই"))


if __name__ == "__main__":
    unittest.main()
