#!/usr/bin/env python3
"""Freeze T93's read-only recurrent-adapter authority audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T80 = ANALYSIS / "t80_t78_nominal_matrix_result.json"
T92 = ANALYSIS / "t92_raw_t78_com_attribution_result.json"
RUNNER = ROOT / "tools" / "run_t93_adapter_authority_audit.py"
BUILDER = ROOT / "tools" / Path(__file__).name
TEST = ROOT / "tests" / "test_t93_adapter_authority_audit.py"
OUTPUT = ANALYSIS / "t93_adapter_authority_preregistration.json"
MARKDOWN = ANALYSIS / "T93_ADAPTER_AUTHORITY_PREREGISTRATION_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def trace_inventory(result: dict[str, Any], population: str) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for block in result["blocks"]:
        for cell in block["result"]["cells"]:
            path = Path(cell["protection"]["path"])
            inventory.append(
                {
                    "population": population,
                    "checkpoint_id": block["checkpoint_id"],
                    "fit_id": block["fit_id"],
                    "command_x_m_s": cell["command_x_m_s"],
                    "trace": receipt(path),
                }
            )
    return inventory


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T93 prereg: {path}")
    t80 = json.loads(T80.read_text(encoding="utf-8"))
    t92 = json.loads(T92.read_text(encoding="utf-8"))
    traces = [
        *trace_inventory(t80, "nominal"),
        *trace_inventory(t92, "com_x_negative"),
    ]
    policies = {
        item["checkpoint_id"]: receipt(Path(item["path"]))
        for item in json.loads(
            (ANALYSIS / "t80_t78_nominal_matrix_preregistration.json").read_text(
                encoding="utf-8"
            )
        )["policies"]
    }
    repository_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t80_result": T80,
        "t92_result": T92,
    }
    checks = {
        "t80_nominal_inventory_exact": len(
            [item for item in traces if item["population"] == "nominal"]
        )
        == 16,
        "t92_com_inventory_exact": len(
            [item for item in traces if item["population"] == "com_x_negative"]
        )
        == 16,
        "both_raw_checkpoints_exact": sorted(policies)
        == ["T78_JOINT_ADAPTER_FINAL", "T78_JOINT_ADAPTER_HALF"],
        "all_trace_and_policy_receipts_exact": all(
            Path(item["trace"]["path"]).is_file()
            and sha256(Path(item["trace"]["path"])) == item["trace"]["sha256"]
            for item in traces
        )
        and all(
            Path(item["path"]).is_file()
            and sha256(Path(item["path"])) == item["sha256"]
            for item in policies.values()
        ),
        "source_results_exact": (
            t80["status"] == "HOLD_T80_T78_NOMINAL_MATRIX"
            and t92["status"] == "PASS_T92_RAW_T78_COM_ATTRIBUTION"
            and t92["decision"] == "CLOSE_T78_ADAPTER_ENDPOINT_CONTINUATION"
        ),
        "read_only_trace_replay_only": True,
        "no_behavior_training_or_colab": True,
        "no_robot_or_rdk": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t93_adapter_authority_preregistration.v1",
        "status": (
            "PREREGISTERED_T93_ADAPTER_AUTHORITY_AUDIT"
            if not failed
            else "HOLD_T93_ADAPTER_AUTHORITY_PREREGISTRATION"
        ),
        "question": (
            "Did the T78 COM failure come from an explicit adapter-output cap, "
            "a saturated recurrent state, or downstream deployment wrappers "
            "erasing an otherwise material adapter response?"
        ),
        "policies": policies,
        "traces": traces,
        "measurements": {
            "intermediate_outputs": [
                "adapter_hidden_pre",
                "h_out",
                "adapter_location",
                "base_anchored_location",
                "raw_continuous_actions",
                "velocity_bounded_actions",
            ],
            "counterfactual": (
                "zero adapter_weight and adapter_bias only; replay the same "
                "recorded obs, previous_action, and h_in"
            ),
            "trace_output_tolerance": 1e-7,
            "nonzero_adapter_action_threshold": 0.005,
        },
        "classification_rule": {
            "hard_cap": {
                "predicate": (
                    "an explicit finite Clip or constant-bound Mul exists on "
                    "the adapter_location path before anchored_location"
                ),
                "classification": "EXPLICIT_ADAPTER_AUTHORITY_CAP_PRESENT",
                "decision": "EARN_EXACT_CAP_REMOVAL_CPU_SCREEN_ONLY",
            },
            "hidden_saturation": {
                "predicate": (
                    "no hard cap; failed moving COM hidden |h|>=0.99 fraction "
                    "is at least 0.50 and exceeds nominal moving by at least 0.10"
                ),
                "classification": "COM_FAILURE_ALIGNS_WITH_HIDDEN_SATURATION",
                "decision": "EARN_HIDDEN_RANGE_CPU_SCREEN_ONLY",
            },
            "downstream_suppression": {
                "predicate": (
                    "no prior predicate; COM moving final/pre-boundary adapter "
                    "L1 retention <=0.25 or >=50% material-adapter ticks are "
                    "erased to <=1e-7 by downstream wrappers"
                ),
                "classification": "DEPLOYMENT_WRAPPERS_SUPPRESS_ADAPTER_AUTHORITY",
                "decision": "EARN_WRAPPER_ORDER_CPU_SCREEN_ONLY",
            },
            "none": {
                "predicate": "none of the preceding predicates",
                "classification": "NO_HARD_ADAPTER_AUTHORITY_LIMIT_FOUND",
                "decision": "CLOSE_ADAPTER_AUTHORITY_HYPOTHESIS",
            },
            "ordered": True,
            "training_selection_weight": 0,
        },
        "repository_inputs": {
            name: receipt(path) for name, path in repository_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "trace_rows": 0,
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "audit_authorized": not failed,
            "successor_cpu_preregistration": False,
            "hosted_training": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T93 adapter-authority preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Failed checks: `{failed}`",
                "- Scope: read-only replay of 32 frozen nominal/COM traces",
                "- No simulator behavior, training, Colab, RDK, or robot",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"preregistered_contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
