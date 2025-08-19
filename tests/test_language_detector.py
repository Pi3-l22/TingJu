import unittest
from utils.language_detector import detect_language, LANGUAGE_CODES, TTS_LOCALES

class TestLanguageDetector(unittest.TestCase):
    def test_detect_supported_language(self):
        """测试支持的语言"""
        text_list = {
            'en': 'Hello, how are you today?',
            'zh-cn': '你好，你今天怎么样？',
            'fr': "Salut, comment vas-tu aujourd'hui?",
            'de': 'Hallo, wie geht es Ihnen heute?',
            'es': 'Hola, ¿cómo estás hoy?',
            'ja': 'こんにちは、今日はどうですか?',
            'ko': '안녕, 오늘 어때?',
            'ru': 'Привет, как ты сегодня?',
            'pt': 'Oi, como você está hoje?',
            'it': 'Ciao, come stai oggi?'
        }
        for lang, text in text_list.items():
            result = detect_language(text)
            self.assertEqual(result['code'], lang)
            self.assertEqual(result['name'], LANGUAGE_CODES[lang])
            self.assertEqual(result['locale'], TTS_LOCALES[lang])
            self.assertIsNone(result['error'])

    def test_detect_unsupported_language(self):
        """测试不支持的语言"""
        unsuppoerted_text = 'مرحبًا، كيف حالك اليوم؟'  # 阿拉伯语
        result = detect_language(unsuppoerted_text)
        self.assertEqual(result['error'], f'语言类型 ar 不支持')
        self.assertIsNone(result['code'])
        self.assertIsNone(result['name'])
        self.assertIsNone(result['locale'])
        