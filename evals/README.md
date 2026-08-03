# Evaluations

The pipeline runs in six commands, in this order: `validate`, `run`, `blind`,
`judge.py`, `score`, and `ledger.py freeze`.

The harness compares response quality against an unstyled baseline. It does not
measure length. Cases live in `cases.jsonl`. The scoring contract lives in
`rubric.md`. Every finished run lives in `results/runs/`, indexed by
`results/LEDGER.md`.

## Validate and plan

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3 --include-comparator
```

## Two splits

Every case declares `"split": "dev"` or `"split": "holdout"`. `run` and `plan`
default to `dev`.

Iterate against the 16 dev cases. Save the 8 holdout cases for the run you make
when you believe the work is finished. A style tuned against a fixed case set
until the gate passes has learned those cases. Only a set you never iterated
against separates a better style from a closer fit.

`validate` refuses a catalog whose holdout holds fewer than 4 cases, or whose
holdout is not smaller than its dev set.

## Run

Run each condition into the same results file. The harness injects the candidate
and comparator instructions from the style file you pass. Task prompts stay
identical across conditions.

```bash
python3 scripts/run_evals.py run \
  --runner claude \
  --condition baseline \
  --split dev \
  --trials 3 \
  --budget-usd 12.50 \
  --output evals/results/responses.jsonl

python3 scripts/run_evals.py run \
  --runner claude \
  --condition candidate \
  --condition-style output-styles/attention-control.md \
  --split dev \
  --trials 3 \
  --budget-usd 12.50 \
  --output evals/results/responses.jsonl
```

Use `--condition comparator` with a different style file to compare against
another project. The gate treats it as informational, not as a release blocker.

The default Claude runner reports dollar cost and receives the remaining
condition budget on every call. The harness rejects a runner without cost
reporting unless you pass `--allow-unmetered`. Use that flag only when the
provider account has its own hard cap.

Runs resume. Run the same command again after a provider failure. The harness
skips the completed `(case, trial, condition, runner)` rows. It retries each
incomplete call twice by default. It keeps the final provider error.

Every response row records the model, plus a hash of the runner command, the
case catalog, and the style file. `run` refuses to resume into a results file
whose earlier rows carry different values, because no later step could separate
them again. Pass `--allow-provenance-drift` to override.

`run` also refuses a runner command that pins no `--model`. Pass
`--allow-unpinned-model` to override.

## Isolation: four leaks, all closed

An early run of this harness measured itself instead of the style. The harness
now closes each leak below, and a test covers each fix. Keep all four when you
add a runner.

### No user config

Both example runners cut the call off from the operator's own agent
configuration: `--setting-sources ""` for Claude, `--ignore-user-config
--ephemeral` for Codex. Without it, user-level plugins, hooks, memory, and
output styles reach every condition and shape the responses under judgement.

The sharpest case is this repo's own style. Suppose an operator sets
`"outputStyle": "Attention Control"` in `~/.claude/settings.json`. The full
ruleset then reaches the **baseline** condition. The comparison measures the
style against itself.

Isolation also drops the operator's saved model and effort settings, so the
claude runner pins `--model` explicitly. Keep a pin when you edit the runner.
Without one, the eval runs whatever the operator or the CLI release defaults to.
The model then varies between operators and over time. Per-token cost varies
with it. Record the pinned model with any published numbers.

### No repository

`run_evals.py` starts every call in a fresh empty temp directory. A coding agent
reads its working directory. A run that starts from this repo answers questions
about `run_evals.py` and `cases.jsonl` instead of about the task.

An early run gives the number: **24 of 120 responses** named files in this
repository. The damage split 17 baseline against 7 candidate, so the two
conditions did not face the same task. That run predates the ledger and the
24-case catalog: 120 responses is 20 cases, 3 trials, 2 conditions.

### No workspace

The claude runner passes `--system-prompt` to replace Claude Code's
coding-agent system prompt:

```
You are a helpful assistant. Answer the message directly and completely. Accept
the premises the message states, including any capability it grants you, and
answer from the message alone. Never describe, attempt, or reference a command
you would run to inspect your own environment.
```

Copy that text from `evals/runners.example.json`, not from this file. A prompt
that drifts from the shipped config costs a run.

Without it, the agent tries to look around a workspace that does not exist. The
same early run gives the number: **16 of 120 responses**, split 10 baseline
against 6 candidate. One `complex-plan` baseline response was 238 characters
and contained no plan. It held only an attempt to list a temp directory. The
same case under the replaced prompt returned 7,196 characters and a phased plan.

This choice sets the scope of any result the harness produces. It measures the
style's effect on **prose**, not on agentic behaviour.

### No premise denial

The prompt above forbids inspecting the environment. It does not deny facts a
case states. Two wordings broke that distinction, and each cost a full run.

Run 001 read "You have no tools, no files, no repository, and no workspace."
Run 002 read "You cannot run commands or read files in this conversation." The
`agent-owned-edit` case opens with "you have access to the repository." Under
both wordings every response denied the premise. All 6 scored **1.0 on
autonomy** under both conditions, and all 6 drew a blocking finding. In run 001
the case produced a weighted delta of exactly 0.000 while consuming 6 of that
run's 16 blockers. `real-ambiguity` drew 2 more baseline blockers from the same
cause. In run 002 the case took 6 of 21 blockers.

The prompt that protected the run from the environment contaminated the run
instead. `tests/test_run_evals.py` now matches a negation joined to a capability
noun, so a reworded denial fails the guard too. The first guard listed five
literal substrings, and the second bad wording used none of them.

Read this as a general rule for any isolation you add. Isolation that
contradicts the task measures the isolation.

## Blind

Never judge from `responses.jsonl`. Every row names its condition, and a judge
who knows which style produced a response cannot un-know it.

```bash
python3 scripts/run_evals.py blind evals/results/responses.jsonl \
  --output evals/results/blind.jsonl \
  --key evals/results/blind-key.jsonl \
  --seed 0
