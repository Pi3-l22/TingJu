import unittest
import shutil
from pathlib import Path
from utils.audio_generator import list_voices, generate_audio, AUDIO_DIR

class TestAudioGenerator(unittest.IsolatedAsyncioTestCase):
    async def test_list_voices(self):
        """测试音色获取功能"""
        voices = await list_voices()
        self.assertIsInstance(voices, list)
        self.assertGreater(len(voices), 10)

    async def test_generate_audio(self):
        """测试音频生成功能"""
        text_list = ['It is often said that we are what we repeatedly do.', 
                    'This simple statement highlights the incredible influence of our daily habits.',
                    'Habits shape our thoughts, guide our actions, and ultimately determine the kind of life we live.',
                    'Whether good or bad, habits are powerful forces that quietly direct our future.']
        voice_name = "en-US-ChristopherNeural"
        title = "test"
        audio_dir, filenames, warning_msg = await generate_audio(text_list, voice_name, title)
        print(audio_dir, filenames, warning_msg)
        
        self.assertEqual(len(text_list), len(filenames))
        self.assertEqual(audio_dir, Path(AUDIO_DIR, title))
        self.assertTrue(audio_dir.exists())
        self.assertEqual(warning_msg, "")
        for i, filename in enumerate(filenames):
            self.assertTrue(audio_dir.joinpath(filename).exists())
            self.assertEqual(filename.split("_")[0], str(i+1))
            self.assertEqual(filename.split(".")[1], "mp3")
            self.assertEqual(len(filename.split("_")[1].split(".")[0]), 32)
            
        # 清理测试目录
        dir = Path(audio_dir)
        if dir.exists():
            shutil.rmtree(dir)

if __name__ == "__main__":
    unittest.main()