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
                return "翻译结果"

        with patch("utils.text_translator._load_translators", return_value=FakeTranslators), patch(
            "utils.text_translator._translation_disabled", False
        ):
            translated_text, warning = get_text_translated(text_list)

        self.assertEqual(len(translated_text), len(text_list))
        self.assertEqual(warning, "")
        for original, translated in zip(text_list, translated_text):
            self.assertNotIn(original, translated)

    def test_invalid_sogou_style_response_switches_provider(self):
        text_list = [f"This is test sentence number {i}." for i in range(33)]
        calls = []

        class FakeTranslators:
            @staticmethod
            def translate_text(text, **kwargs):
                provider = kwargs["translator"]
                calls.append(provider)
                if provider == "youdao" and calls.count("youdao") <= 19:
                    return "有效翻译"
                if provider == "youdao":
                    return "x98tog3p6vtfq7yz8soj"
                if provider == "alibaba":
                    return "阿里翻译"
                raise AssertionError(f"unexpected provider {provider}")

        with patch("utils.text_translator._load_translators", return_value=FakeTranslators), patch(
            "utils.text_translator._translation_disabled", False
        ):
            translated_text, warning = get_text_translated(text_list)

        self.assertEqual(len(translated_text), 33)
        self.assertEqual(warning, "")
        self.assertNotIn("x98tog3p6vtfq7yz8soj", translated_text)
        self.assertEqual(translated_text[:19], ["有效翻译"] * 19)
        self.assertEqual(translated_text[19:], ["阿里翻译"] * 14)
        self.assertEqual(calls.count("youdao"), 20)
        self.assertEqual(calls.count("alibaba"), 14)

    def test_all_providers_failed_preserves_original_and_warns(self):
        text_list = ["A complete English sentence for testing.", "Another complete sentence."]

        class FakeTranslators:
            @staticmethod
            def translate_text(text, **kwargs):
                raise RuntimeError("offline")

        with patch("utils.text_translator._load_translators", return_value=FakeTranslators), patch(
            "utils.text_translator._translation_disabled", False
        ):
            translated_text, warning = get_text_translated(text_list)

        self.assertEqual(translated_text, text_list)
        self.assertIn("第 1,2 句翻译失败", warning)

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
