#!/usr/bin/env python3
"""Attribute T20's hold to collapsed source and external rate vectors."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RESULT = (
    ANALYSIS / "t20_support_trainthrough_one_update_recovery_result.json"
)
V121_PREREG = (
    ANALYSIS / "winner_v121_deployment_transform_preregistration.json"
)
V121_CONTRACT = (
    ANALYSIS / "winner_v121_deployment_transform_contract.json"
)
T18_RESULT = ANALYSIS / "t18_rate_coherent_support_result.json"
FROZEN_RAW = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v119-extracted-20260724/"
    "winner_v119_transition_continuation/training/"
    "2026_07_24_193907_1003520.onnx"
)
FROZEN_DEPLOYED = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v121-deployment-policies-20260724/"
    "V121_DEPLOYMENT_1003520.onnx"
)
OUTPUT = ANALYSIS / "t20_two_rate_mismatch_attribution.json"
MARKDOWN = ANALYSIS / "T20_TWO_RATE_MISMATCH_ATTRIBUTION_20260726.md"


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


def initializers(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite T20 two-rate audit: {path}"
            )
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prereg = json.loads(V121_PREREG.read_text(encoding="utf-8"))
    contract = json.loads(V121_CONTRACT.read_text(encoding="utf-8"))
    t18 = json.loads(T18_RESULT.read_text(encoding="utf-8"))
    raw_path = Path(result["deployments"]["0"]["raw"]["path"])
    raw_model = onnx.load(raw_path)
    frozen_model = onnx.load(FROZEN_RAW)
    raw_initializers = initializers(raw_model)
    frozen_initializers = initializers(frozen_model)
    common = sorted(set(raw_initializers) & set(frozen_initializers))
    different = [
        name
        for name in common
        if not np.array_equal(
            raw_initializers[name], frozen_initializers[name]
        )
    ]
    source_delta = np.asarray(
        prereg["transform"]["exact_train_normalized_action_delta"],
        dtype=np.float32,
    )[None, :]
    full_delta = np.asarray(
        t18["wrappers"][0]["wrapper"]["maximum_action_delta"],
        dtype=np.float32,
    )[None, :]
    raw_delta = raw_initializers["max_action_delta"]
    frozen_delta = frozen_initializers["max_action_delta"]
    checks = {
        "formal_hold_is_exact_four_export_checks": (
            result.get("failed_checks")
            == [
                "both_physical_wrapper_contracts_pass",
                "step_zero_context_abi_byte_exact",
                "step_zero_physical_wrapper_byte_exact",
                "step_zero_raw_onnx_byte_exact",
            ]
        ),
        "restore_update_and_cpu_checks_green": all(
            result["checks"][name]
            for name in (
                "cpu_only",
                "cpu_topology_remap_leaf_exact",
                "source_restore_leaf_exact",
                "trained_structure_exact",
                "trained_tree_finite",
                "every_policy_leaf_updated",
                "every_critic_leaf_updated",
                "exact_exports_0_and_1024",
                "reward_metric_exact_steps",
                "reward_metric_finite",
                "formal_behavior_cells_zero",
                "hosted_compute_zero",
                "robot_access_zero",
            )
        ),
        "step_zero_raw_graph_structure_exact": (
            len(raw_model.graph.node) == len(frozen_model.graph.node) == 29
            and list(raw_initializers) == list(frozen_initializers)
            and [item.name for item in raw_model.graph.input]
            == [item.name for item in frozen_model.graph.input]
            and [item.name for item in raw_model.graph.output]
            == [item.name for item in frozen_model.graph.output]
        ),
        "only_raw_initializer_difference_is_rate_delta": (
            different == ["max_action_delta"]
        ),
        "t20_raw_uses_external_full_delta": np.array_equal(
            raw_delta, full_delta
        ),
        "frozen_v121_raw_uses_trained_source_delta": np.array_equal(
            frozen_delta, source_delta
        ),
        "source_and_external_deltas_are_distinct": (
            not np.array_equal(source_delta, full_delta)
            and float(np.max(np.abs(source_delta - full_delta))) > 0.0
        ),
        "v121_deployment_adds_missing_source_hierarchy": (
            len(onnx.load(FROZEN_DEPLOYED).graph.node)
            - len(frozen_model.graph.node)
            == 27
            and contract.get("status")
            == "PASS_WINNER_V121_DEPLOYMENT_TRANSFORM_CONTRACT"
        ),
        "context_adapter_itself_is_exact": all(
            row["context_parity"]["all_outputs_bit_exact"]
            and all(
                value == 0.0
                for value in row["context_parity"][
                    "maximum_abs_errors"
                ].values()
            )
            for row in result["deployments"].values()
        ),
        "no_hosted_or_robot_execution": (
            result["execution"]["hosted_or_colab_compute"] == 0
            and result["execution"]["robot_or_rdk_access"] == 0
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": "open_duck.t20_two_rate_attribution.v1",
        "status": (
            "PASS_T20_TWO_RATE_MISMATCH_ATTRIBUTION"
            if not failed
            else "HOLD_T20_TWO_RATE_MISMATCH_ATTRIBUTION"
        ),
        "decision": (
            "PREREGISTER_T21_TWO_RATE_SEPARATION"
            if not failed
            else "KEEP_T19_IMPLEMENTATION_CLOSED"
        ),
        "checks": checks,
        "failed_checks": failed,
        "attribution": {
            "cause": (
                "T20 passed the full measured physical rate vector through "
                "the policy/export source boundary. The frozen T18 "
                "composition keeps V121's trained rate vector at that source "
                "boundary and uses the full measured vector only after the "
                "support homeomorphism."
            ),
            "raw_graph_different_initializers": different,
            "maximum_normalized_delta_difference": float(
                np.max(np.abs(source_delta - full_delta))
            ),
            "source_normalized_action_delta": (
                source_delta[0].astype(float).tolist()
            ),
            "external_normalized_action_delta": (
                full_delta[0].astype(float).tolist()
            ),
            "correction": (
                "restore the source vector for actor export and both V121 "
                "source projections; retain the full vector only for T19's "
                "external physical projection"
            ),
            "t20_training_selection_weight": 0,
            "new_optimizer_steps_authorized": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "inputs": {
            "t20_result": receipt(RESULT),
            "t20_step_zero_raw": receipt(raw_path),
            "frozen_v121_raw": receipt(FROZEN_RAW),
            "frozen_v121_deployed": receipt(FROZEN_DEPLOYED),
            "v121_preregistration": receipt(V121_PREREG),
            "v121_contract": receipt(V121_CONTRACT),
            "t18_result": receipt(T18_RESULT),
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
                "# T20 two-rate mismatch attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- T20 policy-selection weight: `0`",
                "- New optimizer/hosted/robot execution: `0/0/0`",
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
