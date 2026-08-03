"""The five translated READMEs mirror the English one. Nothing else checks them.

A translation drifts in silence. The rules renumber, an install command changes,
and the English README is the only file anyone rereads. Both drifts have already
happened here: the translations carried 10 shape rules and a stale skill name
while CI stayed green.

These assertions cover the two drifts that reach a reader as a wrong command or
a missing rule. They do not check the prose. A translator still owns that.
"""

import collections
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sync_style  # noqa: E402


ENGLISH = ROOT / "README.md"
TRANSLATIONS = sorted((ROOT / ".github" / "readme").glob("README.*.md"))

NUMBERED_ITEM = re.compile(r"^(\d+)\. ")
INLINE_CODE = re.compile(r"`([^`\n]+)`")

# A fence in one of these languages holds commands, paths, or settings. Every
# README must carry it character for character, whatever the surrounding prose.
VERBATIM_FENCES = frozenset({"bash", "json", "toml", ""})


def fenced_lines(text: str) -> list[str]:
    lines: list[str] = []
    inside = False
    language = ""
    for line in text.split("\n"):
        if line.startswith("```"):
            inside = not inside
            language = line[3:].strip() if inside else ""
            continue
        if inside and language in VERBATIM_FENCES and line.strip():
            lines.append(line.strip())
    return lines


def inline_code(text: str) -> collections.Counter:
    return collections.Counter(INLINE_CODE.findall(text))


def numbered_items(text: str) -> list[int]:
    return [
        int(match.group(1))
        for line in text.split("\n")
        if (match := NUMBERED_ITEM.match(line))
    ]


class ReadmeTest(unittest.TestCase):
    def setUp(self):
        self.english = ENGLISH.read_text(encoding="utf-8")

    def test_the_translations_exist(self):
        self.assertEqual(5, len(TRANSLATIONS))

    def test_every_translation_carries_the_same_commands(self):
        expected = fenced_lines(self.english)
        self.assertTrue(expected, "the English README lists no commands")

        for path in TRANSLATIONS:
            with self.subTest(readme=path.name):
                self.assertEqual(
                    expected,
                    fenced_lines(path.read_text(encoding="utf-8")),
                    "a command block drifted from README.md",
                )

    def test_every_readme_names_the_same_code(self):
        # The before/after example is a blockquote, not a fence, so the fence
        # test above cannot see it. Its commands, paths, and identifiers still
        # have to survive translation. Compare the code spans as a multiset:
        # Japanese and Korean reorder them inside a sentence, and word order is
        # the translator's business. A dropped or renamed one is not.
        expected = inline_code(self.english)
        self.assertTrue(expected, "the English README names no code")

        for path in TRANSLATIONS:
            with self.subTest(readme=path.name):
                found = inline_code(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    expected,
                    found,
                    f"missing: {expected - found} / extra: {found - expected}",
                )

    def test_every_readme_lists_every_shape_rule(self):
        _, body = sync_style.split_frontmatter(
            sync_style.CANONICAL.read_text(encoding="utf-8")
        )
        count = len(sync_style.numbered_rules(
            sync_style.section(body, "Shape rules"), "Shape rules"
        ))
        expected = list(range(1, count + 1))

        # Every README carries exactly one numbered list: the shape rules. A new
        # numbered list elsewhere fails this on purpose, so the count stays a
        # deliberate choice rather than a coincidence.
        for path in [ENGLISH, *TRANSLATIONS]:
            with self.subTest(readme=path.name):
                self.assertEqual(
                    expected,
                    numbered_items(path.read_text(encoding="utf-8")),
                    f"expected the {count} canonical shape rules, numbered 1..{count}",
                )


if __name__ == "__main__":
    unittest.main()
