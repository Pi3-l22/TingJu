import unittest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

from utils.audio_generator import list_voices, generate_audio

class TestAudioGenerator(unittest.IsolatedAsyncioTestCase):
    async def test_list_voices(self):
        """测试音色获取功能"""
        class FakeVoices:
            def find(self, **kwargs):
                return [{
                    "ShortName": "en-US-TestNeural",
                    "Gender": "Female",
                    "VoiceTag": {
                        "ContentCategories": [],
                        "VoicePersonalities": [],
                    },
                }]

        async def create_voices():
            return FakeVoices()

        with patch("utils.audio_generator.VoicesManager.create", new=create_voices):
            voices = await list_voices()

        self.assertIsInstance(voices, list)
        self.assertEqual(voices[0]["name"], "en-US-TestNeural")

    async def test_generate_audio(self):
        """测试音频生成功能"""
        class FakeCommunicate:
            def __init__(self, text, voice):
                self.text = text

            async def save(self, path):
                Path(path).write_bytes(b"\xff\xf3\x64\xc4")

        text_list = ["First sentence.", "Second sentence.", "Third sentence."]
        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "utils.audio_generator.AUDIO_DIR", Path(temp_dir) / "audios"
        ), patch("utils.audio_generator.edge_tts.Communicate", FakeCommunicate):
            audio_dir, filenames, warning_msg = await generate_audio(
                text_list, "en-US-TestNeural", "test"
            )

            self.assertEqual(len(text_list), len(filenames))
            self.assertEqual(audio_dir, Path(temp_dir) / "audios" / "test")
            self.assertTrue(audio_dir.exists())
            self.assertEqual(warning_msg, "")
            for i, filename in enumerate(filenames):
                self.assertIsNotNone(filename)
                self.assertTrue(audio_dir.joinpath(filename).exists())
                self.assertEqual(filename.split("_")[0], str(i + 1))
                self.assertEqual(filename.split(".")[1], "mp3")

    async def test_invalid_audio_is_retried_and_keeps_alignment(self):
        attempts = {}

        class FakeCommunicate:
            def __init__(self, text, voice):
                self.text = text

            async def save(self, path):
                attempts[self.text] = attempts.get(self.text, 0) + 1
                if self.text == "retry" and attempts[self.text] == 1:
                    raise RuntimeError("temporary")
                if self.text == "invalid":
                    Path(path).write_bytes(b"bad!")
                else:
                    Path(path).write_bytes(b"\xff\xf3\x64\xc4")

        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "utils.audio_generator.AUDIO_DIR", Path(temp_dir) / "audios"
        ), patch("utils.audio_generator.edge_tts.Communicate", FakeCommunicate), patch(
            "utils.audio_generator.asyncio.sleep", new=AsyncMock()
        ):
            audio_dir, filenames, warning_msg = await generate_audio(
                ["ok", "retry", "invalid"], "en-US-TestNeural", "test"
            )

        self.assertIsNotNone(filenames[0])
        self.assertIsNotNone(filenames[1])
        self.assertIsNone(filenames[2])
        self.assertEqual(attempts["retry"], 2)
        self.assertIn("第 3 个音频生成失败", warning_msg)

if __name__ == "__main__":
    unittest.main()
