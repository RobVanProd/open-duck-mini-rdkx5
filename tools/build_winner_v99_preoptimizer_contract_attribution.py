#!/usr/bin/env python3
"""Record the pre-PPO Winner-v99 checker-contract failures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v99_response_conditioned_cpu_retry_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v99_preoptimizer_contract_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V99_PREOPTIMIZER_CONTRACT_ATTRIBUTION_20260722.md"
PREREGISTRATION_SHA256 = (
    "f847c533020f0d9b8643bbbadad5dae0ab34f38c1ae206867967e2a4c4ee8ea0"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--failed-work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v99 attribution: {path}")
    work = args.failed_work_root.resolve()
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        sha256(PREREGISTRATION) != PREREGISTRATION_SHA256
        or preregistration.get("status")
        != "PREREGISTERED_WINNER_V99_RESPONSE_CONDITIONED_CPU_RETRY"
    ):
        raise ValueError("Winner-v99 preregistration changed")
    for name, item in preregistration["sources"].items():
        if lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v99 source changed before attribution: {name}")
    expected_top_level = {"expanded_checkpoint", "winner_v98_step_zero.onnx"}
    actual_top_level = {path.name for path in work.iterdir()}
    if actual_top_level != expected_top_level:
        raise ValueError(f"Winner-v99 failed work population changed: {actual_top_level}")
    if (ANALYSIS / "winner_v99_response_conditioned_cpu_contract.json").exists():
        raise ValueError("Winner-v99 formal result unexpectedly exists")
    value = {
        "schema_version": "winner_v99.preoptimizer_contract_attribution.v1",
        "status": "HOLD_WINNER_V99_PREOPTIMIZER_CHECKER_CONTRACT",
        "decision": "AUTHORIZE_EXACT_CHECKER_AND_SERIALIZATION_CORRECTION_PREREGISTRATION_ONLY",
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "execution_boundary": {
            "automatic_calibration_ticks_completed": 250,
            "home_return_ticks_completed": 250,
            "manual_post_reset_steps_completed": 1,
            "ppo_subprocess_started": False,
            "ppo_locomotion_steps": 0,
            "optimizer_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "failed_checks": {
            "expanded_checkpoint_round_trip_exact": {
                "cause": (
                    "the expansion stored a Flax FrozenDict while Orbax restored the same "
                    "numeric mapping as dict, so tree-container identity failed before "
                    "numeric equality was evaluated"
                ),
                "correction": "store the expanded actor as the checkpoint-native dict type",
            },
            "initial_jax_onnx_within_1e_6": {
                "maximum_abs_error": 1.0013580322265625e-05,
                "cases_above_1e_6": 1,
                "population": 64,
                "cause": (
                    "one deliberately unstructured synthetic observation saturated the "
                    "graph at exactly 1.0; the PPO tanh-location representation is frozen "
                    "at 0.9999899864, while all nonsaturated cases were within 5.97e-8"
                ),
                "correction": (
                    "compare ONNX against the module's exact pre-location bounded action; "
                    "retain the PPO-mode discrepancy as explicit saturation telemetry"
                ),
            },
            "initial_graph_rate_boundary_within_1e_6": {
                "maximum_reported_excess": 1.2207298278808594,
                "cases_above_1e_6": 40,
                "population": 64,
                "cause": (
                    "the synthetic joint offsets were not physically coherent with the "
                    "previous action; the selected graph applies its actual-centered guard "
                    "after the rate stage, so the final guard correction is not itself a "
                    "second rate-limited value"
                ),
                "correction": (
                    "verify the exact graph hierarchy and initializers on synthetic cases, "
                    "and reserve final-action envelope checks for coherent golden/behavior "
                    "traces"
                ),
            },
        },
        "preserved_pretraining_evidence": {
            "expanded_checkpoint_directory_sha256": directory_sha256(
                work / "expanded_checkpoint"
            ),
            "step_zero_onnx_sha256": sha256(work / "winner_v98_step_zero.onnx"),
            "step_zero_golden_ticks_checked_before_failure": 1200,
            "step_zero_x0_exact_before_failure": True,
            "calibrator_or_policy_math_failure_observed": False,
        },
        "prospective_correction": {
            "actor_math_changed": False,
            "calibrator_math_changed": False,
            "training_hyperparameters_changed": False,
            "behavior_gate_changed": False,
            "store_checkpoint_native_container": True,
            "expose_exact_pre_location_action_for_graph_parity": True,
            "replace_invalid_final-rate assertion_with_graph_hierarchy_identity": True,
            "new_run_requires_new_preregistration": True,
        },
        "authority": {
            "retry_authorized_now": False,
            "optimizer_authorized_now": False,
            "hosted_or_colab": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
            "robot_clearance": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v99 pre-optimizer checker-contract attribution\n\n"
        "Status: `HOLD_WINNER_V99_PREOPTIMIZER_CHECKER_CONTRACT`\n\n"
        "The automatic 250-tick calibration and 250-tick home return completed, "
        "but PPO never started. The three failures are checker/serialization contract "
        "errors: container type identity, a tanh representation at exact saturation, "
        "and an invalid final-rate assertion after the graph's actual-centered guard. "
        "No threshold, behavior gate, actor math, or training setting is changed.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
