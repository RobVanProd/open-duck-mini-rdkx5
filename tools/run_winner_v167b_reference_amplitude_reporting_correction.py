#!/usr/bin/env python3
"""Run V167 with only the final-action reproduction field corrected."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "tools/run_winner_v167_reference_amplitude_direction.py"
OUTPUT = (
    ROOT
    / "outputs/analysis/winner_v167b_reference_amplitude_direction_result.json"
)
MARKDOWN = (
    ROOT
    / "outputs/analysis/"
    "WINNER_V167B_REFERENCE_AMPLITUDE_DIRECTION_RESULT_20260725.md"
)


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(
            f"V167b correction marker count changed: {text.count(old)}"
        )
    return text.replace(old, new, 1)


def main() -> int:
    source = ORIGINAL.read_text(encoding="utf-8")
    source = replace_once(
        source,
        'row["policy_graph_authoritative_output"]',
        'row["action"]',
    )
    namespace = {
        "__file__": str(ORIGINAL),
        "__name__": "winner_v167b_corrected_runner",
    }
    exec(compile(source, str(ORIGINAL), "exec"), namespace)
    namespace["OUTPUT"] = OUTPUT
    namespace["MARKDOWN"] = MARKDOWN
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
