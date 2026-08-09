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

# Deliberately allows a newline inside a span. These files are hard-wrapped, so
# `claude plugin\nlist` is ordinary Markdown that renders as one identifier, and
# a pattern anchored to the line does not merely miss such a span: it pairs that
# span's closing backtick with the next span's opening one and captures the
# prose between them. The census then holds a phantom entry no translation can
# reproduce without leaving a clause in English, and silently stops pinning the
# two real identifiers it existed for.
#
# No span in these six files wraps today, so nothing is mispinned. The problem
# is that this is true by accident, and the accident ends the first time someone
# rewraps a paragraph — in a commit that looks like prose editing.
INLINE_CODE = re.compile(r"`([^`]+)`")

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")

# A fence in one of these languages holds commands, paths, or settings. Every
# README must carry it character for character, whatever the surrounding prose.
VERBATIM_FENCES = frozenset({"bash", "json", "toml", ""})


def strip_fences(text: str) -> str:
    """Blank out fenced blocks, preserving line count.

    Required by the newline-tolerant pattern above, which would otherwise pair
    the backticks of two fence delimiters and swallow a whole block as a single
    enormous span. Fence content is compared verbatim by its own test, so the
    census loses nothing by not reading it.
    """
    out, fence = [], None
    for line in text.split("\n"):
        marker = FENCE.match(line)
        if marker:
            char = marker.group(1)[0]
            if fence is None:
                fence = char
            elif fence == char:
                fence = None
            out.append("")
            continue
        out.append("" if fence else line)
    return "\n".join(out)


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
    """Every inline code span, whitespace-normalized, fences excluded.

    Normalized because a span that survives a line break renders as one
    identifier, and the translation that fits it on one line is naming the same
    thing.
    """
    return collections.Counter(
        " ".join(span.split()) for span in INLINE_CODE.findall(strip_fences(text))
    )


def numbered_items(text: str) -> list[int]:
    return [
        int(match.group(1))
        for line in text.split("\n")
        if (match := NUMBERED_ITEM.match(line))
    ]


class CensusTest(unittest.TestCase):
    """The span census against the shapes that broke it in the sibling repo.

    These assert on constructed strings rather than on the READMEs, because the
    failure being guarded is one no current README exhibits. A gate whose only
    evidence is that the tree happens to pass it is a gate nobody can tell is
    working, and this one was silently exact for the wrong reason until the same
    pattern shipped a phantom span elsewhere.
    """

    def test_a_span_that_survives_a_line_break_is_one_identifier(self):
        wrapped = "Run `claude plugin\nlist` and check for `enabled`."
        flat = "Run `claude plugin list` and check for `enabled`."
        self.assertEqual(inline_code(wrapped), inline_code(flat))

    def test_the_prose_between_two_spans_is_never_captured(self):
        """The specific failure: pairing one span's closing backtick with the
        next span's opening one, so a clause of English enters the census."""
        census = inline_code("Run `claude plugin\nlist` and check for `enabled`.")
        self.assertEqual(census, collections.Counter({"claude plugin list": 1, "enabled": 1}))
        self.assertNotIn(" and check for ", census)

    def test_a_fenced_block_contributes_nothing(self):
        """Without stripping, the newline-tolerant pattern pairs the backticks
        of two fence delimiters and swallows the block as one span."""
        self.assertEqual(inline_code("```bash\nclaude --version\n```\n"), collections.Counter())

    def test_a_fence_between_two_spans_does_not_join_them(self):
        text = "See `alpha`.\n\n```bash\nrun me\n```\n\nThen `beta`.\n"
        self.assertEqual(inline_code(text), collections.Counter({"alpha": 1, "beta": 1}))

    def test_the_census_reads_the_real_readmes(self):
        """A helper that returned nothing would pass every assertion above."""
        self.assertGreater(sum(inline_code(ENGLISH.read_text(encoding="utf-8")).values()), 20)


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