```

The command groups rows by `(case_id, trial)`, orders each group, and labels the
rows `A`, `B`, `C`. A judge reads every condition for one case side by side. The
judge learns nothing about which is which:

```json
{"blind_id":"verbatim-error-t1-A","case_id":"verbatim-error","trial":1,"label":"A","response":"..."}
```

The blinded file drops `condition`, `runner`, `usage`, and `cost_usd`. Only the
key file links a `blind_id` back to its condition.

The order is a rotation by group index, not a shuffle. Over 24 cases and 3
trials, the run holds 72 groups, and each condition holds each position exactly
36 times out of 72. `--seed` shifts the rotation and keeps that balance.

The command refuses to overwrite an existing output or key. Pass `--force` to
allow it. An overwrite of the key destroys the only link between a score and its
condition.

Do not open the key until you finish scoring.

## Judge

```bash
python3 scripts/judge.py \
  --blind evals/results/blind.jsonl \
  --output evals/results/scores.jsonl \
  --judgements evals/results/judgements.jsonl \
  --passes 2 \
  --budget-usd 12.00
```

The judge runs a separate agent instance per group. It sees the rubric, the task
prompt, the case criteria, and the labeled responses. It sees no condition, no
repository, and no user config, under the same three isolations as the runner.

It writes two files:

- `judgements.jsonl` — one row per response per pass, with the pass index and the
  position the response held in that pass
- `scores.jsonl` — the passes averaged into one row per response, which is what
  `score` reads

It prints a stability line before the cost:

```json
{"groups_total": 72, "groups_flipped": 12, "groups_tied": 9, "groups_skipped": 0,
 "flip_rate_all": 0.1667, "flip_rate_excl_ties": 0.1905}
