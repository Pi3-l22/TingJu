import unittest

from utils.text_processor import get_sentences


class TestTextProcessor(unittest.TestCase):
    def test_basic_english_sentences(self):
        text = (
            "It is often said that we are what we repeatedly do. "
            "This simple statement highlights the influence of our daily habits. "
            "Habits shape our thoughts, guide our actions, and determine the kind of life we live. "
            "Whether good or bad, habits direct our future."
        )
        self.assertEqual(len(get_sentences(text, "english")), 4)

    def test_supported_languages(self):
        texts = {
            "english": "This is a test sentence. It has multiple sentences.",
            "french": "Ceci est une phrase de test. Il y a plusieurs phrases.",
            "german": "Dies ist ein Testsatz. Es gibt mehrere Sätze.",
            "japanese": "今日はいい天気です。明日も晴れるでしょう。",
            "korean": "오늘은 날씨가 좋습니다. 내일도 맑겠습니다.",
            "russian": "Привет, мир. Ещё одно предложение.",
            "spanish": "Esta es una oración de prueba. Tiene varias oraciones.",
            "portuguese": "Este é um texto de teste. Tem várias frases.",
            "italian": "Questo è un testo. Ha più frasi.",
        }
        for language, text in texts.items():
            with self.subTest(language=language):
                self.assertEqual(len(get_sentences(text, language)), 2)

    def test_language_codes_are_accepted(self):
        self.assertEqual(
            get_sentences("This is one sentence. This is another.", "en"),
            ["This is one sentence.", "This is another."],
        )

    def test_multi_sentence_quotation_is_one_learning_unit(self):
        text = 'Someone said, "This is sentence one. This is sentence two." Then everyone agreed.'
        self.assertEqual(
            get_sentences(text, "english"),
            ['Someone said, "This is sentence one. This is sentence two."', "Then everyone agreed."],
        )

    def test_single_sentence_quotation_is_preserved(self):
        text = 'Someone said, "This is a nice day." Then everyone agreed.'
        self.assertEqual(
            get_sentences(text, "english"),
            ['Someone said, "This is a nice day."', "Then everyone agreed."],
        )

    def test_unicode_quotation_is_preserved(self):
        text = "She asked, “Really? You did that?” I nodded."
        self.assertEqual(get_sentences(text, "english"), ["She asked, “Really? You did that?”", "I nodded."])

    def test_japanese_reporting_clause_is_merged(self):
        text = "彼は「やめて！聞いている？戻って！」と叫んだ。ドアが閉まった。"
        self.assertEqual(get_sentences(text, "japanese"), ["彼は「やめて！聞いている？戻って！」と叫んだ。", "ドアが閉まった。"])

    def test_korean_reporting_clause_is_merged(self):
        text = "그는 “멈춰! 듣고 있어? 돌아와!”라고 외쳤다. 문이 닫혔다."
        self.assertEqual(get_sentences(text, "korean"), ["그는 “멈춰! 듣고 있어? 돌아와!”라고 외쳤다.", "문이 닫혔다."])

    def test_abbreviations_decimals_and_urls(self):
        text = (
            "This was reported by C. Liu, et al., in TLS 1.3 research. "
            "Read more at https://example.com/docs. The result is stable."
        )
        sentences = get_sentences(text, "english")
        self.assertEqual(len(sentences), 3)
        self.assertIn("C. Liu, et al.,", sentences[0])
        self.assertIn("TLS 1.3", sentences[0])
        self.assertIn("https://example.com/docs.", sentences[1])

    def test_original_punctuation_and_spacing_are_not_normalized(self):
        text = "First。  Second！"
        sentences = get_sentences(text, "japanese")
        self.assertEqual(sentences, ["First。", "Second！"])

    def test_short_lexical_sentences_are_kept(self):
        self.assertEqual(get_sentences("I. No! Go!", "english"), ["I.", "No!", "Go!"])

    def test_large_text_has_stable_boundaries(self):
        text = " ".join(f"This is sentence {index}." for index in range(100000))
        sentences = get_sentences(text, "english")

        self.assertEqual(len(sentences), 100000)
        self.assertEqual(sentences[0], "This is sentence 0.")
        self.assertEqual(sentences[-1], "This is sentence 99999.")

    def test_large_text_keeps_quoted_block_feature(self):
        text = " ".join(
            'Someone said, "First. Second." Then everyone agreed.' for _ in range(1000)
        )
        sentences = get_sentences(text, "english")

        self.assertEqual(len(sentences), 2000)
        self.assertEqual(sentences[0], 'Someone said, "First. Second."')
        self.assertEqual(sentences[1], "Then everyone agreed.")

    def test_punctuation_only_fragments_are_ignored(self):
        self.assertEqual(get_sentences("... !!!", "english"), [])

    def test_empty_text_is_ignored(self):
        self.assertEqual(get_sentences("   ", "english"), [])

    def test_unknown_language_falls_back_to_english(self):
        self.assertEqual(get_sentences("First sentence. Second sentence.", "unknown"), ["First sentence.", "Second sentence."])


if __name__ == "__main__":
    unittest.main()
