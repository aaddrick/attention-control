#!/usr/bin/env python3
"""Parse every config file this repo ships to another agent.

A manifest that does not parse breaks the install route it belongs to, and no
reviewer reads JSON for a missing comma. The Gemini command file and the Codex
interface file matter for the same reason: INSTALL.md tells readers to download
gemini.toml directly, so a broken file reaches them before anyone notices.

    python3 scripts/check_configs.py    # exit 1 and name every file that fails
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]

JSON_FILES = (
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "gemini-extension.json",
    "evals/runners.example.json",
)

TOML_FILES = ("skills/attention-control/agents/gemini.toml",)

YAML_FILES = ("skills/attention-control/agents/openai.yaml",)


def load_yaml() -> Callable[[Any], Any]:
    try:
        import yaml
    except ImportError:
        print(
            "ERROR: this check needs PyYAML. Run: pip install pyyaml",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return yaml.safe_load


def check(relative: str, load: Callable[[Any], Any], mode: str = "r") -> str | None:
    path = ROOT / relative
    if not path.exists():
        return "file not found"
    encoding = None if "b" in mode else "utf-8"
    try:
        with path.open(mode, encoding=encoding) as handle:
            load(handle)
    except Exception as error:  # every parser raises its own type
        return str(error).replace("\n", " ")
    return None


def main() -> int:
    safe_load = load_yaml()
    checks: list[tuple[str, Callable[[Any], Any], str]] = []
    checks += [(name, json.load, "r") for name in JSON_FILES]
    checks += [(name, tomllib.load, "rb") for name in TOML_FILES]
    checks += [(name, safe_load, "r") for name in YAML_FILES]

    failures = 0
    for relative, load, mode in checks:
        problem = check(relative, load, mode)
        if problem is None:
            continue
        failures += 1
        print(f"::error file={relative}::{problem}")
        print(f"ERROR: {relative}: {problem}", file=sys.stderr)

    if failures:
        return 1

    print(f"All {len(checks)} shipped config files parse.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