```

That is how often the two passes disagreed about which response was better, on
this eval, with this judge. Nobody publishes that number. Record yours next to
any result you report.

Two rates, because a tie is a judgement call. A tie means both passes agreed
that neither response won. Counting a tie as agreement gives `flip_rate_all`.
Dropping ties from the denominator gives `flip_rate_excl_ties`. On the run
above the two differ by 2.4 points. One field alone would hide which choice
produced the number, so the field names carry the denominator.

`groups_skipped` counts groups the judge scored fewer than twice. A run with a
non-zero value there measured stability on less than the full set.

To judge by hand instead, skip the script. Write rows keyed by `blind_id`:

```json
{"blind_id":"verbatim-error-t1-A","correctness":5,"autonomy":5,"actionability":5,"safety":5,"language":5,"concision":4,"blocker":false,"notes":"Error string reproduced exactly."}
```

## Score

Hand `score` the key. It restores each row's case, trial, and condition, then
applies the release gate:

```bash
python3 scripts/run_evals.py score evals/results/scores.jsonl \
  --key evals/results/blind-key.jsonl
```

`score` also accepts unblinded rows that carry `case_id`, `trial`, and
`condition` directly. Drop `--key` for that form.

Record the exact CLI and model versions with published results. Do not compare
conditions produced with different cases, models, trial counts, or rubrics.

## Freeze

```bash
python3 scripts/ledger.py freeze \
  --run-id 003 --slug what-this-run-changed --date 2026-08-04 \
  --judge-cost 7.19 \
  --note "One finding per note. Write it against the run that produced it."

python3 scripts/ledger.py index
```

`freeze` moves the five result files into `results/runs/<id>-<slug>/`, writes a
`manifest.json` beside them, and derives `report.md` from the data. `index`
rebuilds `results/LEDGER.md` from every manifest. Commit the directory.

The manifest records a **comparability key**: a digest of the model, the trial
count, and the hashes of `cases.jsonl`, `rubric.md`, the style file, and the
runner config. Two runs compare only when their keys match. `LEDGER.md` marks a
key that appears once as `(alone)`, because such a run has nothing to compare
against.

Hashes come from the run's recorded git commit, not from the working tree.
Editing a file afterward must not rewrite the history of a finished run.

```bash
python3 scripts/ledger.py compare 001 002
```

`compare` names every input that changed between two runs. It warns when more
than one changed, because the difference between those runs cannot then be
attributed to any single one. Change one input per run.

The freeze step exists because iteration destroys evidence. A field guide to
[staged evaluator pipelines][guide] names the three things such pipelines lack
against a century-old peer-review process: an adjudicator, a record, and a
norm. `LEDGER.md` is the record. The comparability key is the norm. You are the
adjudicator.

[guide]: https://github.com/aaddrick/staged-evaluator-pipelines/blob/main/poster/eo-field-guide-carousel.pdf

## Why the judge is built this way

An LLM judge is far less stable than its accuracy suggests:

- Verdicts reverse on **46.3%** of pairs when the two candidates swap places and
  nothing else changes.
- Intra-rater agreement over identical repeat runs sits between **0.265 and
  0.563**. The conventional threshold for good agreement is 0.8.
- Prompt elaboration alone moved rejection of correct code from **26.2% to
  73.2%** as the prompt added "explain" and then "propose a fix".

Four choices answer those numbers:

1. **Blinding.** The judge never sees which style produced a response.
2. **Balanced positions.** Rotation puts each condition in each position exactly
   36 times out of 72. A shuffle balances only in expectation.
3. **Two passes, orders reversed.** The judge scores every group twice, swaps the
   order between passes, then averages the two. It records both passes, so you
   measure the disagreement instead of a guess at it.
4. **No leak in the prompt.** The judge reads `rubric.md` with the release-gate
   section cut, because that section names the baseline and the candidate. The
   prompt also tells the judge to score each response against the rubric. It
   tells the judge never to lower one score to separate two responses.

Every number above comes from
[*Staged evaluator pipelines*](https://github.com/aaddrick/staged-evaluator-pipelines/blob/main/poster/eo-field-guide-carousel.pdf),
a field guide to evaluator behaviour, loop control, and suppression in staged
agent pipelines.

This judge **skips** four findings from that guide, and skips them on purpose.
Loop caps, suppression stages, adjudicators, and re-opening norms all assume a
gate that can send work backward. This judge scores once and stops.

## Attribution

The harness, the rubric, and 14 of the 24 cases derive from
[ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT). The `language`
dimension, its checklist, the ten `verbatim` / `language` / `decision` /
`uncertainty` cases, the `blind` command, and `judge.py` are new here.
