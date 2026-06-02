"""Tests for WhiskerShelf app. Uses stdlib unittest only."""
import json
import tempfile
import unittest
from pathlib import Path

from app import build_cc_project


class SanityTest(unittest.TestCase):
    def test_truth(self):
        self.assertTrue(True)


class BuildCCProjectTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.session = {
            "id": "1234567890",
            "time": 1234567890,
            "papers": [
                {"name": "a.pdf", "title": "Paper A", "abstract": "Abs A",
                 "tags": ["linear-attention"], "notes": ""},
                {"name": "b.pdf", "title": "Paper B", "abstract": "Abs B",
                 "tags": ["snn"], "notes": ""},
            ],
            "user_context": "test context",
            "result": "# Brief\n\n## 1. Common themes\n..."
        }

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_directory(self):
        target = Path(self.tmp) / "brief-1234"
        result_path = build_cc_project(self.session, target)
        self.assertTrue(result_path.exists())
        self.assertTrue(result_path.is_dir())

    def test_writes_brief_md(self):
        target = Path(self.tmp) / "brief-1234"
        result_path = build_cc_project(self.session, target)
        self.assertEqual((result_path / "brief.md").read_text(encoding="utf-8"),
                         self.session["result"])

    def test_writes_selected_papers_json(self):
        target = Path(self.tmp) / "brief-1234"
        result_path = build_cc_project(self.session, target)
        data = json.loads((result_path / "selected-papers.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "a.pdf")

    def test_writes_claude_md_with_skills_section(self):
        target = Path(self.tmp) / "brief-1234"
        result_path = build_cc_project(self.session, target)
        claude_md = (result_path / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("whiskershelf-brief", claude_md)
        self.assertIn("whiskershelf-search", claude_md)
        self.assertIn("whiskershelf-tag", claude_md)

    def test_writes_start_claude_bat(self):
        target = Path(self.tmp) / "brief-1234"
        result_path = build_cc_project(self.session, target)
        bat = (result_path / "start-claude.bat").read_text(encoding="utf-8")
        self.assertIn("claude", bat.lower())

    def test_writes_start_claude_sh(self):
        target = Path(self.tmp) / "brief-1234"
        result_path = build_cc_project(self.session, target)
        sh = (result_path / "start-claude.sh").read_text(encoding="utf-8")
        self.assertIn("claude", sh.lower())

    def test_copies_skill_files(self):
        target = Path(self.tmp) / "brief-1234"
        result_path = build_cc_project(self.session, target)
        skills_dir = result_path / ".claude" / "skills"
        self.assertTrue((skills_dir / "whiskershelf-brief" / "SKILL.md").exists())
        self.assertTrue((skills_dir / "whiskershelf-search" / "SKILL.md").exists())
        self.assertTrue((skills_dir / "whiskershelf-tag" / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
