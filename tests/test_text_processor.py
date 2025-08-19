import unittest
from utils.text_processor import init_nltk, get_sentences, normalize_text

class TestTextProcessor(unittest.TestCase):
    
    def test_normalize_text(self):
        """测试文本预处理"""
        text = "This   is a  test sentence。Some people may wonder，“How long does it take to form a habit？”This is a another test sentence！"
        normalized_text = normalize_text(text)
        self.assertEqual(normalized_text, 'This is a test sentence. Some people may wonder, "How long does it take to form a habit?" This is a another test sentence!')
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
        

if __name__ == '__main__':
    unittest.main()