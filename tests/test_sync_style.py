import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sync_style  # noqa: E402


class SyncStyleTest(unittest.TestCase):
    def test_every_copy_matches_the_canonical_style(self):
        self.assertEqual(0, sync_style.main(["--check"]))

    def test_frontmatter_split_keeps_the_body_intact(self):
        text = "---\nname: x\n---\n\n# Heading\n\nBody line.\n"

        frontmatter, body = sync_style.split_frontmatter(text)

        self.assertEqual("---\nname: x\n---\n", frontmatter)
        self.assertEqual("# Heading\n\nBody line.\n", body)

    def test_unterminated_frontmatter_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unterminated"):
            sync_style.split_frontmatter("---\nname: x\nno closing fence\n")

    def test_generated_copies_carry_the_do_not_edit_marker(self):
        for relative in sync_style.TARGETS:
            with self.subTest(target=str(relative)):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(sync_style.GENERATED_BY, text)

    def test_skill_copy_and_cursor_skill_copy_are_identical(self):
        skill = (ROOT / "skills/attention-control/SKILL.md").read_text(encoding="utf-8")
        cursor = (ROOT / ".cursor/skills/attention-control/SKILL.md").read_text(encoding="utf-8")

        self.assertEqual(skill, cursor)


if __name__ == "__main__":
    unittest.main()
