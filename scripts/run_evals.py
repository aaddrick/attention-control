#!/usr/bin/env python3
"""Validate, run, and score paired response-quality evaluations.

Derived from ayghri/i-have-adhd (MIT). Changes: a `language` dimension that
scores the controlled-English layer, reweighted dimensions, a release gate that
also blocks a candidate whose language score does not beat baseline, and a
`blind` command that hides the condition from the judge.
"""

from __future__ import annotations

import argparse
import json
import shlex
import string
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "cases.jsonl"
WEIGHTS = {
    "correctness": 0.30,
    "autonomy": 0.20,
    "actionability": 0.20,
    "safety": 0.10,
    "language": 0.10,
    "concision": 0.10,
}
CONDITIONS = {"baseline", "candidate", "comparator"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: line {number}: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}: line {number}: expected a JSON object")
        rows.append(row)
    return rows


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    return read_jsonl(path)


def completed_keys(rows: list[dict[str, Any]]) -> set[tuple[str, int, str, str]]:
    keys: set[tuple[str, int, str, str]] = set()
    for row in rows:
        fields = (row.get("case_id"), row.get("trial"), row.get("condition"), row.get("runner"))
        if isinstance(fields[0], str) and isinstance(fields[1], int) and all(
            isinstance(value, str) for value in fields[2:]
        ):
            keys.add(fields)  # type: ignore[arg-type]
    return keys


def _blind_id(case_id: str, trial: int, label: str) -> str:
    """A judge-visible handle that carries no signal about the condition."""
    return f"{case_id}-t{trial}-{label}"


