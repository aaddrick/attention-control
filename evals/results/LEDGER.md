# Evaluation run ledger

One row per frozen run. `scripts/ledger.py index` rebuilds this file from
the manifests. Do not edit it by hand.

Two runs compare only when their comparability keys match. The key covers
the model, the trial count, and the hashes of the case catalog, the rubric,
the style file, and the runner config. A key that appears once has nothing
to compare against.

| Run | Date | Slug | Model | Cases | Weighted delta | Gate | Blockers b/c | Flip (all) | Cost | Key |
|---|---|---|---|---:|---:|---|---|---:|---:|---|
| 001 | 2026-08-02 | baseline-vs-candidate | `unrecorded` | 24 | +0.449 | pass | 9/7 | 0.1667 | $10.98 | `cdb8372807a4` (alone) |

## Notes by run

**001 — baseline-vs-candidate**

- First full paired run: 24 cases, 3 trials, baseline against candidate.
- Model is unrecorded. responses.jsonl carried no model field and evals/runners.json is gitignored and absent. Every comparison against this run rests on an assumption.
- agent-owned-edit is unpassable in this run. The case prompt states the agent has repository access; the runner system prompt denies it. All 6 responses scored autonomy 1.0 and all 6 drew a blocker.
- real-ambiguity drew 2 baseline blockers from the same contradiction.
- 75% of the weighted gain comes from language and concision, the two dimensions whose rubric checklist restates the style's own rules.
- Superseded as a reference point by run 002, which reworded the isolation prompt.
