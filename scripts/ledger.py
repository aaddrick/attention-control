#!/usr/bin/env python3
"""Freeze a finished evaluation run and index the run history.

An eval you iterate on needs a record. Without one, the gap between two runs
mixes style edits, harness edits, and sampling noise, and nothing separates
them afterward. `freeze` writes that record. It copies the five result files
into a numbered directory, hashes the four inputs that decide whether two runs
compare, and derives a report from the data instead of from memory.

The four inputs are the case catalog, the rubric, the style file, and the
runner command. Two runs compare only when all four hashes match and the model
matches. `index` groups the runs that share those five values and marks the
runs that stand alone.

Hashes come from the recorded git commit, not from the working tree. A run
records the tree that produced it. Editing a file afterward must not rewrite
the history of a run that already finished.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_evals import WEIGHTS, read_jsonl, resolve_blind, summarize_scores  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "evals" / "results"
DEFAULT_RUNS = DEFAULT_RESULTS / "runs"
DEFAULT_LEDGER = DEFAULT_RESULTS / "LEDGER.md"
RESULT_FILES = (
    "responses.jsonl",
    "blind.jsonl",
    "blind-key.jsonl",
    "judgements.jsonl",
    "scores.jsonl",
)
# The four inputs that decide whether two runs measure the same thing.
TRACKED_INPUTS = {
    "cases": "evals/cases.jsonl",
    "rubric": "evals/rubric.md",
    "style": "output-styles/attention-control.md",
    "runner_config": "evals/runners.example.json",
}
UNRECORDED = "unrecorded"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_output(args: list[str]) -> str | None:
    """Run a git command and return its stdout, or None when git cannot answer."""
    try:
        done = subprocess.run(
            ["git", *args], cwd=ROOT, check=False, capture_output=True, text=True
        )
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


def blob_at(sha: str | None, relative: str) -> bytes | None:
    """Read a file as it existed at a commit, falling back to the working tree."""
    if sha:
        text = git_output(["show", f"{sha}:{relative}"])
        if text is not None:
            return text.encode("utf-8")
    path = ROOT / relative
    return path.read_bytes() if path.exists() else None


def input_hashes(sha: str | None) -> dict[str, dict[str, Any]]:
    hashes: dict[str, dict[str, Any]] = {}
    for name, relative in TRACKED_INPUTS.items():
        payload = blob_at(sha, relative)
        hashes[name] = {
            "path": relative,
            "sha256": sha256_bytes(payload) if payload is not None else None,
        }
    return hashes


def comparability_key(manifest: dict[str, Any]) -> str:
    """A short digest of everything a valid comparison must hold constant."""
    parts = [str(manifest.get("model") or UNRECORDED), str(manifest.get("trials"))]
    for name in sorted(TRACKED_INPUTS):
        parts.append(str(manifest["inputs"].get(name, {}).get("sha256")))
    return sha256_bytes("\x1f".join(parts).encode("utf-8"))[:12]


def weighted(row: dict[str, Any]) -> float:
    return sum(float(row[name]) * weight for name, weight in WEIGHTS.items())


def paired_stats(deltas: list[float]) -> dict[str, float]:
    """Mean, standard error, t, and a normal-approximation 95% interval."""
    count = len(deltas)
    mean = statistics.mean(deltas)
    if count < 2:
        return {"n": count, "mean": mean, "se": 0.0, "t": 0.0, "lo": mean, "hi": mean}
    error = statistics.stdev(deltas) / (count**0.5)
    return {
        "n": count,
        "mean": mean,
        "se": error,
        "t": mean / error if error else 0.0,
        "lo": mean - 1.96 * error,
        "hi": mean + 1.96 * error,
    }


def pair_rows(resolved: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, dict[str, Any]]]:
    pairs: dict[tuple[str, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in resolved:
        pairs[(row["case_id"], row["trial"])][row["condition"]] = row
    return pairs


def flip_rates(judgements: list[dict[str, Any]], key_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Recompute both flip rates from the raw per-pass judgements.

    A tie means the two passes agreed that neither response won. Counting ties
    as agreement and dropping them from the denominator give different numbers,
    and one number alone hides the choice. Report both.
    """
    lookup = {row["blind_id"]: row["condition"] for row in key_rows}
    grouped: dict[tuple[str, int], dict[int, dict[str, dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for row in judgements:
        condition = lookup.get(row["blind_id"])
        if condition is None:
            continue
        grouped[(row["case_id"], row["trial"])][row["pass"]][condition] = row

    total = flipped = tied = skipped = 0
    for passes in grouped.values():
        usable = [
            index
            for index, byc in passes.items()
            if {"baseline", "candidate"} <= set(byc)
        ]
        if len(usable) < 2:
            skipped += 1
            continue
        first, second = sorted(usable)[:2]
        signs = []
        for index in (first, second):
            delta = weighted(passes[index]["candidate"]) - weighted(passes[index]["baseline"])
            signs.append((delta > 0) - (delta < 0))
        total += 1
        if 0 in signs:
            tied += 1
        elif signs[0] != signs[1]:
            flipped += 1

    decided = total - tied
    return {
        "groups_total": total,
        "groups_flipped": flipped,
        "groups_tied": tied,
        "groups_skipped": skipped,
        "flip_rate_all": round(flipped / total, 4) if total else None,
        "flip_rate_excl_ties": round(flipped / decided, 4) if decided else None,
    }


def build_analysis(results: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    resolved = resolve_blind(results["scores"], results["blind-key"])
    summary = summarize_scores(resolved)
    pairs = pair_rows(resolved)
    complete = [v for v in pairs.values() if {"baseline", "candidate"} <= set(v)]

    dimensions: dict[str, Any] = {}
    for name, weight in WEIGHTS.items():
        deltas = [v["candidate"][name] - v["baseline"][name] for v in complete]
        stats = paired_stats(deltas)
        stats["contribution"] = stats["mean"] * weight
        stats["significant"] = stats["lo"] * stats["hi"] > 0
        dimensions[name] = stats

    overall = paired_stats([weighted(v["candidate"]) - weighted(v["baseline"]) for v in complete])
    per_case: dict[str, list[float]] = defaultdict(list)
    for (case_id, _), value in pairs.items():
        if {"baseline", "candidate"} <= set(value):
            per_case[case_id].append(weighted(value["candidate"]) - weighted(value["baseline"]))
    case_means = {cid: statistics.mean(v) for cid, v in per_case.items()}

    blockers: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in resolved:
        if row.get("blocker"):
            blockers[row["condition"]].append(
                {
                    "case_id": row["case_id"],
                    "trial": row["trial"],
                    "notes": str(row.get("notes", "")),
                }
            )

    return {
        "gate": summary["release_gate"],
        "conditions": summary["conditions"],
        "dimensions": dimensions,
        "overall": overall,
        "per_case_mean_delta": dict(sorted(case_means.items(), key=lambda item: item[1])),
        "blockers": {c: sorted(v, key=lambda b: (b["case_id"], b["trial"])) for c, v in blockers.items()},
        "stability": flip_rates(results["judgements"], results["blind-key"]),
    }


def render_report(manifest: dict[str, Any], analysis: dict[str, Any]) -> str:
    gate = analysis["gate"]
    base = analysis["conditions"]["baseline"]
    cand = analysis["conditions"]["candidate"]
    lines = [
        f"# Run {manifest['run_id']}: {manifest['slug']}",
        "",
        f"- Date: {manifest['created']}",
        f"- Model: `{manifest['model']}`",
        f"- Runner: `{manifest['runner']}`",
        f"- Git commit: `{manifest['git_sha'] or UNRECORDED}`",
        f"- Comparability key: `{manifest['comparability_key']}`",
        f"- Trials: {manifest['trials']} | Blind seed: {manifest['blind_seed']} "
        f"| Judge passes: {manifest['judge_passes']}",
        f"- Cost: ${manifest['cost_usd']['total']:.2f} "
        f"(run ${manifest['cost_usd']['run']:.2f}, judge ${manifest['cost_usd']['judge']:.2f})",
        "",
        "## Release gate",
        "",
        f"**{'PASSED' if gate['passed'] else 'FAILED'}**",
        "",
    ]
    if gate["reasons"]:
        lines += [f"- {reason}" for reason in gate["reasons"]] + [""]

    lines += [
        "## Dimensions",
        "",
        "| Dimension | Baseline | Candidate | Delta | t | 95% CI | Significant | Share of total |",
        "|---|---:|---:|---:|---:|---|---|---:|",
    ]
    total_delta = analysis["overall"]["mean"]
    for name in WEIGHTS:
        stats = analysis["dimensions"][name]
        share = stats["contribution"] / total_delta * 100 if total_delta else 0.0
        lines.append(
            f"| {name} | {base[name]:.3f} | {cand[name]:.3f} | {stats['mean']:+.3f} "
            f"| {stats['t']:.2f} | [{stats['lo']:+.3f}, {stats['hi']:+.3f}] "
            f"| {'yes' if stats['significant'] else 'no'} | {share:.1f}% |"
        )
    overall = analysis["overall"]
    lines += [
        f"| **weighted** | **{base['weighted_score']:.3f}** | **{cand['weighted_score']:.3f}** "
        f"| **{overall['mean']:+.3f}** | **{overall['t']:.2f}** "
        f"| [{overall['lo']:+.3f}, {overall['hi']:+.3f}] "
        f"| {'yes' if overall['lo'] * overall['hi'] > 0 else 'no'} | 100% |",
        "",
        "## Judge stability",
        "",
        "```json",
        json.dumps(analysis["stability"]),
        "```",
        "",
        "A flip means the two passes disagreed about which response won. Published",
        "measurements put positional reversal at 46.3% and intra-rater agreement",
        "between 0.265 and 0.563 against a 0.8 threshold for good agreement. Nothing",
        "here labels a flip as beneficial or harmful, so a flip stays noise.",
        "",
        "## Blocking findings",
        "",
    ]
    for condition in ("baseline", "candidate"):
        found = analysis["blockers"].get(condition, [])
        lines.append(f"**{condition}: {len(found)}**")
        lines.append("")
        for item in found:
            lines.append(f"- `{item['case_id']}` t{item['trial']} — {item['notes']}")
        lines.append("")

    lines += ["## Weighted delta by case", "", "| Case | Mean delta |", "|---|---:|"]
    for case_id, value in analysis["per_case_mean_delta"].items():
        lines.append(f"| `{case_id}` | {value:+.3f} |")
    lines.append("")

    if manifest.get("notes"):
        lines += ["## Notes", ""] + [f"- {note}" for note in manifest["notes"]] + [""]
    return "\n".join(lines)


def load_results(source: Path) -> dict[str, list[dict[str, Any]]]:
    results: dict[str, list[dict[str, Any]]] = {}
    missing = [name for name in RESULT_FILES if not (source / name).exists()]
    if missing:
        raise FileNotFoundError(f"{source} is missing: {', '.join(missing)}")
    for name in RESULT_FILES:
        results[name.removesuffix(".jsonl")] = read_jsonl(source / name)
    return results


def freeze(args: argparse.Namespace) -> int:
    results = load_results(args.results_dir)
    target = args.runs_dir / f"{args.run_id}-{args.slug}"
    if target.exists() and not args.force:
        print(f"ERROR: {target} exists. Pass --force to overwrite.", file=sys.stderr)
        return 1

    sha = args.git_sha
    if sha is None:
        head = git_output(["rev-parse", "--short", "HEAD"])
        sha = head.strip() if head else None
    dirty = bool((git_output(["status", "--porcelain"]) or "").strip())

    run_cost = sum(float(row.get("cost_usd") or 0) for row in results["responses"])
    conditions = sorted({str(row.get("condition")) for row in results["responses"]})

    # Prefer the model the rows carry over the one the operator typed. A typed
    # value records a belief; a recorded value records what ran.
    recorded = {row["model"] for row in results["responses"] if row.get("model")}
    model = args.model
    if len(recorded) == 1:
        found = recorded.pop()
        if model and model != UNRECORDED and model != found:
            raise ValueError(
                f"--model says {model!r} but every response row says {found!r}. "
                "Fix the flag or the data; do not record a value the run contradicts."
            )
        model = found
    elif len(recorded) > 1:
        raise ValueError(
            f"Responses name more than one model: {', '.join(sorted(recorded))}. "
            "A run that mixed models cannot be frozen as one comparison."
        )
    elif not model:
        raise ValueError(
            "No response row carries a model and --model was not given. "
            f"Pass --model {UNRECORDED} only when the value is genuinely lost."
        )

    manifest: dict[str, Any] = {
        "run_id": args.run_id,
        "slug": args.slug,
        "created": args.date,
        "git_sha": sha,
        "git_dirty_at_freeze": dirty,
        "model": model,
        "runner": args.runner,
        "conditions": conditions,
        "trials": args.trials,
        "blind_seed": args.blind_seed,
        "judge_passes": args.judge_passes,
        "cases_count": len({str(row.get("case_id")) for row in results["responses"]}),
        "split": args.split,
        "responses": len(results["responses"]),
        "inputs": input_hashes(sha),
        "cost_usd": {
            "run": round(run_cost, 4),
            "judge": round(args.judge_cost, 4),
            "total": round(run_cost + args.judge_cost, 4),
        },
        "notes": list(args.note or []),
    }
    manifest["comparability_key"] = comparability_key(manifest)

    analysis = build_analysis(results)
    manifest["gate_passed"] = analysis["gate"]["passed"]
    manifest["weighted_delta"] = round(analysis["overall"]["mean"], 4)
    manifest["stability"] = analysis["stability"]
    manifest["blocking_findings"] = {
        condition: len(analysis["blockers"].get(condition, []))
        for condition in ("baseline", "candidate")
    }

    target.mkdir(parents=True, exist_ok=True)
    for name in RESULT_FILES:
        source = args.results_dir / name
        (target / name).write_bytes(source.read_bytes())
        if not args.keep:
            source.unlink()
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (target / "report.md").write_text(render_report(manifest, analysis), encoding="utf-8")

    print(f"froze run {args.run_id} into {target}")
    print(f"comparability key: {manifest['comparability_key']}")
    if model == UNRECORDED:
        print(
            "WARNING: the model is unrecorded. Every comparison against this run "
            "rests on an assumption instead of a record.",
            file=sys.stderr,
        )
    return 0


def read_manifests(runs_dir: Path) -> list[dict[str, Any]]:
    manifests = []
    for path in sorted(runs_dir.glob("*/manifest.json")):
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    return manifests


def index(args: argparse.Namespace) -> int:
    manifests = read_manifests(args.runs_dir)
    if not manifests:
        print(f"No runs found under {args.runs_dir}", file=sys.stderr)
        return 1

    groups: dict[str, list[str]] = defaultdict(list)
    for manifest in manifests:
        groups[manifest["comparability_key"]].append(manifest["run_id"])

    lines = [
        "# Evaluation run ledger",
        "",
        "One row per frozen run. `scripts/ledger.py index` rebuilds this file from",
        "the manifests. Do not edit it by hand.",
        "",
        "Two runs compare only when their comparability keys match. The key covers",
        "the model, the trial count, and the hashes of the case catalog, the rubric,",
        "the style file, and the runner config. A key that appears once has nothing",
        "to compare against.",
        "",
        "| Run | Date | Slug | Model | Cases | Weighted delta | Gate | Blockers b/c | Flip (all) | Cost | Key |",
        "|---|---|---|---|---:|---:|---|---|---:|---:|---|",
    ]
    for manifest in manifests:
        stability = manifest.get("stability", {})
        blockers = manifest.get("blocking_findings", {})
        shared = len(groups[manifest["comparability_key"]]) > 1
        key_cell = f"`{manifest['comparability_key']}`" + ("" if shared else " (alone)")
        flip = stability.get("flip_rate_all")
        lines.append(
            f"| {manifest['run_id']} | {manifest['created']} | {manifest['slug']} "
            f"| `{manifest['model']}` | {manifest['cases_count']} "
            f"| {manifest.get('weighted_delta', 0):+.3f} "
            f"| {'pass' if manifest.get('gate_passed') else 'FAIL'} "
            f"| {blockers.get('baseline', 0)}/{blockers.get('candidate', 0)} "
            f"| {flip if flip is not None else 'n/a'} "
            f"| ${manifest['cost_usd']['total']:.2f} | {key_cell} |"
        )

    lines += ["", "## Notes by run", ""]
    for manifest in manifests:
        lines.append(f"**{manifest['run_id']} — {manifest['slug']}**")
        lines.append("")
        for note in manifest.get("notes") or ["(none)"]:
            lines.append(f"- {note}")
        lines.append("")

    args.ledger.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {len(manifests)} runs to {args.ledger}")
    return 0


def compare(args: argparse.Namespace) -> int:
    manifests = {m["run_id"]: m for m in read_manifests(args.runs_dir)}
    missing = [rid for rid in (args.left, args.right) if rid not in manifests]
    if missing:
        print(f"ERROR: no such run: {', '.join(missing)}", file=sys.stderr)
        return 1
    left, right = manifests[args.left], manifests[args.right]

    drifted = []
    for name in sorted(TRACKED_INPUTS):
        if left["inputs"][name]["sha256"] != right["inputs"][name]["sha256"]:
            drifted.append(name)
    if left["model"] != right["model"]:
        drifted.append("model")
    if left["trials"] != right["trials"]:
        drifted.append("trials")

    print(f"run {left['run_id']} ({left['slug']}) against run {right['run_id']} ({right['slug']})")
    print(f"  weighted delta: {left.get('weighted_delta', 0):+.3f} -> {right.get('weighted_delta', 0):+.3f}")
    print(f"  gate:           {left.get('gate_passed')} -> {right.get('gate_passed')}")
    print(f"  inputs changed: {', '.join(drifted) if drifted else 'none'}")
    if len(drifted) > 1:
        print(
            f"  WARNING: {len(drifted)} inputs changed at once. The difference between "
            "these runs cannot be attributed to any one of them.",
            file=sys.stderr,
        )
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze_parser = subparsers.add_parser("freeze", help="Freeze a finished run into the ledger")
    freeze_parser.add_argument("--run-id", required=True)
    freeze_parser.add_argument("--slug", required=True)
    freeze_parser.add_argument("--date", required=True, help="Run date as YYYY-MM-DD")
    freeze_parser.add_argument(
        "--model",
        default=None,
        help=(
            "Overrides nothing. The model comes from the response rows when they carry one. "
            f"Pass {UNRECORDED!r} only for a run whose rows predate model recording."
        ),
    )
    freeze_parser.add_argument("--runner", default="claude")
    freeze_parser.add_argument("--trials", type=int, default=3)
    freeze_parser.add_argument("--blind-seed", type=int, default=0)
    freeze_parser.add_argument("--judge-passes", type=int, default=2)
    freeze_parser.add_argument("--judge-cost", type=float, default=0.0)
    freeze_parser.add_argument("--split", default="all")
    freeze_parser.add_argument("--git-sha", default=None, help="Defaults to current HEAD")
    freeze_parser.add_argument("--note", action="append")
    freeze_parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    freeze_parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    freeze_parser.add_argument("--keep", action="store_true", help="Copy instead of move")
    freeze_parser.add_argument("--force", action="store_true")

    index_parser = subparsers.add_parser("index", help="Rebuild LEDGER.md from the manifests")
    index_parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    index_parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)

    compare_parser = subparsers.add_parser("compare", help="Diff two frozen runs")
    compare_parser.add_argument("left")
    compare_parser.add_argument("right")
    compare_parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return {"freeze": freeze, "index": index, "compare": compare}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
