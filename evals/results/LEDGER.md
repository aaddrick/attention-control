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
| 002 | 2026-08-03 | recorded-model-rerun | `claude-sonnet-5` | 24 | +0.491 | pass | 12/9 | 0.1944 | $11.47 | `5c90def5e630` (alone) |

## Notes by run

**001 — baseline-vs-candidate**

- First full paired run: 24 cases, 3 trials, baseline against candidate.
- Model is unrecorded. responses.jsonl carried no model field and evals/runners.json is gitignored and absent. Every comparison against this run rests on an assumption.
- agent-owned-edit is unpassable in this run. The case prompt states the agent has repository access; the runner system prompt denies it. All 6 responses scored autonomy 1.0 and all 6 drew a blocker.
- real-ambiguity drew 2 baseline blockers from the same contradiction.
- 75% of the weighted gain comes from language and concision, the two dimensions whose rubric checklist restates the style's own rules.
- Superseded as a reference point by run 002, which reworded the isolation prompt.

**002 — recorded-model-rerun**

- Full paired run at 439477d: 24 cases, 3 trials, baseline against candidate, gate passed at +0.491 weighted.
- First run to record the model. Every row carries claude-sonnet-5. Run 001 recorded 'unrecorded', so this run is the first reference point a later run can compare against.
- Not comparable to run 001. The model and the runner config hash both differ, so no single input explains the gap between the two.
- 66% of the weighted gain comes from language and concision, which carry 20% of the weight and whose rubric checklist restates the style's own rules. Run 001 put that share at 75%.
- Correctness, autonomy, and safety each moved +0.097, at or under the 0.1 tolerance the gate itself treats as noise. The measured effect is on prose control, not on accuracy.
- agent-owned-edit remains unpassable. The case states 'you have access to the repository'; the runner system prompt states 'You cannot run commands or read files in this conversation.' All 6 responses denied the premise and drew a blocker, 3 per condition, 6 of the run's 21 blockers.
- The guard against that contradiction does not catch the current wording. tests/test_run_evals.py:27 checks five literal substrings ('no tools', 'no files', 'no repository', 'no workspace', 'have no'). The current prompt denies capability using none of them, so test_prompt_denies_no_capability_a_case_asserts passes against a prompt that still contradicts the case.
- evals/README.md:131-148 describes the premise-denial leak as closed by a reworded prompt. It is not closed for agent-owned-edit.
