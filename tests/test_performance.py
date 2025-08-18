import unittest
import time
import tempfile
from pathlib import Path
from utils.text_processor import get_sentences, init_nltk
from utils.file_processor import extract_text_from_file
from utils.text_translator import get_text_translated
from utils.audio_generator import generate_audio
from utils.language_detector import detect_language

# 测试句子集合
SENTENCES = [
    "The sun is a star at the center of our solar system.",
    "It is a nearly perfect sphere of hot plasma.",
    "Life on Earth depends on its light and heat.",
    "Exploring space helps us understand our place in the universe.",
    "Future missions aim to discover more about distant planets and galaxies.",
    "Have you ever wondered how technology has changed our lives so dramatically?",
    "Just a few decades ago, the idea of carrying a powerful computer in your pocket seemed like science fiction.",
    "Now, it's our everyday reality!",
    "The famous inventor, Mr. Johnson, once said, \"The best way to predict the future is to invent it.\"",
    "This powerful statement continues to inspire innovators around the world.",
    "The journey of innovation is not always easy, but it is always rewarding."
]

class TestPerformance(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化，初始化依赖库"""
        try:
            init_nltk()
        except Exception as e:
            print(f"NLTK 初始化失败: {e}")
    
    def test_sentence_splitting_performance(self):
        """测试分句性能"""
        # 创建一个长文本进行测试
        long_text = " ".join(SENTENCES * 100)  # 1100个句子
        
        start_time = time.time()
        sentences = get_sentences(long_text)
        end_time = time.time()
        
        # 检查结果正确性
        self.assertGreater(len(sentences), 0)
        
        # 检查性能 - 应该在2秒内完成
        execution_time = end_time - start_time
        self.assertLess(execution_time, 2.0)
        
        print(f"对 {len(sentences)} 个句子进行分句的耗时为 {execution_time:.4f} 秒")
    
    def test_file_processing_performance(self):
        """测试文件处理性能"""
        # 创建一个大文本文件
        test_dir = tempfile.mkdtemp()
        large_file = Path(test_dir) / "large.txt"
        
        # 创建包含大量文本的文件
        content = " ".join(SENTENCES * 100)  # 相当于1100个句子
        with open(large_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        start_time = time.time()
        extracted_text = extract_text_from_file(str(large_file))
        end_time = time.time()
        
        # 检查结果
        self.assertIsInstance(extracted_text, str)
        self.assertGreater(len(extracted_text), 0)
        
        # 检查性能
        execution_time = end_time - start_time
        self.assertLess(execution_time, 3.0)  # 应该在3秒内完成
        
        # 清理临时文件
        large_file.unlink()
        Path(test_dir).rmdir()
        
        print(f"大文件处理的耗时为 {execution_time:.4f} 秒")
    
    def test_translation_performance(self):
        """测试翻译性能"""
        start_time = time.time()
        translations = get_text_translated(SENTENCES)
        end_time = time.time()
        
        # 检查结果
        self.assertEqual(len(translations), len(SENTENCES))
        
        # 检查性能 - 翻译可能较慢，但应该在30秒内完成
        execution_time = end_time - start_time
        self.assertLess(execution_time, 30.0)
        
        print(f"对 {len(SENTENCES)} 个句子进行翻译的耗时为: {execution_time:.4f} 秒")
    
    async def test_audio_generation_performance(self):
        """测试音频生成性能"""
        start_time = time.time()
        audio_dir, audio_filenames, _ = await generate_audio(SENTENCES[:5], "en-US-ChristopherNeural", "performance_test")  # 只测试前5个句子
        end_time = time.time()
        
        # 检查结果
        self.assertEqual(len(audio_filenames), 5)
        self.assertTrue(all([Path(audio_dir, filename).exists() for filename in audio_filenames]))
        
        # 检查性能
        execution_time = end_time - start_time
        self.assertLess(execution_time, 30.0)  # 应该在30秒内完成
        
        print(f"对 {len(SENTENCES[:5])} 个句子生成音频的耗时为 {execution_time:.4f} 秒")
        
        # 清理生成的音频文件
        try:
            import shutil
            if audio_dir.exists():
                shutil.rmtree(audio_dir)
        except Exception as e:
            print(f"清理音频文件时出错: {e}")
            
    def test_detect_language_performance(self):
        """测试语言检测性能"""
        text_list = [
            'Hello, how are you today?',
            '你好，今天天气怎么样？',
            "Salut, comment vas-tu aujourd'hui?",
            'Hallo, wie geht es Ihnen heute?',
            'Hola, ¿cómo estás hoy?',
            'こんにちは、今日はどうですか?',
            '안녕, 오늘 어때?',
            'Привет, как ты сегодня?',
            'Oi, como você está hoje?',
            'Ciao, come stai oggi?'
        ] * 100
        
        results = []
        
        start_time = time.time()
        for text in text_list:
            results.append(detect_language(text))
        end_time = time.time()
        
        # 检查结果
        self.assertEqual(len(results), len(text_list))
        
        # 检查性能
        execution_time = end_time - start_time
        self.assertLess(execution_time, 10.0)  # 应该在10秒内完成
        
        print(f"对 {len(text_list)} 条文本进行语言检测的耗时为 {execution_time:.4f} 秒")
        

if __name__ == '__main__':
    unittest.main()