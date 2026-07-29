#!/usr/bin/env python3
"""Preregister T99's deployment-coordinate correction of the T98 audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t99_deployment_coordinate_audit_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T99_DEPLOYMENT_COORDINATE_AUDIT_PREREGISTRATION_20260728.md"
)
T98_RESULT = ANALYSIS / "t98_hidden_expert_cpu_result.json"
T98_PREREG = ANALYSIS / "t98_hidden_expert_cpu_preregistration.json"
T97_PREREG = ANALYSIS / "t97_hidden_gate_preregistration.json"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
SOURCE_RAW = Path(
    "D:/CodexArtifacts/open-duck-policy/t78_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training/"
    "2026_07_28_183936_2007040.onnx"
)
SOURCE_DEPLOYED = Path(
    "D:/CodexArtifacts/open-duck-policy/t79_t78_postexport_v1/"
    "2007040/action_margin.onnx"
)

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t99_deployment_coordinate_audit.py",
    "test": ROOT / "tests" / "test_t99_deployment_coordinate_audit.py",
    "t31_deployment_transform": ROOT
    / "tools"
    / "run_t31_action_margin_trainthrough_cpu_smoke.py",
    "t22_deployment_transform": ROOT
    / "tools"
    / "run_t22_corrected_one_update_cpu_smoke.py",
    "t18_support_transform": ROOT
    / "tools"
    / "t18_rate_coherent_support_onnx.py",
    "t17_support_transform": ROOT
    / "tools"
    / "t17_support_homeomorphism_onnx.py",
    "t98_preregistration": T98_PREREG,
    "t98_result": T98_RESULT,
    "t97_preregistration": T97_PREREG,
    "hidden_gate": GATE,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T99 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T99 preregistration requires a clean worktree")

    t98 = json.loads(T98_RESULT.read_text(encoding="utf-8"))
    raw_zero = Path(t98["training"]["graphs"]["0"]["receipt"]["path"])
    raw_final = Path(t98["training"]["graphs"]["1024"]["receipt"]["path"])
    checks = {
        "t98_hold_is_coordinate_audit_only": (
            t98["status"] == "HOLD_T98_HIDDEN_EXPERT_CPU_CONTRACT"
            and t98["decision"] == "CLOSE_T98_HIDDEN_EXPERT_MECHANISM"
            and set(t98["failed_checks"])
            == {
                "final_gate_and_hidden_exact",
                "final_nominal_branch_bit_exact",
                "step_zero_trace_outputs_bit_exact",
            }
        ),
        "t98_training_mechanism_checks_green": all(
            t98["checks"][name]
            for name in (
                "command_exact",
                "every_critic_leaf_changed",
                "final_negative_deployed_action_binding",
                "final_negative_raw_action_binding",
                "graph_abi_and_cpu_chain_exact",
                "materialized_protected_source_exact",
                "normalizer_bit_exact",
                "only_negative_expert_actor_changed",
                "runner_readback_exact",
                "step_zero_random_chain_bit_exact",
                "step_zero_tree_exact",
                "trees_finite",
                "update_structure_exact",
            )
        ),
        "frozen_graphs_present": all(
            path.is_file()
            for path in (
                SOURCE_RAW,
                SOURCE_DEPLOYED,
                raw_zero,
                raw_final,
            )
        ),
        "coordinate_cause_is_frozen_t17_inverse": True,
        "no_retraining_threshold_or_mechanism_change": True,
        "no_behavior_hosted_or_robot_execution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T99 preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t99_deployment_coordinate_audit_preregistration.v1"
        ),
        "status": "PREREGISTERED_T99_DEPLOYMENT_COORDINATE_AUDIT",
        "question": (
            "Do the already-produced T98 step-0 and step-1024 graphs satisfy "
            "the unchanged causal contract after the frozen T17/T18/T31 "
            "deployment transform maps deployed observations into the "
            "training actor's source coordinates?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "invalidation": {
            "invalid_t98_checks": [
                "step_zero_trace_outputs_bit_exact",
                "final_gate_and_hidden_exact",
                "final_nominal_branch_bit_exact",
            ],
            "cause": (
                "T98 fed deployed-coordinate obs_state directly to a raw "
                "training graph. The frozen T17 support homeomorphism "
                "instead rewires raw actor obs through "
                "t17_source_obs before obs_normalized."
            ),
            "training_outcome_reused": True,
            "optimizer_rerun": False,
            "threshold_change": False,
            "gate_change": False,
            "head_change": False,
        },
        "population": {
            "checkpoint": "T78_JOINT_ADAPTER_FINAL",
            "ticks": [8, 16, 32],
            "nominal_rows": 18,
            "negative_com_rows": 18,
            "total_rows": 36,
            "reason": (
                "T98 restores T78 final; half-checkpoint rows are excluded "
                "from source-output equality while remaining part of the "
                "frozen gate's cross-checkpoint derivation."
            ),
        },
        "thresholds": {
            "step_zero_trace_bit_exact_rows": 36,
            "step_zero_random_chain_bit_exact_steps": 256,
            "final_nominal_bit_exact_rows": 18,
            "minimum_negative_raw_action_changed_fraction": 0.5,
            "minimum_negative_final_action_changed_fraction": 0.1,
            "minimum_maximum_negative_raw_action_delta": 1.0e-5,
        },
        "sources": {
            name: receipt(path) for name, path in SOURCE_FILES.items()
        },
        "graphs": {
            "source_raw": receipt(SOURCE_RAW),
            "source_deployed": receipt(SOURCE_DEPLOYED),
            "t98_raw_zero": receipt(raw_zero),
            "t98_raw_final": receipt(raw_final),
        },
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "The frozen deployment transform itself passes; deployed "
                "T98 step zero is bit-exact to deployed T78 final over all "
                "36 trace rows and 256 chained states; the fixed gate labels "
                "all 36 rows; postupdate h_out and all 18 nominal rows remain "
                "bit-exact; negative raw/final action binding meets the "
                "unchanged T98 fractional thresholds."
            ),
            "pass_decision": (
                "EARN_T100_HIDDEN_EXPERT_HOSTED_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_HIDDEN_EXPERT_AFTER_COORDINATE_CORRECTION",
        },
        "authority": {
            "one_read_only_postexport_audit": True,
            "optimizer_or_simulator": False,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T99 deployment-coordinate audit preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Reuses: exact existing T98 step-0 and step-1024 graphs",
                "- Correction: apply frozen T17/T18/T31 deployment transform before trace replay",
                "- Retraining / gate / head / threshold changes: `0 / 0 / 0 / 0`",
                "- Optimizer / behavior / hosted / robot: `0 / 0 / 0 / 0`",
                "",
                "A pass earns only a separate hosted-run preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
