import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import judge  # noqa: E402


VERDICT = (
    '[{"label":"A","correctness":5,"autonomy":4,"actionability":5,"safety":5,'
    '"language":4,"concision":3,"blocker":false,"notes":"Direct."},'
    '{"label":"B","correctness":3,"autonomy":3,"actionability":2,"safety":5,'
    '"language":2,"concision":2,"blocker":false,"notes":"Buried the answer."}]'
)


class JudgeTest(unittest.TestCase):
    def test_parses_a_bare_json_array(self):
        verdicts = judge.parse_verdicts(VERDICT, {"A", "B"})

        self.assertEqual(2, len(verdicts))
        self.assertEqual(5, verdicts[0]["correctness"])

    def test_parses_a_fenced_array_with_surrounding_prose(self):
        text = f"Here are the scores:\n\n```json\n{VERDICT}\n```\n"

        verdicts = judge.parse_verdicts(text, {"A", "B"})

        self.assertEqual({"A", "B"}, {verdict["label"] for verdict in verdicts})

    def test_rejects_a_missing_label(self):
        with self.assertRaisesRegex(ValueError, "expected"):
            judge.parse_verdicts(VERDICT, {"A", "B", "C"})

    def test_rejects_an_out_of_range_score(self):
        text = VERDICT.replace('"correctness":5', '"correctness":9')

        with self.assertRaisesRegex(ValueError, "correctness=9"):
            judge.parse_verdicts(text, {"A", "B"})

    def test_rejects_text_without_any_json(self):
        with self.assertRaisesRegex(ValueError, "no JSON objects"):
            judge.parse_verdicts("I cannot score these.", {"A"})

    def test_parses_objects_returned_one_per_line(self):
        text = "\n".join(VERDICT.strip("[]").split("},{")).replace("\n", "}\n{")
        text = VERDICT[1:-1].replace("},{", "}\n{")

        verdicts = judge.parse_verdicts(text, {"A", "B"})

        self.assertEqual({"A", "B"}, {verdict["label"] for verdict in verdicts})

    def test_parses_objects_with_prose_between_them(self):
        first, second = VERDICT[1:-1].split("},{")
        text = f"Scores:\n{first}}}\n\nAnd the second:\n{{{second}\nDone."

        verdicts = judge.parse_verdicts(text, {"A", "B"})

        self.assertEqual(2, len(verdicts))

    def test_rubric_hides_the_release_gate_from_the_judge(self):
        rubric = (ROOT / "evals" / "rubric.md").read_text(encoding="utf-8")

        trimmed = judge.judgeable_rubric(rubric)

        self.assertIn("Language checklist", trimmed)
        self.assertIn("Correctness", trimmed)
        self.assertNotIn("Release gate", trimmed)
        self.assertNotIn("baseline", trimmed)
        self.assertNotIn("candidate", trimmed)

    def test_passes_average_into_one_score_row(self):
        rows = [
            {"blind_id": "x-t1-A", "pass": 0, "blocker": False, "notes": "first", **self._metrics(4)},
            {"blind_id": "x-t1-A", "pass": 1, "blocker": True, "notes": "second", **self._metrics(2)},
        ]

        aggregated = judge.aggregate_passes(rows)

        self.assertEqual(1, len(aggregated))
        self.assertEqual(3.0, aggregated[0]["correctness"])
        self.assertTrue(aggregated[0]["blocker"])
        self.assertEqual("first", aggregated[0]["notes"])
        self.assertEqual(2, aggregated[0]["passes"])

    def test_flip_rate_counts_groups_where_the_winner_changed(self):
        rows = [
            self._judgement("stable", 0, "A", 5),
            self._judgement("stable", 0, "B", 3),
            self._judgement("stable", 1, "A", 5),
            self._judgement("stable", 1, "B", 3),
            self._judgement("flipped", 0, "A", 5),
            self._judgement("flipped", 0, "B", 3),
            self._judgement("flipped", 1, "A", 2),
            self._judgement("flipped", 1, "B", 4),
        ]

        stability = judge.winner_flip_rate(rows)

        self.assertEqual(2, stability["groups_compared"])
        self.assertEqual(1, stability["groups_flipped"])
        self.assertEqual(0.5, stability["flip_rate"])

    def test_flip_rate_sets_ties_aside(self):
        rows = [
            self._judgement("tied", 0, "A", 4),
            self._judgement("tied", 0, "B", 4),
            self._judgement("tied", 1, "A", 5),
            self._judgement("tied", 1, "B", 3),
        ]

        stability = judge.winner_flip_rate(rows)

        self.assertEqual(0, stability["groups_compared"])
        self.assertEqual(1, stability["groups_tied"])
        self.assertIsNone(stability["flip_rate"])

    @staticmethod
    def _metrics(value):
        return {
            "correctness": value,
            "autonomy": value,
            "actionability": value,
            "safety": value,
            "language": value,
            "concision": value,
        }

    @classmethod
    def _judgement(cls, case_id, index, label, value):
        return {
            "blind_id": f"{case_id}-t1-{label}",
            "case_id": case_id,
            "trial": 1,
            "label": label,
            "pass": index,
            "blocker": False,
            "notes": "fixture",
            **cls._metrics(value),
        }

    def test_prompt_carries_the_case_criteria_and_every_label(self):
        case = {"id": "x", "prompt": "Do the thing.", "criteria": ["Does it.", "Says so."]}
        rows = [
            {"label": "A", "response": "first answer"},
            {"label": "B", "response": "second answer"},
        ]

        prompt = judge.build_prompt("RUBRIC BODY", case, rows)

        self.assertIn("RUBRIC BODY", prompt)
        self.assertIn("Do the thing.", prompt)
        self.assertIn("- Says so.", prompt)
        self.assertIn('<response label="A">', prompt)
        self.assertIn('<response label="B">', prompt)
        self.assertNotIn("condition", prompt)


if __name__ == "__main__":
    unittest.main()
