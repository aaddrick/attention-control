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


class IsolationPromptTest(unittest.TestCase):
    """The isolation prompt must not contradict a premise a case states.

    An early version told the runner "You have no tools, no files, no
    repository, and no workspace." The `agent-owned-edit` case tells it "you
    have access to the repository." Every response denied the premise, scored
    1.0 on autonomy under both conditions, and drew a blocking finding. The
    prompt that protected the run from the environment contaminated the run
    instead.
    """

    DENIALS = ("no tools", "no files", "no repository", "no workspace", "have no")

    def _system_prompt(self):
        config = json.loads((ROOT / "evals" / "runners.example.json").read_text(encoding="utf-8"))
        command = config["claude"]["command"]
        return command[command.index("--system-prompt") + 1]

    def test_prompt_denies_no_capability_a_case_asserts(self):
        prompt = self._system_prompt().lower()
        found = [phrase for phrase in self.DENIALS if phrase in prompt]

        self.assertEqual([], found, f"the isolation prompt denies a stated premise: {found}")

    def test_prompt_still_forbids_inspecting_the_environment(self):
        prompt = self._system_prompt().lower()

        self.assertIn("never describe, attempt, or reference a command", prompt)
        self.assertIn("answer from the message alone", prompt)

    def test_prompt_tells_the_runner_to_accept_stated_premises(self):
        self.assertIn("accept the premises", self._system_prompt().lower())

    def test_every_runner_pins_a_model(self):
        config = json.loads((ROOT / "evals" / "runners.example.json").read_text(encoding="utf-8"))
        metered = {
            name: runner
            for name, runner in config.items()
            if runner.get("response_format") == "claude-json"
        }
        self.assertTrue(metered, "expected at least one cost-reporting runner")
        for name, runner in metered.items():
            with self.subTest(runner=name):
                self.assertIsNotNone(run_evals.runner_model(runner["command"]))


