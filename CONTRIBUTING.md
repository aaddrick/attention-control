# Contributing

This repository takes no pull requests from outside contributors. GitHub blocks
them: pull request creation is set to **collaborators only**. A fork you push
to cannot open one here.

Two things still work, and both are better fits for this project.

## Found a problem? Open an issue

[Open an issue](https://github.com/aaddrick/attention-control/issues/new).
Include these four things:

1. The harness and its version: `claude --version`, `codex --version`.
2. The exact command you ran, copied from your terminal.
3. What happened.
4. What you expected instead.

A wrong path or a wrong command in [INSTALL.md](./INSTALL.md) is the most
useful report. Those claims are checked against each harness by hand, and a
harness changes them without warning.

## Want different rules? Fork

The license is MIT. Fork the repository and change the rules to fit how you
read.

The style is one file:
[`output-styles/attention-control.md`](./output-styles/attention-control.md).
Edit it, then regenerate every other copy:

```bash
python3 scripts/sync_style.py
```

The README's [Tune it](./README.md#tune-it) section gives the four commands
that swap your copy in.

## Why pull requests are off

Two reasons.

**Every file but one is generated.** `scripts/sync_style.py` writes the skill,
the Cursor rule, `AGENTS.md`, and the INSTALL.md snippet from the canonical
style file. A patch against a generated file cannot be merged. It fails CI, and
the fix is to edit the canonical file instead.

**The rules are a personal reading model, not a standard.** The style targets
one reader with ADHD. A rule that helps you may not belong here, and the fork
route gives you the change without a negotiation.

## Maintainers

Branch in this repository. Never push to `main`. Run the gates before you push:

```bash
python3 scripts/sync_style.py --check
```

```bash
python3 scripts/check_configs.py
```

```bash
python3 -m unittest discover -s tests -v
```

An eval change also needs `python3 scripts/run_evals.py validate` and a frozen
run. See [evals/README.md](./evals/README.md).