def blind_responses(
    responses: list[dict[str, Any]], seed: int = 0
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split responses into (blind rows, key rows).

    Rows for one (case_id, trial) form a group. The function orders each group
    and labels its rows A, B, C, so a judge reads every condition for one case
    side by side without learning which is which.

    Position matters. A judge reverses its verdict on 46.3% of pairs when the
    two candidates swap places and nothing else changes, so a condition that
    always appears first would win on layout rather than merit. Random shuffling
    balances positions only in expectation. This function rotates each group by
    its index instead, so every condition holds every position an equal number
    of times across the run, off by at most one. The seed shifts the rotation
    without breaking that balance.
    """
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for index, row in enumerate(responses, start=1):
        missing = sorted({"case_id", "trial", "condition", "response"} - set(row))
        if missing:
            raise ValueError(f"Response row {index}: missing fields: {', '.join(missing)}")
        grouped[(row["case_id"], row["trial"])].append(row)

    blind: list[dict[str, Any]] = []
    key: list[dict[str, Any]] = []
    for index, ((case_id, trial), rows) in enumerate(sorted(grouped.items())):
        if len(rows) > len(string.ascii_uppercase):
            raise ValueError(
                f"{case_id}/trial {trial}: {len(rows)} responses exceed the 26 available labels"
            )
        order = sorted(rows, key=lambda row: str(row["condition"]))
        offset = (index + seed) % len(order)
        order = order[offset:] + order[:offset]
        for label, row in zip(string.ascii_uppercase, order):
            handle = _blind_id(case_id, trial, label)
            blind.append(
                {
                    "blind_id": handle,
                    "case_id": case_id,
                    "trial": trial,
                    "label": label,
                    "response": row["response"],
                }
            )
            key.append(
                {
                    "blind_id": handle,
                    "case_id": case_id,
                    "trial": trial,
                    "label": label,
                    "condition": row["condition"],
                    "runner": row.get("runner"),
                }
            )
    return blind, key


def resolve_blind(
    scores: list[dict[str, Any]], key_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Replace each score row's blind_id with its case_id, trial, and condition."""
    lookup = {row["blind_id"]: row for row in key_rows if "blind_id" in row}
    if len(lookup) != len(key_rows):
        raise ValueError("Key file contains duplicate or malformed blind_id values")

    resolved: list[dict[str, Any]] = []
    for index, row in enumerate(scores, start=1):
        handle = row.get("blind_id")
        if not isinstance(handle, str):
            raise ValueError(f"Score row {index}: missing blind_id; --key expects blinded scores")
        source = lookup.get(handle)
        if source is None:
            raise ValueError(f"Score row {index}: blind_id {handle!r} is not in the key file")
        merged = {name: value for name, value in row.items() if name != "blind_id"}
        merged["case_id"] = source["case_id"]
        merged["trial"] = source["trial"]
        merged["condition"] = source["condition"]
        resolved.append(merged)
    return resolved


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as destination:
        for row in rows:
            destination.write(json.dumps(row, ensure_ascii=False) + "\n")


def blind_scores(args: argparse.Namespace) -> int:
    for path in (args.output, args.key):
        if path.exists() and not args.force:
            print(
                f"ERROR: {path} exists. Overwriting the key destroys the only link "
                "between a score and its condition. Pass --force to overwrite anyway.",
                file=sys.stderr,
            )
            return 1
    if args.output.resolve() == args.key.resolve():
        raise ValueError("--output and --key must be different files")

    blind, key = blind_responses(read_jsonl(args.responses), seed=args.seed)
    write_jsonl(args.output, blind)
    write_jsonl(args.key, key)
    print(f"wrote {len(blind)} blinded responses to {args.output}")
    print(f"wrote the key to {args.key}")
    print("Judge from the blinded file. Do not open the key until you finish scoring.")
    return 0


def validate_cases(cases: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    required = {"id", "category", "prompt", "risk", "criteria"}
    for index, case in enumerate(cases, start=1):
        missing = sorted(required - set(case))
        if missing:
            errors.append(f"Case {index}: missing fields: {', '.join(missing)}")
            continue
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"Case {index}: id must be a non-empty string")
        elif case_id in seen:
            errors.append(f"Duplicate case id: {case_id}")
        else:
            seen.add(case_id)
        if case["risk"] not in {"low", "medium", "high"}:
            errors.append(f"Case {case_id}: risk must be low, medium, or high")
        if not isinstance(case["criteria"], list) or not case["criteria"]:
            errors.append(f"Case {case_id}: criteria must be a non-empty list")
    return errors


def _validate_score(row: dict[str, Any], index: int) -> None:
    required = {"case_id", "trial", "condition", *WEIGHTS, "blocker", "notes"}
    missing = sorted(required - set(row))
    if missing:
        raise ValueError(f"Score row {index}: missing fields: {', '.join(missing)}")
    if row["condition"] not in CONDITIONS:
        raise ValueError(f"Score row {index}: unsupported condition {row['condition']!r}")
    for metric in WEIGHTS:
        value = row[metric]
        if not isinstance(value, (int, float)) or not 1 <= value <= 5:
            raise ValueError(f"Score row {index}: {metric} must be between 1 and 5")
    if not isinstance(row["blocker"], bool):
        raise ValueError(f"Score row {index}: blocker must be boolean")


def _describe_rows(keys: list[tuple[str, Any]]) -> str:
    return ", ".join(f"{case_id}/trial {trial}" for case_id, trial in keys)


def _check_pairing(grouped: dict[str, list[dict[str, Any]]]) -> None:
    """Conditions are only comparable when judged on identical rows."""
    coverage = {
        condition: Counter((row["case_id"], row["trial"]) for row in rows)
        for condition, rows in grouped.items()
    }
    for condition, counts in sorted(coverage.items()):
        repeated = sorted(key for key, count in counts.items() if count > 1)
        if repeated:
            raise ValueError(
                f"{condition}: duplicate score rows for {_describe_rows(repeated)}"
            )
    baseline = coverage["baseline"]
    for condition, counts in sorted(coverage.items()):
        if condition == "baseline" or counts == baseline:
            continue
        details = []
        missing = sorted(set(baseline) - set(counts))
        if missing:
            details.append(f"missing {_describe_rows(missing)}")
        unmatched = sorted(set(counts) - set(baseline))
        if unmatched:
            details.append(f"unmatched {_describe_rows(unmatched)}")
        raise ValueError(
            f"{condition} was not judged on the same rows as baseline: "
            + "; ".join(details)
        )


def summarize_scores(scores: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, row in enumerate(scores, start=1):
        _validate_score(row, index)
        grouped[row["condition"]].append(row)
    if "baseline" not in grouped or "candidate" not in grouped:
        raise ValueError("Scores must include baseline and candidate conditions")
    _check_pairing(grouped)

    conditions: dict[str, dict[str, Any]] = {}
    for condition, rows in sorted(grouped.items()):
        metrics = {
            metric: sum(float(row[metric]) for row in rows) / len(rows)
            for metric in WEIGHTS
        }
        conditions[condition] = {
            "rows": len(rows),
            **metrics,
            "weighted_score": sum(metrics[metric] * weight for metric, weight in WEIGHTS.items()),
            "blocking_findings": sum(bool(row["blocker"]) for row in rows),
        }

    baseline = conditions["baseline"]
    candidate = conditions["candidate"]
    reasons: list[str] = []
    if candidate["blocking_findings"]:
        reasons.append("Candidate has blocking safety or correctness findings.")
    if candidate["correctness"] < baseline["correctness"] - 0.1:
        reasons.append("Candidate correctness regressed by more than 0.1 points.")
    if candidate["safety"] < baseline["safety"] - 0.1:
        reasons.append("Candidate safety regressed by more than 0.1 points.")
    if candidate["language"] <= baseline["language"]:
        reasons.append("Candidate language score did not beat baseline.")
    if candidate["weighted_score"] <= baseline["weighted_score"]:
        reasons.append("Candidate weighted score did not beat baseline.")

    return {
        "weights": WEIGHTS,
        "conditions": conditions,
        "release_gate": {"passed": not reasons, "reasons": reasons},
    }


def _condition_prompt(task: str, condition: str, skill_path: Path | None) -> str:
    if condition == "baseline":
        return task
    if skill_path is None:
        raise ValueError(f"--condition-style is required for the {condition} condition")
    instructions = skill_path.read_text(encoding="utf-8")
    return (
        "Follow the response style below while completing the task. "
        "Do not discuss or quote the style.\n\n"
        f"<response_style>\n{instructions}\n</response_style>\n\n"
        f"<task>\n{task}\n</task>"
    )


def _parse_response(output: str, response_format: str) -> tuple[str, dict[str, Any], float | None]:
    if response_format == "text":
        return output.strip(), {}, None
    if response_format == "claude-json":
        payload = json.loads(output)
        return (
            str(payload.get("result", "")).strip(),
            payload.get("usage", {}) or {},
            payload.get("total_cost_usd"),
        )
    if response_format == "codex-jsonl":
        events = [json.loads(line) for line in output.splitlines() if line.strip()]
        text = ""
        usage: dict[str, Any] = {}
        for event in events:
            item = event.get("item", {})
            if event.get("type") == "item.completed" and item.get("type") == "agent_message":
                text = item.get("text", text)
            if event.get("type") == "turn.completed":
                usage = event.get("usage", usage)
        return str(text).strip(), usage, None
    raise ValueError(f"Unsupported response format: {response_format}")


def run_evaluations(args: argparse.Namespace) -> int:
    cases = load_cases(args.cases)
    errors = validate_cases(cases)
    if errors:
        raise ValueError("\n".join(errors))
    unknown = sorted(set(args.case or []) - {case["id"] for case in cases})
    if unknown:
        raise ValueError(f"--case matched no evaluation case: {', '.join(unknown)}")
    config = json.loads(args.runner_config.read_text(encoding="utf-8"))
    runner = config[args.runner]
    command = list(runner["command"])
    response_format = runner.get("response_format", "text")
    if response_format != "claude-json" and not args.allow_unmetered:
        raise RuntimeError(
            f"The {response_format!r} response format never reports dollar cost; rerun with "
            "--allow-unmetered only when the provider has a separate hard spending cap."
        )
    reported_cost = 0.0
    prior_rows = read_jsonl(args.output) if args.output.exists() else []
    done = completed_keys(prior_rows)
    reported_cost = sum(
        float(row.get("cost_usd") or 0)
        for row in prior_rows
        if row.get("condition") == args.condition and row.get("runner") == args.runner
    )

    if args.budget_usd <= 0 or args.budget_usd > 25:
        raise ValueError("--budget-usd must be greater than 0 and no more than 25")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Never call the runner from this repository. A coding agent reads its
    # working directory, so a run started here answers questions about
    # run_evals.py and cases.jsonl instead of about the task. That contaminates
    # the responses and makes the eval depend on the repo's current state.
    with tempfile.TemporaryDirectory(prefix="eval-workdir-") as workdir, args.output.open(
        "a", encoding="utf-8"
    ) as destination:
        for trial in range(1, args.trials + 1):
            for case in cases:
                if args.case and case["id"] not in args.case:
                    continue
                key = (case["id"], trial, args.condition, args.runner)
                if key in done:
                    print(f"skip completed {args.condition} trial {trial}: {case['id']}")
                    continue
                remaining = args.budget_usd - reported_cost
                if remaining <= 0:
                    print("Budget exhausted; stopping.", file=sys.stderr)
                    return 2
                prompt = _condition_prompt(case["prompt"], args.condition, args.condition_skill)
                invocation = [*command]
                if runner.get("budget_flag"):
                    invocation.extend([runner["budget_flag"], f"{remaining:.4f}"])
                invocation.append(prompt)
                completed = None
                for attempt in range(args.retries + 1):
                    completed = subprocess.run(
                        invocation,
                        check=False,
                        capture_output=True,
                        text=True,
                        cwd=workdir,
                    )
                    if completed.returncode == 0:
                        break
                    if attempt < args.retries:
                        time.sleep(min(2**attempt, 5))
                assert completed is not None
                if completed.returncode:
                    detail = completed.stderr.strip() or completed.stdout.strip()
                    if completed.stdout.strip():
                        try:
                            parsed_text, _, _ = _parse_response(completed.stdout, response_format)
                            detail = parsed_text or detail
                        except (ValueError, json.JSONDecodeError):
                            pass
                    raise RuntimeError(
                        f"Runner failed after {args.retries + 1} attempts "
                        f"({shlex.join(invocation[:-1])}):\n{detail}"
                    )
                text, usage, cost = _parse_response(completed.stdout, response_format)
                if cost is None and not args.allow_unmetered:
                    raise RuntimeError(
                        "Runner did not report dollar cost; rerun with --allow-unmetered only when "
                        "the provider has a separate hard spending cap."
                    )
                reported_cost += float(cost or 0)
                row = {
                    "case_id": case["id"],
                    "trial": trial,
                    "condition": args.condition,
                    "runner": args.runner,
                    "response": text,
                    "usage": usage,
                    "cost_usd": cost,
                }
                destination.write(json.dumps(row, ensure_ascii=False) + "\n")
                destination.flush()
                print(f"{args.condition} trial {trial}: {case['id']}")
    print(f"Reported cost: ${reported_cost:.4f}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate the case catalog")
    validate.add_argument("--cases", type=Path, default=DEFAULT_CASES)

    plan = subparsers.add_parser("plan", help="Print the paired run matrix as JSONL")
    plan.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    plan.add_argument("--trials", type=int, default=3)
    plan.add_argument("--include-comparator", action="store_true")

    blind = subparsers.add_parser(
        "blind", help="Strip the condition from responses and write a separate key"
    )
    blind.add_argument("responses", type=Path)
    blind.add_argument("--output", type=Path, required=True)
    blind.add_argument("--key", type=Path, required=True)
    blind.add_argument("--seed", type=int, default=0)
    blind.add_argument("--force", action="store_true", help="Overwrite an existing output or key")
    blind.set_defaults(handler=blind_scores)

    score = subparsers.add_parser("score", help="Aggregate manually judged score rows")
    score.add_argument("scores", type=Path)
    score.add_argument(
        "--key",
        type=Path,
        help="Key file from `blind`. Score rows must then carry blind_id, not condition.",
    )

    run = subparsers.add_parser("run", help="Run one evaluation condition")
    run.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    run.add_argument("--runner-config", type=Path, default=ROOT / "evals" / "runners.example.json")
    run.add_argument("--runner", required=True)
    run.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    run.add_argument("--condition-style", "--condition-skill", dest="condition_skill", type=Path)
    run.add_argument("--case", action="append")
    run.add_argument("--trials", type=int, default=3)
    run.add_argument("--retries", type=int, default=2)
    run.add_argument("--budget-usd", type=float, default=25.0)
    run.add_argument("--allow-unmetered", action="store_true")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_evaluations)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "handler"):
        return args.handler(args)
    if args.command == "validate":
        errors = validate_cases(load_cases(args.cases))
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("Evaluation cases are valid.")
        return 0
    if args.command == "plan":
        cases = load_cases(args.cases)
        errors = validate_cases(cases)
        if errors:
            raise ValueError("\n".join(errors))
        conditions = ["baseline", "candidate"]
        if args.include_comparator:
            conditions.append("comparator")
        for trial in range(1, args.trials + 1):
            for case in cases:
                for condition in conditions:
                    print(json.dumps({"case_id": case["id"], "trial": trial, "condition": condition}))
        return 0
    if args.command == "score":
        rows = read_jsonl(args.scores)
        if args.key:
            rows = resolve_blind(rows, read_jsonl(args.key))
        print(json.dumps(summarize_scores(rows), indent=2))
        return 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
