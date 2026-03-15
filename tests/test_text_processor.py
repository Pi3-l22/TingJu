import unittest
from utils.text_processor import init_nltk, get_sentences, normalize_text

class TestTextProcessor(unittest.TestCase):
    
    def test_normalize_text(self):
        """测试文本预处理"""
        text = "This   is a  test sentence。Some people may wonder，“How long does it take to form a habit？”This is a another test sentence！"
        normalized_text = normalize_text(text)
        self.assertEqual(normalized_text, 'This is a test sentence. Some people may wonder, "How long does it take to form a habit?" This is a another test sentence!')

        # 回归测试：专有缩写和小数不应被错误插入空格
        edge_text = "by C. Liu, et al., we compare TLS 1.3 in detail."
        normalized_edge_text = normalize_text(edge_text)
        self.assertIn("et al.,", normalized_edge_text)
        self.assertIn("TLS 1.3", normalized_edge_text)

        ja_text = '今日はいい天気だ...でも“急に雨が降り出した!”と彼は叫んだ. 明日の予定は? (キャンプを中止する) みんなで“楽しみにしていた”イベントだったのに…本当に残念ですね。'
        normalized_text = normalize_text(ja_text, 'japanese')
        self.assertEqual(normalized_text, '今日はいい天気だ…でも『急に雨が降り出した！』と彼は叫んだ。明日の予定は？（キャンプを中止する）みんなで『楽しみにしていた』イベントだったのに…本当に残念ですね。')


    def test_get_sentences(self):
        """测试句子分割"""
        init_nltk()
        text = 'It is often said that we are what we repeatedly do. This simple statement highlights the incredible influence of our daily habits. Habits shape our thoughts, guide our actions, and ultimately determine the kind of life we live. Whether good or bad, habits are powerful forces that quietly direct our future.'
        sentences = get_sentences(text)
        self.assertEqual(len(sentences), 4)
        self.assertEqual(sentences[0], "It is often said that we are what we repeatedly do.")
        self.assertEqual(sentences[1], "This simple statement highlights the incredible influence of our daily habits.")
        self.assertEqual(sentences[2], "Habits shape our thoughts, guide our actions, and ultimately determine the kind of life we live.")
        self.assertEqual(sentences[3], "Whether good or bad, habits are powerful forces that quietly direct our future.")

    def test_large_text(self):
        """测试大文本分句"""
        text = ' '.join([f"This is a test sentence {i}." for i in range(100000)])
        sentences = get_sentences(text)
        self.assertEqual(len(sentences), 100000)
        
    def test_get_sentences_lang(self):
        """测试不同语言的分句"""
        init_nltk()
        texts = {
            'english': 'This is a test sentence. It has multiple sentences.',
            'japanese': '今日はいい天気だ...でも「急に雨が降り出した！」と彼は叫んだ。明日の予定は？（キャンプを中止する）みんなで『楽しみにしていた』イベントだったのに…本当に残念ですね。',
            'korean': '이것은 테스트 문장입니다. 여러 문장이 있습니다.',
            'french': 'Ceci est une phrase de test. Il y a plusieurs phrases.',
            'spanish': 'Esta es una oración de prueba. Tiene varias oraciones.',
            'german': 'Dies ist ein Test-Satz. Es gibt mehrere Sätze.',
            'italian': 'Questo è un testo. Ha più frasi.',
            'portuguese': 'Este é um texto de teste. Tem várias frases.',
            'russian': 'Это тестовая фраза. Имеет несколько предложений.',
        }
        for lang, text in texts.items():
            sentences = get_sentences(text, lang)
            self.assertEqual(len(sentences), 2)

    def test_get_sentences_with_abbreviation_and_decimal(self):
        """回归测试：缩写 + 小数场景不应导致误拆分"""
        init_nltk()
        text = "This was reported by C. Liu, et al., in TLS 1.3 research. The result is stable."
        sentences = get_sentences(text, 'english')
        self.assertEqual(len(sentences), 2)
        self.assertIn("et al.,", sentences[0])
        self.assertIn("TLS 1.3", sentences[0])

    def test_normalize_text_special_cases(self):
        """更多特殊情况：缩写链、版本号、URL、邮箱、数字格式"""
        text = (
            "In the U.S.A.we use v3.10 and TLS 1.3.This is common!"
            "Contact me at test@example.com,and check https://example.com/docs."
            "The budget is 1,000.25 at 12:30."
        )
        normalized = normalize_text(text)

        self.assertIn("U.S.A.", normalized)
        self.assertIn("v3.10", normalized)
        self.assertIn("TLS 1.3", normalized)
        self.assertIn("test@example.com", normalized)
        self.assertIn("https://example.com/docs", normalized)
        self.assertIn("1,000.25", normalized)
        self.assertIn("12:30", normalized)
        self.assertIn("This is common! Contact", normalized)

    def test_get_sentences_with_acronym_and_url(self):
        """回归测试：缩写链与URL不应导致误拆分"""
        init_nltk()
        text = "In the U.S.A. we test TLS 1.3. Read more at https://example.com/docs. This is final."
        sentences = get_sentences(text, 'english')
        self.assertEqual(len(sentences), 3)
        self.assertIn("U.S.A.", sentences[0])
        self.assertIn("TLS 1.3", sentences[0])
        self.assertIn("https://example.com/docs.", sentences[1])

    def test_get_sentences_with_quoted_speech(self):
        """回归测试：引号内句号不应把结尾引号拆成独立句子"""
        text = 'Someone said, "This is a nice day." Then everyone agreed.'
        sentences = get_sentences(text, 'english')

        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], 'Someone said, "This is a nice day."')
        self.assertEqual(sentences[1], 'Then everyone agreed.')

    def test_get_sentences_with_terminal_quote_only(self):
        """回归测试：整句以引号结尾时仍应保持为单句"""
        text = 'Someone said, "This is a nice day."'
        sentences = get_sentences(text, 'english')

        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0], 'Someone said, "This is a nice day."')
        

if __name__ == '__main__':
    unittest.main()