class ProvenanceTest(unittest.TestCase):
    """Every response row records what produced it.

    evals/README.md requires a recorded model beside any published number. The
    first full run carried none, so nothing links its results to a model.
    """

    def test_model_is_read_from_the_runner_command(self):
        self.assertEqual("claude-sonnet-5", run_evals.runner_model(["claude", "--model", "claude-sonnet-5"]))
        self.assertEqual("x", run_evals.runner_model(["claude", "--model=x"]))
        self.assertEqual("y", run_evals.runner_model(["claude", "-m", "y"]))
        self.assertIsNone(run_evals.runner_model(["claude", "--print"]))
        self.assertIsNone(run_evals.runner_model(["claude", "--model"]))

    def test_style_hash_separates_the_conditions(self):
        with tempfile.TemporaryDirectory() as tmp:
            style = Path(tmp) / "style.md"
            style.write_text("be brief")
            command = ["claude", "--model", "m"]
            cases = ROOT / "evals" / "cases.jsonl"

            baseline = run_evals.provenance(command, cases, None)
            candidate = run_evals.provenance(command, cases, style)

            self.assertIsNone(baseline["style_sha256"])
            self.assertIsNotNone(candidate["style_sha256"])
            self.assertEqual(baseline["cases_sha256"], candidate["cases_sha256"])

    def test_drift_names_every_field_that_changed(self):
        prior = [
            {
                "condition": "candidate",
                "model": "old",
                "runner_sha256": "a",
                "cases_sha256": "b",
                "style_sha256": "c",
            }
        ]
        current = {
            "model": "new",
            "runner_sha256": "a",
            "cases_sha256": "b",
            "style_sha256": "z",
        }

        self.assertEqual(["model", "style_sha256"], run_evals.check_provenance(prior, current, "candidate"))
        self.assertEqual([], run_evals.check_provenance(prior, current, "baseline"))

    def test_run_records_provenance_and_refuses_to_resume_after_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner_config = tmp_path / "runners.json"
            runner_config.write_text(
                json.dumps(
                    {
                        "stub": {
                            "command": ["sh", "-c", "echo hi", "--model", "stub-1"],
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
                split="all",
                trials=1,
                retries=0,
                budget_usd=1.0,
                allow_unmetered=True,
                allow_unpinned_model=False,
                allow_provenance_drift=False,
                output=tmp_path / "out.jsonl",
            )

            self.assertEqual(0, run_evals.run_evaluations(args))
            row = run_evals.read_jsonl(args.output)[0]
            self.assertEqual("stub-1", row["model"])
            for field in run_evals.PROVENANCE_FIELDS:
                self.assertIn(field, row)

            # Repin the model, then resume into the same file.
            runner_config.write_text(
                json.dumps(
                    {
                        "stub": {
                            "command": ["sh", "-c", "echo hi", "--model", "stub-2"],
                            "response_format": "text",
                        }
                    }
                )
            )
            args.case = ["code-answer"]
            with self.assertRaisesRegex(RuntimeError, "different model"):
                run_evals.run_evaluations(args)

            args.allow_provenance_drift = True
            self.assertEqual(0, run_evals.run_evaluations(args))
            self.assertEqual(
                {"stub-1", "stub-2"},
                {row["model"] for row in run_evals.read_jsonl(args.output)},
            )

    def test_run_refuses_an_unpinned_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner_config = tmp_path / "runners.json"
            runner_config.write_text(
                json.dumps({"stub": {"command": ["echo", "hi"], "response_format": "text"}})
            )
            args = argparse.Namespace(
                cases=ROOT / "evals" / "cases.jsonl",
                runner_config=runner_config,
                runner="stub",
                condition="baseline",
                condition_skill=None,
                case=["direct-answer"],
                split="all",
                trials=1,
                retries=0,
                budget_usd=1.0,
                allow_unmetered=True,
                allow_unpinned_model=False,
                allow_provenance_drift=False,
                output=tmp_path / "out.jsonl",
            )

            with self.assertRaisesRegex(RuntimeError, "pins no --model"):
                run_evals.run_evaluations(args)
            self.assertFalse(args.output.exists())

    def test_blinding_never_carries_provenance_to_the_judge(self):
        """The style hash differs by condition, so it names the condition."""
        responses = []
        for condition, style in (("baseline", None), ("candidate", "deadbeef")):
            responses.append(
                {
                    "case_id": "direct-answer",
                    "trial": 1,
                    "condition": condition,
                    "runner": "claude",
                    "model": "m",
                    "runner_sha256": "r",
                    "cases_sha256": "c",
                    "style_sha256": style,
                    "response": "102",
                    "cost_usd": 0.01,
                }
            )

        blind, key = run_evals.blind_responses(responses)

        for row in blind:
            self.assertEqual(
                {"blind_id", "case_id", "trial", "label", "response"},
                set(row),
                "a blinded row carried a field the judge must not see",
            )
        self.assertEqual({"baseline", "candidate"}, {row["condition"] for row in key})


class CaseSplitTest(unittest.TestCase):
    """The dev set is what you tune against. The holdout is what checks you.

    Tuning a style against a fixed case set until the release gate passes
    measures memorization of those cases. Only a set you never iterated
    against separates a better style from a better fit.
    """

    def setUp(self):
        self.cases = run_evals.load_cases(ROOT / "evals" / "cases.jsonl")

    def test_every_case_declares_a_split(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertIn(case["split"], run_evals.SPLITS)

    def test_holdout_is_smaller_than_dev_and_large_enough_to_matter(self):
        counts = Counter(case["split"] for case in self.cases)

        self.assertGreaterEqual(counts["holdout"], 4)
        self.assertLess(counts["holdout"], counts["dev"])

    def test_holdout_covers_categories_the_dev_set_also_covers(self):
        """A holdout category absent from dev cannot detect overfitting in it."""
        dev = {case["category"] for case in self.cases if case["split"] == "dev"}
        holdout = {case["category"] for case in self.cases if case["split"] == "holdout"}

        self.assertGreaterEqual(len(holdout & dev), 4)

    def test_validate_rejects_a_missing_split(self):
        broken = [{k: v for k, v in case.items() if k != "split"} for case in self.cases]

        errors = run_evals.validate_cases(broken)

        self.assertTrue(any("split" in error for error in errors))

    def test_validate_rejects_a_holdout_that_swallows_the_dev_set(self):
        broken = [{**case, "split": "holdout"} for case in self.cases]

        errors = run_evals.validate_cases(broken)

        self.assertTrue(any("not smaller than the dev set" in error for error in errors))

    def test_validate_rejects_an_unknown_split(self):
        broken = [{**case, "split": "train"} for case in self.cases]

        errors = run_evals.validate_cases(broken)

        self.assertTrue(any("split must be one of" in error for error in errors))


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
            "split": "dev",
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
                split="all",
                trials=1,
                retries=0,
                budget_usd=1.0,
                allow_unmetered=False,
                allow_unpinned_model=True,
                allow_provenance_drift=False,
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
                split="all",
                trials=1,
                retries=0,
                budget_usd=1.0,
                allow_unmetered=True,
                allow_unpinned_model=True,
                allow_provenance_drift=False,
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
