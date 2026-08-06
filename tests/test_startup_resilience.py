import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


class TestStartupResilience(unittest.TestCase):
    def test_app_import_does_not_import_translators(self):
        # Use a clean interpreter because another legacy test may import the
        # optional package at collection time.
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-c", "import sys; import app; print('translators' in sys.modules)"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "False")

    def test_translation_falls_back_without_network(self):
        from utils.text_translator import get_text_translated

        with patch("utils.text_translator._load_translators", return_value=None):
            self.assertEqual(get_text_translated(["one", "two"]), ["one", "two"])

    def test_resources_are_independent_of_current_directory(self):
        from utils.runtime import APP_DIR, resource_path

        self.assertEqual(resource_path("static"), APP_DIR / "static")
        self.assertTrue(resource_path("templates").is_dir())

    def test_sentencex_is_local_and_available(self):
        import sentencex

        self.assertEqual(list(sentencex.segment("en", "One sentence.")), ["One sentence."])


if __name__ == "__main__":
    unittest.main()
