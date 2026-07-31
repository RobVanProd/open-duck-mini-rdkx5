#!/usr/bin/env python3
"""Run the correction-only Winner-v97 response mechanics contract."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import build_winner_v97_mechanics_numeric_correction_preregistration as builder  # noqa: E402
import run_winner_v96_response_conditioned_mechanics as v96  # noqa: E402
import winner_v96_response_conditioned_networks as networks  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v97_mechanics_numeric_correction_preregistration.json"
V96_PREREGISTRATION = ANALYSIS / "winner_v96_response_conditioned_mechanics_preregistration.json"
V92_RESULT = ANALYSIS / "winner_v92_universal_target_response_observer_result.json"


def validate_preregistration(value: Mapping[str, Any]) -> None:
    corrections = value.get("corrections", {})
    unchanged = value.get("unchanged", {})
    if (
        value.get("schema_version")
        != "winner_v97.mechanics_numeric_correction_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V97_MECHANICS_NUMERIC_CORRECTION"
        or value.get("source_hold", {}).get("v96_result_sha256")
        != builder.V96_RESULT_SHA256
        or corrections.get("numeric_tolerance") != builder.NUMERIC_TOLERANCE
        or unchanged.get("graph_artifact_sha256") != builder.EXPECTED_ARTIFACTS
        or unchanged.get("network_source") is not True
        or unchanged.get("adapter_seed_and_weights") is not True
        or unchanged.get("flat_transport_feature_enabled") is not False
        or value.get("execution_now")
        != {
            "simulator_cells": 0,
            "golden_ticks": 0,
            "stress_cases": 0,
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v97 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v97 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v97 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v97 source manifest changed")


def all_but(checks: Mapping[str, Any], excluded: str) -> bool:
    return all(value is True for name, value in checks.items() if name != excluded)


def check_same_input_numeric(base_session: Any) -> dict[str, Any]:
    rows = []
    global_maximum = 0.0
    for path in v96.GOLDENS:
        golden = np.load(path)
        maximum = 0.0
        for obs, previous, expected_action, expected_previous in zip(
            golden["obs"],
            golden["previous_action_in"],
            golden["final_action"],
            golden["previous_action_out"],
            strict=True,
        ):
            actual_action, actual_previous = base_session.run(
                ["continuous_actions", "previous_action_out"],
                {"obs": obs[None, :], "previous_action": previous[None, :]},
            )
            maximum = max(
                maximum,
                v96.maximum_error(actual_action[0], expected_action),
                v96.maximum_error(actual_previous[0], expected_previous),
            )
        global_maximum = max(global_maximum, maximum)
        rows.append(
            {
                "golden": path.relative_to(ROOT).as_posix(),
                "ticks": int(golden["obs"].shape[0]),
                "same_input_action_and_state_maximum_abs": maximum,
                "at_most_frozen_1e_minus_6": maximum <= builder.NUMERIC_TOLERANCE,
            }
        )
    return {
        "rows": rows,
        "maximum_abs": global_maximum,
        "all_at_most_frozen_1e_minus_6": all(
            row["at_most_frozen_1e_minus_6"] for row in rows
        ),
    }


def check_stress_boundary_numeric(
    stress_session: Any, contexts: list[np.ndarray]
) -> dict[str, Any]:
    import onnx

    model = onnx.load(v96.POLICY)
    initializers = {
        item.name: onnx.numpy_helper.to_array(item) for item in model.graph.initializer
    }
    maximum_delta = np.asarray(initializers["max_action_delta"], dtype=np.float32)
    pitch_mask = np.asarray(initializers["guard_pitch_mask"], dtype=np.bool_)[0]
    zero = np.load(v96.builder.GOLDEN_ZERO)
    moving = np.load(v96.builder.GOLDEN_MOVING)
    rng = np.random.Generator(np.random.PCG64(60797))
    maximum_absolute_excess = 0.0
    maximum_rate_excess = 0.0
    maximum_pitch_rate_excess = 0.0
    maximum_nonpitch_rate_excess = 0.0
    for index in range(256):
        use_zero = index % 4 == 0
        source = zero if use_zero else moving
        row = int(rng.integers(0, 600))
        obs = source["obs"][row : row + 1].copy()
        previous = source["previous_action_in"][row : row + 1].copy()
        if use_zero:
            obs[:, 6] = 0.0
            previous[:] = 0.0
        h_in = rng.uniform(-0.6, 0.6, (1, 64)).astype(np.float32)
        context = contexts[index % len(contexts)]
        action = stress_session.run(
            ["continuous_actions"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": h_in,
                "calibration_context": context,
            },
        )[0]
        absolute_excess = np.abs(action) - np.float32(1.0)
        rate_excess = np.abs(action - previous) - maximum_delta
        maximum_absolute_excess = max(
            maximum_absolute_excess, float(np.max(absolute_excess))
        )
        maximum_rate_excess = max(maximum_rate_excess, float(np.max(rate_excess)))
        maximum_pitch_rate_excess = max(
            maximum_pitch_rate_excess, float(np.max(rate_excess[:, pitch_mask]))
        )
        maximum_nonpitch_rate_excess = max(
            maximum_nonpitch_rate_excess,
            float(np.max(rate_excess[:, ~pitch_mask])),
        )
    return {
        "cases": 256,
        "numeric_tolerance": builder.NUMERIC_TOLERANCE,
        "maximum_absolute_excess": maximum_absolute_excess,
        "maximum_rate_excess": maximum_rate_excess,
        "maximum_pitch_rate_excess": maximum_pitch_rate_excess,
        "maximum_nonpitch_rate_excess": maximum_nonpitch_rate_excess,
        "absolute_and_rate_excess_at_most_1e_minus_6": (
            maximum_absolute_excess <= builder.NUMERIC_TOLERANCE
            and maximum_rate_excess <= builder.NUMERIC_TOLERANCE
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-correction-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.formal_correction_authorized:
        raise PermissionError("Winner-v97 requires explicit offline CPU correction authorization")
    if args.output.exists() or args.artifact_dir.exists():
        raise FileExistsError("refusing to overwrite Winner-v97 evidence or artifacts")

    import jax
    import onnx

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v97 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v96_preregistration = json.loads(V96_PREREGISTRATION.read_text(encoding="utf-8"))
    v92_result = json.loads(V92_RESULT.read_text(encoding="utf-8"))
    args.artifact_dir.mkdir(parents=True)
    paths = {
        "winner_v96_universal_calibrator.onnx": args.artifact_dir
        / "winner_v96_universal_calibrator.onnx",
        "winner_v96_locomotion_default_off.onnx": args.artifact_dir
        / "winner_v96_locomotion_default_off.onnx",
        "winner_v96_locomotion_enabled_zero.onnx": args.artifact_dir
        / "winner_v96_locomotion_enabled_zero.onnx",
        "winner_v96_locomotion_stress.onnx": args.artifact_dir
        / "winner_v96_locomotion_stress.onnx",
    }
    source_calibrator = args.training_work_root / "graphs/winner_v22_final.onnx"
    zero_parameters = networks.initialize_locomotion_adapter_parameters(seed=60721)
    stressed_parameters = v96.stress_parameters(zero_parameters)
    networks.export_universal_calibrator_onnx(
        source_calibrator,
        np.asarray(v96.builder.UNIVERSAL_TARGET, dtype=np.float32),
        paths["winner_v96_universal_calibrator.onnx"],
    )
    networks.export_locomotion_onnx(
        v96.POLICY,
        zero_parameters,
        paths["winner_v96_locomotion_default_off.onnx"],
        adapter_enabled=False,
    )
    networks.export_locomotion_onnx(
        v96.POLICY,
        zero_parameters,
        paths["winner_v96_locomotion_enabled_zero.onnx"],
        adapter_enabled=True,
        expose_adapter_delta=True,
    )
    networks.export_locomotion_onnx(
        v96.POLICY,
        stressed_parameters,
        paths["winner_v96_locomotion_stress.onnx"],
        adapter_enabled=True,
        expose_adapter_delta=True,
    )
    for path in paths.values():
        onnx.checker.check_model(onnx.load(path))
    artifact_hashes = {name: v96.sha256(path) for name, path in paths.items()}
    calibrator_session = v96.session(paths["winner_v96_universal_calibrator.onnx"])
    base_session = v96.session(v96.POLICY)
    off_session = v96.session(paths["winner_v96_locomotion_default_off.onnx"])
    zero_session = v96.session(paths["winner_v96_locomotion_enabled_zero.onnx"])
    stress_session = v96.session(paths["winner_v96_locomotion_stress.onnx"])
    signed, contexts = v96.run_signed_calibration(
        args, calibrator_session, v96_preregistration
    )
    handoff = v96.check_fail_closed(contexts[0])
    golden = v96.check_golden_replay(
        base_session, off_session, zero_session, zero_parameters, contexts[0]
    )
    same_input = check_same_input_numeric(base_session)
    stress = v96.check_stress(
        base_session, stress_session, stressed_parameters, contexts
    )
    stress_boundary = check_stress_boundary_numeric(stress_session, contexts)
    corrected_signed = bool(
        all_but(signed["checks"], "universal_target_chain_exact")
        and signed["checks"]["all_v92_receipts_exact"]
        and v92_result["maximum_bounded_target_action_error"] == 0.0
    )
    corrected_golden = bool(
        all_but(golden["checks"], "source_graph_matches_both_goldens_bit_exact")
        and same_input["all_at_most_frozen_1e_minus_6"]
    )
    corrected_stress = bool(
        all_but(stress["checks"], "absolute_and_rate_bounds_hold")
        and stress_boundary["absolute_and_rate_excess_at_most_1e_minus_6"]
    )
    abi = {
        "calibrator": v96.describe_abi(paths["winner_v96_universal_calibrator.onnx"]),
        "locomotion_default_off": v96.describe_abi(
            paths["winner_v96_locomotion_default_off.onnx"]
        ),
        "locomotion_enabled_zero": v96.describe_abi(
            paths["winner_v96_locomotion_enabled_zero.onnx"]
        ),
    }
    expected_abi = v96_preregistration["expected_abi"]
    abi_exact = bool(
        abi["calibrator"] == expected_abi["calibrator"]
        and abi["locomotion_default_off"] == expected_abi["locomotion"]
        and abi["locomotion_enabled_zero"]["inputs"]
        == expected_abi["locomotion"]["inputs"]
        and abi["locomotion_enabled_zero"]["outputs"][:3]
        == expected_abi["locomotion"]["outputs"]
    )
    checks = {
        "cpu_only_execution": jax.default_backend() == "cpu",
        "all_graph_hashes_unchanged_from_v96": artifact_hashes
        == builder.EXPECTED_ARTIFACTS,
        "exact_abis_unchanged": abi_exact,
        "corrected_signed_calibration_passes": corrected_signed,
        "all_invalid_handoffs_fail_closed": handoff["all_invalid_cases_rejected"],
        "corrected_golden_replay_passes": corrected_golden,
        "corrected_nonzero_stress_passes": corrected_stress,
        "all_corrected_metrics_finite": all(
            math.isfinite(value)
            for value in (
                same_input["maximum_abs"],
                stress_boundary["maximum_absolute_excess"],
                stress_boundary["maximum_rate_excess"],
            )
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed_checks
    result = {
        "schema_version": "winner_v97.mechanics_numeric_correction_result.v1",
        "status": (
            "PASS_WINNER_V97_MECHANICS_NUMERIC_CORRECTION"
            if passed
            else "HOLD_WINNER_V97_MECHANICS_NUMERIC_CORRECTION"
        ),
        "decision": (
            "PREREGISTER_RESPONSE_CONDITIONED_LOCOMOTION_TRAINING"
            if passed
            else "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "signed_calibration": signed,
        "signed_target_correction": {
            "v92_exact_receipts": signed["checks"]["all_v92_receipts_exact"],
            "v92_bounded_target_action_error": v92_result[
                "maximum_bounded_target_action_error"
            ],
            "corrected_pass": corrected_signed,
        },
        "handoff_fail_closed": handoff,
        "golden_replay": golden,
        "same_input_numeric_correction": same_input,
        "nonzero_adapter_stress": stress,
        "stress_boundary_numeric_correction": stress_boundary,
        "abi": abi,
        "artifact_sha256": artifact_hashes,
        "execution": {
            "simulator_cells": 4,
            "golden_ticks": 1200,
            "stress_cases": 256,
            "onnx_exports": 4,
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": preregistration["sources"],
        "source_manifest_sha256": preregistration["source_manifest_sha256"],
        "authority": preregistration["authority"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"failed_checks={failed_checks}")
    print(f"sha256={v96.sha256(args.output)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
