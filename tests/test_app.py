import unittest
import tempfile
import os
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

from app import app, TEMP_DIR, EXPORT_DIR, AUDIO_DIR, cleanup_temp_files

class TestApp(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """在每个测试之前执行"""
        self.app = app
        self.client = TestClient(self.app)
        
        # 创建必要的目录
        Path(TEMP_DIR).mkdir(exist_ok=True)
        Path(AUDIO_DIR).mkdir(exist_ok=True)
        Path(EXPORT_DIR).mkdir(exist_ok=True)

    def tearDown(self):
        """在每个测试之后执行"""
        # 清理临时文件
        cleanup_temp_files()
                    
        # 清理导出文件
        export_dir = Path(EXPORT_DIR)
        if export_dir.exists():
            shutil.rmtree(export_dir)
            export_dir.mkdir(exist_ok=True)

    async def test_read_root(self):
        """测试根路径访问"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        # 检查是否包含主页的关键内容
        self.assertIn("听句 TingJu", response.text)

    async def test_manual_input(self):
        """测试手动输入页面"""
        response = self.client.get("/manual")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        # 检查是否包含手动输入页面的关键内容
        self.assertIn("textarea", response.text)
        self.assertIn("text-content", response.text)

    async def test_get_voices(self):
        """测试获取音色列表"""
        response = self.client.get("/voices")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # 检查返回数据是否包含voices键
        self.assertIn("voices", data)
        # 检查voices是否为列表且不为空
        self.assertIsInstance(data["voices"], list)
        self.assertGreater(len(data["voices"]), 0)

    async def test_upload_file_txt(self):
        """测试上传txt文件"""
        # 创建一个临时txt文件用于测试
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write("This is a test sentence. This is another test sentence.")
            tmp_file_path = tmp_file.name

        try:
            # 上传文件
            with open(tmp_file_path, 'rb') as f:
                response = self.client.post("/upload", files={"file": f})
            
            # 检查响应
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/html", response.headers["content-type"])
            # 检查是否跳转到文本确认页面
            self.assertIn("textarea", response.text)
            self.assertIn("text-content", response.text)
        finally:
            # 清理临时文件
            os.unlink(tmp_file_path)

    async def test_upload_file_unsupported(self):
        """测试上传不支持的文件类型"""
        # 创建一个不支持的文件类型
        with tempfile.NamedTemporaryFile(mode='w', suffix='.unsupported', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write("This is a test sentence.")
            tmp_file_path = tmp_file.name

        try:
            # 上传文件
            with open(tmp_file_path, 'rb') as f:
                response = self.client.post("/upload", files={"file": f})
            
            # 检查响应
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/html", response.headers["content-type"])
            # 检查是否返回index.html页面
            self.assertIn("upload-form", response.text)
            self.assertIn("upload-area", response.text)
        finally:
            # 清理临时文件
            os.unlink(tmp_file_path)

    async def test_generate(self):
        """测试生成音频和翻译功能"""
        test_text = "This is a test sentence. This is another test sentence."
        response = self.client.post("/generate", data={
            "text": test_text,
            "voice": "en-US-ChristopherNeural"
        })
        
        # 检查响应
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        # 检查是否跳转到结果页面
        self.assertIn("result-item", response.text)
        
        # 检查结果中是否包含句子和翻译
        self.assertIn("This is a test sentence.", response.text)
        self.assertIn("This is another test sentence.", response.text)

    async def test_generate_empty_text(self):
        """测试生成空文本时的处理"""
        response = self.client.post("/generate", data={
            "text": "",
            "voice": "en-US-ChristopherNeural"
        })
        
        # 检查响应
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        # 检查是否返回错误信息
        self.assertIn("未能从文本中分割出句子", response.text)

    async def test_export_content(self):
        """测试导出功能"""
        # 先生成一些内容，设置CURRENT_UUID
        test_text = "This is a test sentence. This is another test sentence."
        response = self.client.post("/generate", data={
            "text": test_text,
            "voice": "en-US-ChristopherNeural"
        })
        
        self.assertEqual(response.status_code, 200)
        
        # 测试导出功能
        response = self.client.get("/export")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 检查返回数据
        self.assertIn("status", data)
        self.assertIn("message", data)
        self.assertIn("path", data)
        self.assertEqual(data["status"], "success")
        
        # 检查导出路径是否存在
        export_path = Path(data["path"])
        self.assertTrue(export_path.exists())
        
        # 检查导出目录中是否包含必要文件
        self.assertTrue((export_path / "index.html").exists())
        self.assertTrue((export_path / "css").exists())
        self.assertTrue((export_path / "js").exists())
        self.assertTrue((export_path / "img").exists())
        self.assertTrue((export_path / AUDIO_DIR).exists())

if __name__ == "__main__":
    unittest.main()