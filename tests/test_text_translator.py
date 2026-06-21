import unittest
import translators as ts
from utils.text_translator import get_text_translated, TRANSLATORS

class TestTextTranslator(unittest.TestCase):
    
    def test_get_text_translated(self):
        """测试翻译功能"""
        text_list = ['It is often said that we are what we repeatedly do.', 
                    'This simple statement highlights the incredible influence of our daily habits.',
                    'Habits shape our thoughts, guide our actions, and ultimately determine the kind of life we live.',
                    'Whether good or bad, habits are powerful forces that quietly direct our future.']
        translated_text = get_text_translated(text_list)
        self.assertEqual(len(translated_text), len(text_list))
        for i, translated in enumerate(translated_text):
            self.assertNotIn(text_list[i], translated)
            self.assertNotIn("翻译失败", translated)
        
    def test_all_translators(self):
        """测试所有翻译器是否正常"""
        text = 'Habits shape our thoughts, guide our actions, and ultimately determine the kind of life we live.'
        success_count = 0
        translated_text = []
        for translator in TRANSLATORS:
            try:
                translated = ts.translate_text(
                    text,
                    from_language='en',
                    to_language='zh',
                    translator=translator,
                    timeout=5.0
                )
                success_count += 1
                translated_text.append(translated)
            except Exception as e:
                continue
        
        # 至少应该有大多数翻译器可用（允许个别翻译器因网络原因暂时不可用）
        self.assertGreaterEqual(success_count, len(TRANSLATORS) - 3)
        
        for translated in translated_text:
            self.assertNotIn(text, translated)
            
if __name__ == '__main__':
    unittest.main()
