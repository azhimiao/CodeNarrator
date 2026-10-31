import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def invoke(self, parent, *options):
        return subprocess.run([sys.executable, str(ROOT / "scripts/install_skill.py"), "--skills-dir", str(parent), *options],
                              capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8":"1"})

    def test_install_refuse_overwrite_and_explicit_upgrade_preserves_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            self.assertEqual(self.invoke(parent).returncode, 0)
            installed = parent / "code-narrator"
            (installed / "local-notes.txt").write_text("keep old", encoding="utf-8")
            self.assertEqual(self.invoke(parent).returncode, 1)
            result = self.invoke(parent, "--update")
            self.assertEqual(result.returncode, 0, result.stderr)
            backups = list(parent.glob("code-narrator.backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].suffix, ".zip")
            with zipfile.ZipFile(backups[0]) as archive:
                self.assertEqual(archive.read("local-notes.txt"), b"keep old")
            self.assertFalse((installed / "local-notes.txt").exists())
            for path in (ROOT / "code-narrator").rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                    self.assertEqual(path.read_bytes(), (installed / path.relative_to(ROOT / "code-narrator")).read_bytes())

    def test_update_refuses_unidentified_existing_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            existing = parent / "code-narrator"
            existing.mkdir()
            (existing / "keep.txt").write_text("unchanged")
            self.assertNotEqual(self.invoke(parent, "--update").returncode, 0)
            self.assertEqual((existing / "keep.txt").read_text(), "unchanged")
            self.assertFalse(list(parent.glob("code-narrator.backup-*")))


if __name__ == "__main__":
    unittest.main()
