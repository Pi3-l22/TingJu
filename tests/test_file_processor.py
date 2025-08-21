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
            
    def test_extract_from_markdown_file(self):
        """测试 Markdown 文件提取"""
        markdown_content = """# Test Title
This is **bold** and *italic* text.
- List item
> Quote text
```code block```
Normal text after code."""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(markdown_content)
            temp_file.flush()
            temp_filename = temp_file.name
            
        try:
            text = extract_text_from_file(temp_filename)
            
            # 验证基本功能
            self.assertGreater(len(text), 0)
            self.assertIn("Test Title", text)
            self.assertIn("bold", text)
            self.assertIn("italic", text)
            self.assertIn("Normal text after code", text)
            
            # 验证格式标记已移除
            self.assertNotIn("#", text)
            self.assertNotIn("**", text)
            self.assertNotIn("```", text)
            
        finally:
            os.unlink(temp_filename)

if __name__ == '__main__':
    unittest.main()
