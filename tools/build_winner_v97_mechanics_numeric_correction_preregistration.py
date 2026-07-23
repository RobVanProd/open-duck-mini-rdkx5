#!/usr/bin/env python3
"""Preregister the correction-only Winner-v97 mechanics rerun."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v97_mechanics_numeric_correction_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V97_MECHANICS_NUMERIC_CORRECTION_PREREGISTRATION_20260722.md"
V96_PREREGISTRATION = ANALYSIS / "winner_v96_response_conditioned_mechanics_preregistration.json"
V96_RESULT = ANALYSIS / "winner_v96_response_conditioned_mechanics_result.json"
V92_RESULT = ANALYSIS / "winner_v92_universal_target_response_observer_result.json"
CROSS_CPU = ANALYSIS / "winner_v2_recursive_cross_cpu_closure_preregistration.json"

V96_PREREGISTRATION_SHA256 = "1eeaf4c2e026b525d03baa963066c41576066030013aa5fd0b5ed3bfbe58b6d7"
V96_RESULT_SHA256 = "5abba51f4ce65b672c6190e76a1dc79cdba02990fc0eadca4277dc2e74377a01"
V92_RESULT_SHA256 = "3f706f1a36b66f7cd5d1a78d693162bdfa47dcf02fa18bb5556c6936494ae652"
CROSS_CPU_SHA256 = "d8a897047a036fe183fceea12755dc2f0dd9fcbdafcb1969ed5e388731a8a3ca"
NUMERIC_TOLERANCE = 1.0e-6
EXPECTED_ARTIFACTS = {
    "winner_v96_locomotion_default_off.onnx": "a86fcb8e091b8e743772773fa2d3384856d0c6df215082ba73b04737c5441555",
    "winner_v96_locomotion_enabled_zero.onnx": "9a62b32c5cbf0f11801abe6f7dca4acf8ef31c825ed363e358ed075be5f94d6a",
    "winner_v96_locomotion_stress.onnx": "3db85000db7c53227f747befc8b320d95a1190a66c23878a2124ae363b389780",
    "winner_v96_universal_calibrator.onnx": "0f3aebfd9946a6271fdb14adec3d68d556648f270984639d372c973a7d7dc576",
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


def exact_single_failure(checks: dict[str, Any], failed: str) -> bool:
    return checks.get(failed) is False and all(
        value is True for name, value in checks.items() if name != failed
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v97 contract: {path}")
    preregistration = json.loads(V96_PREREGISTRATION.read_text(encoding="utf-8"))
    result = json.loads(V96_RESULT.read_text(encoding="utf-8"))
    v92 = json.loads(V92_RESULT.read_text(encoding="utf-8"))
    cross_cpu = json.loads(CROSS_CPU.read_text(encoding="utf-8"))
    if (
        sha256(V96_PREREGISTRATION) != V96_PREREGISTRATION_SHA256
        or preregistration.get("status")
        != "PREREGISTERED_WINNER_V96_RESPONSE_CONDITIONED_MECHANICS"
    ):
        raise ValueError("Winner-v96 preregistration changed")
    if (
        sha256(V96_RESULT) != V96_RESULT_SHA256
        or result.get("status") != "HOLD_WINNER_V96_RESPONSE_CONDITIONED_MECHANICS"
        or result.get("failed_checks")
        != [
            "all_golden_replay_checks",
            "all_nonzero_stress_checks",
            "all_signed_calibration_checks",
        ]
        or not exact_single_failure(
            result["signed_calibration"]["checks"], "universal_target_chain_exact"
        )
        or not exact_single_failure(
            result["golden_replay"]["checks"],
            "source_graph_matches_both_goldens_bit_exact",
        )
        or not exact_single_failure(
            result["nonzero_adapter_stress"]["checks"],
            "absolute_and_rate_bounds_hold",
        )
        or result["signed_calibration"]["maximum_universal_target_error"]
        != 5.066394805908203e-07
    ):
        raise ValueError("Winner-v96 hold signature changed")
    if (
        sha256(V92_RESULT) != V92_RESULT_SHA256
        or v92.get("maximum_bounded_target_action_error") != 0.0
        or not result["signed_calibration"]["checks"]["all_v92_receipts_exact"]
    ):
        raise ValueError("exact V92 transitive target evidence changed")
    if (
        sha256(CROSS_CPU) != CROSS_CPU_SHA256
        or cross_cpu.get("frozen_constants", {}).get("direct_same_input_tolerance")
        != NUMERIC_TOLERANCE
    ):
        raise ValueError("frozen cross-CPU tolerance changed")
    actual_artifacts = {
        name: item["sha256"] for name, item in result["artifacts"].items()
    }
    if actual_artifacts != EXPECTED_ARTIFACTS:
        raise ValueError("Winner-v96 graph artifacts changed")
    source_paths = {
        "builder": Path("tools/build_winner_v97_mechanics_numeric_correction_preregistration.py"),
        "runner": Path("tools/run_winner_v97_mechanics_numeric_correction.py"),
        "tests": Path("tests/test_winner_v97_mechanics_numeric_correction.py"),
        "network": Path("patches/winner_v96_response_conditioned_networks.py"),
        "v96_runner": Path("tools/run_winner_v96_response_conditioned_mechanics.py"),
        "v96_preregistration": V96_PREREGISTRATION.relative_to(ROOT),
        "v96_result": V96_RESULT.relative_to(ROOT),
        "v92_result": V92_RESULT.relative_to(ROOT),
        "cross_cpu_preregistration": CROSS_CPU.relative_to(ROOT),
    }
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v97.mechanics_numeric_correction_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V97_MECHANICS_NUMERIC_CORRECTION",
        "decision": "AUTHORIZE_ONE_UNCHANGED_GRAPH_CORRECTION_RUN_ONLY",
        "source_hold": {
            "v96_preregistration_sha256": V96_PREREGISTRATION_SHA256,
            "v96_result_sha256": V96_RESULT_SHA256,
            "failed_top_level_checks": result["failed_checks"],
        },
        "corrections": {
            "universal_target": (
                "require exact V92 trace receipts plus the frozen V92 zero target error; "
                "do not compare against a locally reconstructed limiter vector"
            ),
            "golden_same_input": (
                "replace cross-host bit identity with the already frozen Winner-v2 "
                "direct same-input tolerance of 1e-6"
            ),
            "rate_boundary": (
                "use the same frozen 1e-6 numeric tolerance; retain exact independent "
                "final-action composition, actual-centered guard, and x=0 checks"
            ),
            "numeric_tolerance": NUMERIC_TOLERANCE,
        },
        "unchanged": {
            "network_source": True,
            "graph_artifact_sha256": EXPECTED_ARTIFACTS,
            "policy_and_calibrator_sources": True,
            "adapter_seed_and_weights": True,
            "population": "4 signed cells + 1200 golden ticks + 256 stress cases",
            "thresholds_other_than_three_attributed_assertions": True,
            "optimizer_updates": 0,
            "flat_transport_feature_enabled": False,
        },
        "pass_rule": [
            "all four regenerated ONNX graphs reproduce the exact V96 artifact hashes",
            "all four signed calibration cells retain exact V92 receipts, physical support, immutable contexts, and at least 0.15 signed separation",
            "V92's frozen bounded-target alignment remains exact zero",
            "all 1,200 selected-policy same-input action differences are at most 1e-6 while default-off remains bit-exact to the locally executed source graph",
            "the nonzero stress graph retains exact independent composition and its absolute/rate numeric excess is at most 1e-6",
            "all unaffected V96 checks remain true",
        ],
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "execution_now": {
            "simulator_cells": 0,
            "golden_ticks": 0,
            "stress_cases": 0,
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "formal_cpu_correction_run_authorized": True,
            "result_authorizes": "one separately preregistered response-conditioned locomotion training experiment only if every corrected and unaffected check passes",
            "training_authorized_now": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v97 mechanics numeric correction preregistration\n\n"
        "V96 is preserved as a hold. V97 changes no graph, weight, seed, source, or "
        "population. It corrects only three checker assertions: the calibrator limiter "
        "must be verified transitively through the exact V92 receipts; cross-host "
        "same-input comparison uses the already frozen `1e-6` threshold; and the same "
        "numeric threshold applies at the rate boundary. No training or robot access.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
