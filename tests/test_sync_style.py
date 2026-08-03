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

    def test_snippet_carries_every_shape_rule_in_canonical_order(self):
        body = self._canonical_body()
        rules = sync_style.numbered_rules(
            sync_style.section(body, "Shape rules"), "Shape rules"
        )

        snippet = sync_style.build_snippet(body)

        for number, (headword, _) in enumerate(rules, 1):
            self.assertIn(f"{number}. {headword}", snippet)

    def test_snippet_carries_every_exception(self):
        body = self._canonical_body()
        exceptions = sync_style.numbered_rules(
            sync_style.section(body, "When to break the rules"), "When to break the rules"
        )

        snippet = sync_style.build_snippet(body)

        for headword, _ in exceptions:
            self.assertIn(f"**{headword}**", snippet)

    def test_snippet_keeps_the_rule_against_inventing_a_specific(self):
        snippet = sync_style.build_snippet(self._canonical_body())

        self.assertIn("Never invent a specific to fill the gap.", snippet)

    def test_a_reworded_rule_fails_the_run_instead_of_dropping_out(self):
        body = self._canonical_body().replace(
            "- Limit noun clusters to 3 words.", "- Keep noun clusters to 3 words."
        )

        with self.assertRaisesRegex(ValueError, "Limit noun clusters"):
            sync_style.build_snippet(body)

    def test_renumbered_shape_rules_fail_the_run(self):
        body = self._canonical_body().replace(
            "2. **Do the work you own.**", "12. **Do the work you own.**"
        )

        with self.assertRaisesRegex(ValueError, "numbering"):
            sync_style.build_snippet(body)

    def test_install_snippet_section_is_regenerated_between_the_markers(self):
        text = (ROOT / "INSTALL.md").read_text(encoding="utf-8")

        self.assertIn(sync_style.SNIPPET_BEGIN, text)
        self.assertIn(sync_style.SNIPPET_END, text)
        self.assertIn(sync_style.build_snippet(self._canonical_body()), text)

    def _canonical_body(self):
        _, body = sync_style.split_frontmatter(
            sync_style.CANONICAL.read_text(encoding="utf-8")
        )
        return body

    def test_agents_md_mirrors_claude_md(self):
        # Two file names, one text. A tool reads whichever it knows, and the
        # pair cannot drift because one is generated from the other.
        for target, source in sync_style.MIRRORS.items():
            with self.subTest(target=str(target)):
                mirror = (ROOT / target).read_text(encoding="utf-8")
                original = (ROOT / source).read_text(encoding="utf-8")

                self.assertIn(sync_style.MIRROR_GENERATED_BY, mirror)
                body = mirror.replace(sync_style.MIRROR_GENERATED_BY, "", 1)
                self.assertEqual(original.split(), body.split())

    def test_the_root_agents_file_is_the_repository_guide(self):
        # AGENTS.md tells an agent how to work on this repository. It is not a
        # copy of the style. A tool that reads it must learn the one rule that
        # breaks the build before it edits anything.
        root = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("Never edit a generated file.", root)
        self.assertIn("scripts/sync_style.py", root)

    def test_skill_copy_and_cursor_skill_copy_are_identical(self):
        skill = (ROOT / "skills/attention-control/SKILL.md").read_text(encoding="utf-8")
        cursor = (ROOT / ".cursor/skills/attention-control/SKILL.md").read_text(encoding="utf-8")

        self.assertEqual(skill, cursor)


if __name__ == "__main__":
    unittest.main()
