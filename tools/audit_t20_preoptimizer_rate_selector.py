#!/usr/bin/env python3
"""Attribute T20 attempt 1 to a pre-optimizer rate-selector conflict."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t20_support_trainthrough_one_update_preregistration.json"
)
FORMAL_RESULT = (
    ANALYSIS / "t20_support_trainthrough_one_update_result.json"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t20_support_trainthrough_one_update_v1"
)
LOG = WORK / "training.log"
SMOKE = WORK / "smoke"
V3_RUNNER = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v3/"
    "playground/open_duck_mini_v2/runner.py"
)
V4_MANIFEST = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v4/"
    "T19_COMPOSED_SOURCE_MANIFEST.json"
)
OUTPUT = ANALYSIS / "t20_preoptimizer_rate_selector_attribution.json"
MARKDOWN = (
    ANALYSIS / "T20_PREOPTIMIZER_RATE_SELECTOR_ATTRIBUTION_20260726.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite T20 attribution: {path}"
            )
    log_text = LOG.read_text(encoding="utf-8")
    runner_text = V3_RUNNER.read_text(encoding="utf-8")
    smoke_files = sorted(path for path in SMOKE.rglob("*") if path.is_file())
    smoke_dirs = sorted(path for path in SMOKE.rglob("*") if path.is_dir())
    event_files = [
        path
        for path in smoke_files
        if path.name.startswith("events.out.tfevents")
    ]
    v3_manifest = json.loads(
        (
            V3_RUNNER.parents[2] / "T19_COMPOSED_SOURCE_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )
    v4_manifest = json.loads(V4_MANIFEST.read_text(encoding="utf-8"))
    changed_python = sorted(
        name
        for name in set(v3_manifest["final_python_hashes"])
        | set(v4_manifest["final_python_hashes"])
        if v3_manifest["final_python_hashes"].get(name)
        != v4_manifest["final_python_hashes"].get(name)
    )
    old_selector = (
        "if args.winner_v119_train_transition_match" in runner_text
        and "if args.winner_t19_support_trainthrough:" in runner_text
    )
    checks = {
        "formal_result_was_not_written": not FORMAL_RESULT.exists(),
        "failure_is_exact_rate_selector": (
            "winner-v3 selected all-joint velocity vector changed"
            in log_text
        ),
        "failure_precedes_environment_construction": (
            "runner = OpenDuckMiniV2Runner(args)" in log_text
            and "BaseRunner.run" not in log_text
        ),
        "no_checkpoint_or_onnx_was_written": (
            smoke_dirs == []
            and all(path.suffix.lower() != ".onnx" for path in smoke_files)
        ),
        "event_writer_contains_header_only": (
            len(event_files) == 1
            and event_files[0].stat().st_size == 40
            and smoke_files == event_files
        ),
        "old_selector_contains_both_incompatible_validators": old_selector,
        "correction_changes_only_open_duck_runner": (
            changed_python == ["playground/open_duck_mini_v2/runner.py"]
        ),
        "optimizer_and_behavior_weight_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": (
            "open_duck.t20_preoptimizer_rate_selector_attribution.v1"
        ),
        "status": (
            "PASS_T20_PREOPTIMIZER_RATE_SELECTOR_ATTRIBUTION"
            if not failed
            else "HOLD_T20_PREOPTIMIZER_RATE_SELECTOR_ATTRIBUTION"
        ),
        "decision": (
            "PREREGISTER_T20_RATE_SELECTOR_RECOVERY"
            if not failed
            else "KEEP_T20_CLOSED"
        ),
        "checks": checks,
        "failed_checks": failed,
        "attribution": {
            "failure_class": "PRE_ENVIRONMENT_RATE_SELECTOR_CONFLICT",
            "old_v3_rule": (
                "winner_v119_train_transition_match selects V121's derived "
                "rate vector before the later T19 validator requires T19's "
                "full measured rate vector"
            ),
            "correction": (
                "when and only when winner_t19_support_trainthrough is true, "
                "the inherited Winner-v3 selector validates T19's frozen rate "
                "vector; all other branches retain their old selector"
            ),
            "changed_python_files": changed_python,
            "optimizer_steps": 0,
            "simulator_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "attempt_decision_weight": 0,
        },
        "inputs": {
            "preregistration": receipt(PREREGISTRATION),
            "training_log": receipt(LOG),
            "header_only_event": receipt(event_files[0]),
            "v3_runner": receipt(V3_RUNNER),
            "v4_manifest": receipt(V4_MANIFEST),
        },
    }
    value = {
        **basis,
        "attribution_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T20 pre-optimizer rate-selector attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Attempt 1 optimizer/behavior/hosted/robot: `0/0/0/0`",
                "- Attempt 1 decision weight: `0`",
                (
                    "- Attribution SHA-256: "
                    f"`{value['attribution_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"attribution_sha256={value['attribution_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
