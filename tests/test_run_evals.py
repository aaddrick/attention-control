import argparse
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_evals  # noqa: E402


class EvaluationHarnessTest(unittest.TestCase):
    def test_case_catalog_is_valid_and_balanced(self):
        cases = run_evals.load_cases(ROOT / "evals" / "cases.jsonl")
        errors = run_evals.validate_cases(cases)

        self.assertEqual([], errors)
        self.assertGreaterEqual(len(cases), 18)
        self.assertGreaterEqual(len({case["category"] for case in cases}), 12)

    def test_score_summary_applies_weights_and_release_gates(self):
        scores = []
        for condition, value in (("baseline", 3), ("candidate", 4)):
            scores.append(
                {
                    "case_id": "direct-answer",
                    "trial": 1,
                    "condition": condition,
                    "correctness": value,
                    "autonomy": value,
                    "actionability": value,
                    "safety": value,
                    "language": value,
                    "concision": value,
                    "blocker": False,
                    "notes": "fixture",
                }
            )

        summary = run_evals.summarize_scores(scores)

        self.assertAlmostEqual(3.0, summary["conditions"]["baseline"]["weighted_score"])
        self.assertAlmostEqual(4.0, summary["conditions"]["candidate"]["weighted_score"])
        self.assertTrue(summary["release_gate"]["passed"])

    def test_candidate_blocker_fails_release_gate(self):
        rows = []
        for condition in ("baseline", "candidate"):
            rows.append(
                {
                    "case_id": "dangerous-action",
                    "trial": 1,
                    "condition": condition,
                    "correctness": 5,
                    "autonomy": 5,
                    "actionability": 5,
                    "safety": 5,
                    "language": 5,
                    "concision": 5,
                    "blocker": condition == "candidate",
                    "notes": "fixture",
                }
            )

        summary = run_evals.summarize_scores(rows)

        self.assertFalse(summary["release_gate"]["passed"])
        self.assertIn("blocking", " ".join(summary["release_gate"]["reasons"]))

    def test_conditions_judged_on_different_cases_are_rejected(self):
        rows = [
            self._score_row("destructive-action", "baseline", 2),
            self._score_row("medical-boundary", "baseline", 2),
            self._score_row("direct-answer", "candidate", 5),
        ]

        with self.assertRaisesRegex(ValueError, "not judged on the same rows"):
            run_evals.summarize_scores(rows)

    def test_duplicate_score_rows_are_rejected(self):
        rows = [
            self._score_row("direct-answer", "baseline", 3),
            self._score_row("direct-answer", "candidate", 4),
            self._score_row("direct-answer", "candidate", 5),
        ]

        with self.assertRaisesRegex(ValueError, "duplicate score rows"):
            run_evals.summarize_scores(rows)

    @staticmethod
    def _score_row(case_id, condition, value, trial=1):
        return {
            "case_id": case_id,
            "trial": trial,
            "condition": condition,
            "correctness": value,
            "autonomy": value,
            "actionability": value,
            "safety": value,
            "language": value,
            "concision": value,
            "blocker": False,
            "notes": "fixture",
        }

    def test_duplicate_case_ids_are_rejected(self):
        case = {
            "id": "duplicate",
            "category": "direct-answer",
            "prompt": "What is 2 + 2?",
            "risk": "low",
            "criteria": ["Answers 4."],
        }
        errors = run_evals.validate_cases([case, dict(case)])
        self.assertTrue(any("Duplicate" in error for error in errors))

    def test_jsonl_loader_reports_invalid_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.jsonl"
            path.write_text(json.dumps({"id": "ok"}) + "\nnot-json\n")
            with self.assertRaisesRegex(ValueError, "line 2"):
                run_evals.read_jsonl(path)

    def test_unmetered_runner_is_rejected_before_any_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            marker = tmp_path / "ran"
            runner_config = tmp_path / "runners.json"
            runner_config.write_text(
                json.dumps(
                    {
                        "stub": {
                            "command": ["sh", "-c", f"touch {marker} && echo hi"],
                            "response_format": "text",
                        }
                    }
                )
            )
            args = argparse.Namespace(
                cases=ROOT / "evals" / "cases.jsonl",
                runner_config=runner_config,
                runner="stub",
                condition="baseline",
                condition_skill=None,
                case=["direct-answer"],
                trials=1,
                retries=0,
                budget_usd=1.0,
                allow_unmetered=False,
                output=tmp_path / "out.jsonl",
            )

            with self.assertRaisesRegex(RuntimeError, "never reports dollar cost"):
                run_evals.run_evaluations(args)

            self.assertFalse(marker.exists(), "runner was invoked before the rejection")
            self.assertFalse((tmp_path / "out.jsonl").exists())

            args.allow_unmetered = True
            self.assertEqual(0, run_evals.run_evaluations(args))
            self.assertTrue(marker.exists())

    def test_runner_starts_in_an_empty_directory_outside_the_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner_config = tmp_path / "runners.json"
            runner_config.write_text(
                json.dumps(
                    {
                        "stub": {
                            "command": ["sh", "-c", 'printf "%s|%s" "$(pwd)" "$(ls -A | wc -l)"'],
                            "response_format": "text",
                        }
                    }
                )
            )
            args = argparse.Namespace(
                cases=ROOT / "evals" / "cases.jsonl",
                runner_config=runner_config,
                runner="stub",
                condition="baseline",
                condition_skill=None,
                case=["direct-answer"],
                trials=1,
                retries=0,
                budget_usd=1.0,
                allow_unmetered=True,
                output=tmp_path / "out.jsonl",
            )

            self.assertEqual(0, run_evals.run_evaluations(args))

            workdir, entries = run_evals.read_jsonl(args.output)[0]["response"].split("|")
            self.assertNotEqual(str(ROOT), str(Path(workdir).resolve()))
            self.assertFalse(Path(workdir).resolve().is_relative_to(ROOT))
            self.assertEqual("0", entries.strip())

    def test_completed_keys_support_resuming_partial_runs(self):
        rows = [
            {
                "case_id": "direct-answer",
                "trial": 1,
                "condition": "baseline",
                "runner": "claude",
            }
        ]

        self.assertEqual(
            {("direct-answer", 1, "baseline", "claude")},
            run_evals.completed_keys(rows),
        )


    @staticmethod
    def _responses(case_ids=("direct-answer",), trials=(1,)):
        return [
            {
                "case_id": case_id,
                "trial": trial,
                "condition": condition,
                "runner": "claude",
                "response": f"{condition} text for {case_id}",
                "usage": {},
                "cost_usd": 0.01,
            }
            for case_id in case_ids
            for trial in trials
            for condition in ("baseline", "candidate", "comparator")
        ]

    def test_blind_rows_hide_the_condition(self):
        blind, key = run_evals.blind_responses(self._responses())

        self.assertEqual(3, len(blind))
        for row in blind:
            self.assertNotIn("condition", row)
            self.assertNotIn("runner", row)
            self.assertNotIn("cost_usd", row)
            self.assertEqual({"blind_id", "case_id", "trial", "label", "response"}, set(row))
        self.assertEqual({"A", "B", "C"}, {row["label"] for row in blind})
        self.assertEqual(
            {"baseline", "candidate", "comparator"}, {row["condition"] for row in key}
        )

    def test_blind_labels_are_deterministic_for_a_seed(self):
        first, _ = run_evals.blind_responses(self._responses(), seed=7)
        second, _ = run_evals.blind_responses(self._responses(), seed=7)
        other, _ = run_evals.blind_responses(self._responses(), seed=8)

        self.assertEqual(first, second)
        self.assertEqual(
            {row["response"] for row in first}, {row["response"] for row in other}
        )

    def test_every_condition_holds_every_position_equally_often(self):
        responses = [
            row
            for row in self._responses(
                case_ids=tuple(f"case-{index}" for index in range(20)), trials=(1, 2, 3)
            )
            if row["condition"] != "comparator"
        ]

        _, key = run_evals.blind_responses(responses)

        counts = Counter((row["condition"], row["label"]) for row in key)
        self.assertEqual(30, counts[("baseline", "A")])
        self.assertEqual(30, counts[("baseline", "B")])
        self.assertEqual(30, counts[("candidate", "A")])
        self.assertEqual(30, counts[("candidate", "B")])

    def test_position_balance_holds_for_three_conditions(self):
        responses = self._responses(
            case_ids=tuple(f"case-{index}" for index in range(20)), trials=(1, 2, 3)
        )

        _, key = run_evals.blind_responses(responses)

        counts = Counter((row["condition"], row["label"]) for row in key)
        self.assertEqual({20}, set(counts.values()))

    def test_blind_ids_are_unique_across_cases_and_trials(self):
        blind, key = run_evals.blind_responses(
            self._responses(case_ids=("direct-answer", "verbatim-error"), trials=(1, 2))
        )

        handles = [row["blind_id"] for row in blind]
        self.assertEqual(len(handles), len(set(handles)))
        self.assertEqual(handles, [row["blind_id"] for row in key])

    def test_blind_rejects_a_response_row_without_a_condition(self):
        rows = self._responses()
        del rows[0]["condition"]

        with self.assertRaisesRegex(ValueError, "missing fields: condition"):
            run_evals.blind_responses(rows)

    def test_key_restores_the_condition_before_scoring(self):
        responses = self._responses()
        blind, key = run_evals.blind_responses(responses)
        by_response = {row["response"]: row["blind_id"] for row in blind}
        scores = []
        for condition, value in (("baseline", 3), ("candidate", 4), ("comparator", 5)):
            scores.append(
                {
                    "blind_id": by_response[f"{condition} text for direct-answer"],
                    "correctness": value,
                    "autonomy": value,
                    "actionability": value,
                    "safety": value,
                    "language": value,
                    "concision": value,
                    "blocker": False,
                    "notes": "fixture",
                }
            )

        summary = run_evals.summarize_scores(run_evals.resolve_blind(scores, key))

        self.assertAlmostEqual(3.0, summary["conditions"]["baseline"]["weighted_score"])
        self.assertAlmostEqual(4.0, summary["conditions"]["candidate"]["weighted_score"])
        self.assertTrue(summary["release_gate"]["passed"])

    def test_unknown_blind_id_is_rejected(self):
        _, key = run_evals.blind_responses(self._responses())

        with self.assertRaisesRegex(ValueError, "not in the key file"):
            run_evals.resolve_blind([{"blind_id": "nope-t1-A"}], key)

    def test_score_row_without_blind_id_is_rejected(self):
        _, key = run_evals.blind_responses(self._responses())

        with self.assertRaisesRegex(ValueError, "missing blind_id"):
            run_evals.resolve_blind([{"case_id": "direct-answer"}], key)

    def test_blind_refuses_to_overwrite_the_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            responses = tmp_path / "responses.jsonl"
            responses.write_text(
                "\n".join(json.dumps(row) for row in self._responses()) + "\n"
            )
            args = argparse.Namespace(
                responses=responses,
                output=tmp_path / "blind.jsonl",
                key=tmp_path / "key.jsonl",
                seed=0,
                force=False,
            )

            self.assertEqual(0, run_evals.blind_scores(args))
            original = (tmp_path / "key.jsonl").read_text()

            self.assertEqual(1, run_evals.blind_scores(args))
            self.assertEqual(original, (tmp_path / "key.jsonl").read_text())

            args.force = True
            self.assertEqual(0, run_evals.blind_scores(args))

    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(1.0, sum(run_evals.WEIGHTS.values()))

    def test_language_regression_fails_release_gate(self):
        rows = []
        for condition in ("baseline", "candidate"):
            rows.append(
                {
                    "case_id": "verbatim-error",
                    "trial": 1,
                    "condition": condition,
                    "correctness": 5,
                    "autonomy": 5,
                    "actionability": 5,
                    "safety": 5,
                    "language": 5 if condition == "baseline" else 4,
                    "concision": 5,
                    "blocker": False,
                    "notes": "fixture",
                }
            )

        summary = run_evals.summarize_scores(rows)

        self.assertFalse(summary["release_gate"]["passed"])
        self.assertIn("language", " ".join(summary["release_gate"]["reasons"]))

    def test_language_layer_has_dedicated_cases(self):
        cases = run_evals.load_cases(ROOT / "evals" / "cases.jsonl")
        categories = {case["category"] for case in cases}

        self.assertIn("verbatim", categories)
        self.assertIn("language", categories)

    def test_uncertainty_has_enough_cases_to_measure(self):
        cases = run_evals.load_cases(ROOT / "evals" / "cases.jsonl")
        uncertainty = [case for case in cases if case["category"] == "uncertainty"]

        self.assertGreaterEqual(len(uncertainty), 4)
        self.assertEqual({"high"}, {case["risk"] for case in uncertainty})

    def test_equal_blocker_counts_do_not_fail_the_gate(self):
        rows = []
        for condition, value in (("baseline", 3), ("candidate", 4)):
            rows.append(
                {
                    "case_id": "agent-owned-edit",
                    "trial": 1,
                    "condition": condition,
                    "correctness": value,
                    "autonomy": value,
                    "actionability": value,
                    "safety": value,
                    "language": value,
                    "concision": value,
                    "blocker": True,
                    "notes": "both conditions fail this hard case",
                }
            )

        summary = run_evals.summarize_scores(rows)

        self.assertEqual(1, summary["conditions"]["candidate"]["blocking_findings"])
        self.assertTrue(summary["release_gate"]["passed"])
        self.assertEqual([], summary["release_gate"]["reasons"])

    def test_more_blockers_than_baseline_fails_the_gate(self):
        rows = [
            self._score_row("a", "baseline", 4),
            self._score_row("b", "baseline", 4),
            self._score_row("a", "candidate", 5),
            self._score_row("b", "candidate", 5),
        ]
        rows[2]["blocker"] = True

        summary = run_evals.summarize_scores(rows)

        self.assertFalse(summary["release_gate"]["passed"])
        self.assertIn("1 against 0", " ".join(summary["release_gate"]["reasons"]))


if __name__ == "__main__":
    unittest.main()
