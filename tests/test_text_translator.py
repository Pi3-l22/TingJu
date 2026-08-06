import os
import unittest
from unittest.mock import patch

from utils.text_translator import TRANSLATORS, get_text_translated


class TestTextTranslator(unittest.TestCase):
    def test_get_text_translated(self):
        text_list = [
            "It is often said that we are what we repeatedly do.",
            "This simple statement highlights the incredible influence of our daily habits.",
            "Habits shape our thoughts, guide our actions, and ultimately determine the kind of life we live.",
            "Whether good or bad, habits are powerful forces that quietly direct our future.",
        ]

        class FakeTranslators:
            @staticmethod
            def translate_text(text, **kwargs):
                return "translated"

        with patch("utils.text_translator._load_translators", return_value=FakeTranslators), patch(
            "utils.text_translator._translation_disabled", False
        ):
            translated_text = get_text_translated(text_list)

        self.assertEqual(len(translated_text), len(text_list))
        for original, translated in zip(text_list, translated_text):
            self.assertNotIn(original, translated)

    def test_all_translators(self):
        if os.environ.get("TINGJU_RUN_NETWORK_TESTS") != "1":
            self.skipTest("network integration test; set TINGJU_RUN_NETWORK_TESTS=1 to run")

        os.environ.setdefault("translators_default_region", "CN")
        import translators as ts

        text = "Habits shape our thoughts, guide our actions, and ultimately determine the kind of life we live."
        success_count = 0
        translated_text = []
        for translator in TRANSLATORS:
            try:
                translated = ts.translate_text(
                    text,
                    from_language="en",
                    to_language="zh",
                    translator=translator,
                    timeout=5.0,
                )
                success_count += 1
                translated_text.append(translated)
            except Exception:
                continue

        self.assertGreaterEqual(success_count, len(TRANSLATORS) - 3)
        for translated in translated_text:
            self.assertNotIn(text, translated)


if __name__ == "__main__":
    unittest.main()
