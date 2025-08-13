import unittest
import tempfile
import os
from utils.file_processor import extract_text_from_file

class TestFileProcessor(unittest.TestCase):
    def test_extract_from_unsupported_file(self):
        """测试一个不支持的文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.unsupport', encoding='utf-8') as temp_file:
            temp_file.write('This is a test sentence. This is a another test sentence!')
            temp_file.flush()
            
            # 读取文件内容
            text = extract_text_from_file(temp_file.name)
            self.assertEqual(text, '')
            
    def test_extract_from_txt_file(self):
        """测试现有test.txt文件"""
        text = extract_text_from_file('tests/test.txt')
        self.assertIn('It is often said that we are what we repeatedly do.', text)
        self.assertIn('In conclusion, habits are the building blocks of our lives.', text)
        self.assertEqual(len(text), 2650)
        
    def test_large_file(self):
        """测试一个较大的文件"""
        fd, temp_filename = tempfile.mkstemp(suffix='.txt', text=True)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as temp_file:
                temp_file.write(' '.join([f"This is a test sentence {i}." for i in range(100000)]))
            
            # 读取文件内容
            text = extract_text_from_file(temp_filename)
            self.assertIn("This is a test sentence 0.", text)
            self.assertIn("This is a test sentence 99999.", text)
            self.assertGreater(len(text), 2500000)
        finally:
            # 确保文件被删除
            os.unlink(temp_filename)

if __name__ == '__main__':
    unittest.main()
