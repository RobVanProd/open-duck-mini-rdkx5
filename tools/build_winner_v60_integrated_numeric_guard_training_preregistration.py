#!/usr/bin/env python3
"""Freeze the evidence-selected integrated continuation with a numeric replay guard."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v60_integrated_numeric_guard_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V60_INTEGRATED_NUMERIC_GUARD_TRAINING_PREREGISTRATION_20260722.md"
V58_PREREG = ANALYSIS / "winner_v58_integrated_first_tick_training_preregistration.json"
V58_PREREG_SHA256 = "28dc79f2fb7108f332da1d2ee93bb5b8da7a0a840751fcfa5501abc90ac6fd9a"
V59_RESULT = ANALYSIS / "winner_v59_hidden_replay_numeric_attribution_result.json"
V59_RESULT_SHA256 = "2bc025115d2c2d4eba2aca7e8d0670b2c9e6f90fc2d96507d38034cbc946c39b"

NUMERIC_REPLAY_GUARD = {
    "metric": "sampled_hidden_replay_max_abs_error",
    "source_legacy_threshold": 1.0e-6,
    "selected_threshold": 2.0e-6,
    "selection_basis": "next power-of-two bound above the V59 measured maximum",
    "v59_measured_maximum": 1.125037670135498e-6,
    "v59_result_sha256": V59_RESULT_SHA256,
    "coefficient_or_threshold_search": False,
}

CUSTOM_SOURCES = {
    "v60_builder": Path(
        "tools/build_winner_v60_integrated_numeric_guard_training_preregistration.py"
    ),
    "v60_runner": Path("tools/run_winner_v60_integrated_numeric_guard_training.py"),
    "v60_tests": Path("tests/test_winner_v60_integrated_numeric_guard_training.py"),
    "v59_result": Path(
        "outputs/analysis/winner_v59_hidden_replay_numeric_attribution_result.json"
    ),
    "v59_preregistration": Path(
        "outputs/analysis/winner_v59_hidden_replay_numeric_attribution_preregistration.json"
    ),
    "v58_transform_builder": Path(
        "tools/build_winner_v58_integrated_first_tick_training_preregistration.py"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def transformed_source() -> tuple[str, list[dict[str, Any]]]:
    import build_winner_v58_integrated_first_tick_training_preregistration as v58

    source, _ = v58.transformed_source()
    receipts: list[dict[str, Any]] = []

    def replace(old: str, new: str, count: int = 1) -> None:
        nonlocal source
        actual = source.count(old)
        if actual != count:
            raise ValueError(
                f"Winner-v60 transform count changed: expected {count}, "
                f"found {actual}: {old!r}"
            )
        source = source.replace(old, new)
        receipts.append(
            {
                "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
                "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
                "replacement_count": count,
            }
        )

    replace("winner_v58", "winner_v60", source.count("winner_v58"))
    replace("Winner-v58", "Winner-v60", source.count("Winner-v58"))
    replace("WINNER_V58", "WINNER_V60", source.count("WINNER_V58"))
    replace(
        'float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) > 1.0e-6',
        'float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) > 2.0e-6',
    )
    replace(
        '"all_100_hidden_replays_at_most_1e_6"',
        '"all_100_hidden_replays_at_most_2e_6"',
    )
    replace(
        'row["sampled_hidden_replay_max_abs_error"] <= 1.0e-6',
        'row["sampled_hidden_replay_max_abs_error"] <= 2.0e-6',
    )
    marker = '        raise ValueError("Winner-v60 first-tick objective changed")'
    guard_validation = marker + '''
    replay_guard = value.get("frozen_training", {}).get("hidden_replay_numeric_guard", {})
    if replay_guard != {
        "metric": "sampled_hidden_replay_max_abs_error",
        "source_legacy_threshold": 1.0e-6,
        "selected_threshold": 2.0e-6,
        "selection_basis": "next power-of-two bound above the V59 measured maximum",
        "v59_measured_maximum": 1.125037670135498e-6,
        "v59_result_sha256": "2bc025115d2c2d4eba2aca7e8d0670b2c9e6f90fc2d96507d38034cbc946c39b",
        "coefficient_or_threshold_search": False,
    }:
        raise ValueError("Winner-v60 numeric replay guard changed")'''
    replace(marker, guard_validation)
    compile(source, "winner_v60_integrated_numeric_guard_training.py", "exec")
    return source, receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v60 evidence: {path}")
    if sha256(V58_PREREG) != V58_PREREG_SHA256:
        raise ValueError("Winner-v60 base preregistration changed")
    if sha256(V59_RESULT) != V59_RESULT_SHA256:
        raise ValueError("Winner-v60 numeric attribution result changed")
    old = json.loads(V58_PREREG.read_text(encoding="utf-8"))
    attribution = json.loads(V59_RESULT.read_text(encoding="utf-8"))
    if (
        attribution.get("status")
        != "PASS_WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION"
        or attribution.get("decision")
        != "AUTHORIZE_REVISED_NUMERIC_GUARD_CONTINUATION_PREREGISTRATION_ONLY"
        or attribution.get("failed_checks") != []
        or attribution.get("metrics", {}).get("scan_hidden_max_abs_error")
        != NUMERIC_REPLAY_GUARD["v59_measured_maximum"]
        or attribution.get("execution", {}).get("optimizer_updates") != 0
    ):
        raise ValueError("Winner-v60 source authority changed")
    transformed, receipts = transformed_source()
    sources = dict(old["sources"])
    for name, path in CUSTOM_SOURCES.items():
        sources[name] = {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
    payload = json.loads(json.dumps(old))
    frozen = dict(payload["frozen_training"])
    frozen["hidden_replay_numeric_guard"] = NUMERIC_REPLAY_GUARD
    stop_rules = dict(payload["stop_rules"])
    stop_rules["stop_on_hidden_replay_above_2e_6"] = True
    payload.update(
        {
            "schema_version": "winner_v60.integrated_first_tick_training_preregistration.v1",
            "status": "PREREGISTERED_WINNER_V60_INTEGRATED_FIRST_TICK_TEACHER_TRAINING",
            "decision": "AUTHORIZE_ONE_100_UPDATE_INTEGRATED_FIRST_TICK_TEACHER_ARM_ONLY",
            "causal_hypothesis": (
                "V59 proves the Winner-v58 stop was bounded eager-versus-scan float32 "
                "drift with zero PPO-loss effect. Re-running the unchanged integrated "
                "objective from count 454 with the preregistered 2e-6 numeric guard can "
                "produce a complete, auditable 100-update half/final record."
            ),
            "frozen_training": frozen,
            "numeric_guard_evidence": {
                "path": V59_RESULT.relative_to(ROOT).as_posix(),
                "bytes": V59_RESULT.stat().st_size,
                "sha256": sha256(V59_RESULT),
            },
            "stop_rules": stop_rules,
            "sources": sources,
            "source_manifest_sha256": canonical_sha256(sources),
            "transformation": {
                "base_v58_transformed_source_sha256": old["transformation"][
                    "transformed_source_sha256"
                ],
                "transformed_source_sha256": hashlib.sha256(
                    transformed.encode()
                ).hexdigest(),
                "replacements": receipts,
                "replacement_groups": len(receipts),
            },
            "authority": {
                "robot_clearance": False,
                "training_authorized": True,
                "formal_support_gate_authorized": False,
                "pass_authorizes_only": (
                    "a separately preregistered unchanged half/final support gate"
                ),
                "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            },
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v60 integrated numeric-guard training preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source / half / final optimizer counts: `454 / 504 / 554`",
                "- Optimizer updates: exact `100`",
                "- Replay guard: `2e-6` (V59 measured `1.125037670135498e-6`)",
                "- Objective and coefficients: exact Winner-v58, unchanged",
                "- Observation/action ABI: unchanged stateful `115+14+64 -> 14+64`",
                "- Attention or flat-transport mechanism: none",
                "- Support cells / robot access authorized now: `0 / 0`",
                "",
                "This is a new evidence-selected arm, not a resumption or silent retry of",
                "Winner-v58. It starts from the immutable V57 count-454 snapshot so all 100",
                "metrics, atomic snapshots, and the half/final checkpoints are complete.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
