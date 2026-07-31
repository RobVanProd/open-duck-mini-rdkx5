from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v20_joint_recurrent_support_training.py"
RESULT = ROOT / "outputs/analysis/winner_v20_joint_recurrent_support_training_result.json"


def load():
    spec = importlib.util.spec_from_file_location(
        "winner_v20_joint_recurrent_support_training_import", IMPORTER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checkpoint(module, label: str, update: int) -> dict:
    path = f"/tmp/winner-v20-joint-recurrent-training-work/graphs/winner_v20_{label}.onnx"
    graph_sha = "a" * 64
    contract = {
        "abi_exact": True,
        "all_chain_outputs_finite": True,
        "all_initializers_finite": True,
        "bytes": 54896,
        "chain_ticks": 250,
        "forbidden_training_or_privileged_tokens": [],
        "initializer_count": 9,
        "inputs": [
            {"name": "obs", "shape": [1, 115]},
            {"name": "previous_action", "shape": [1, 14]},
            {"name": "h_in", "shape": [1, 64]},
        ],
        "jax_onnx_at_most_1e_7": True,
        "jax_onnx_max_abs_error": 0.0,
        "outputs": [
            {"name": "calibration_actions", "shape": [1, 14]},
            {"name": "previous_action_out", "shape": [1, 14]},
            {"name": "h_out", "shape": [1, 64]},
        ],
        "path": path,
        "previous_action_out_equals_action_bit_exact": True,
        "sha256": graph_sha,
        "training_only_tensors_absent": True,
    }
    return {
        "label": label,
        "update": update,
        "snapshot": {},
        "graph": {
            "label": label,
            "update": update,
            "path": path,
            "sha256": graph_sha,
            "bytes": 54896,
            "contract": contract,
        },
    }


def test_expected_artifact_inventory_is_complete_and_exact() -> None:
    module = load()
    members = module.artifact_members()
    assert len(members) == 104
    assert module.RAW_RESULT in members
    assert module.RAW_RECEIPT in members
    assert (
        f"{module.WORK_PREFIX}/snapshots/snapshot_joint_recurrent_update_001.npz"
        in members
    )
    assert (
        f"{module.WORK_PREFIX}/snapshots/snapshot_joint_recurrent_update_100.npz"
        in members
    )
    assert f"{module.WORK_PREFIX}/graphs/winner_v20_half.onnx" in members
    assert f"{module.WORK_PREFIX}/graphs/winner_v20_final.onnx" in members


def test_runner_shaped_nested_graph_receipt_keeps_all_inherited_abi_checks() -> None:
    module = load()
    module.validate_graph(checkpoint(module, "half", 50), "half", 50)


@pytest.mark.parametrize(
    ("target", "key", "value"),
    [
        ("receipt", "sha256", "b" * 64),
        ("contract", "chain_ticks", 249),
        ("contract", "previous_action_out_equals_action_bit_exact", False),
    ],
)
def test_nested_graph_receipt_rejects_binding_or_contract_changes(
    target: str, key: str, value: object
) -> None:
    module = load()
    value_under_test = checkpoint(module, "half", 50)
    graph = value_under_test["graph"]
    (graph if target == "receipt" else graph["contract"])[key] = value
    with pytest.raises(ValueError):
        module.validate_graph(value_under_test, "half", 50)


def test_checkpoint_snapshot_binds_manifest_payload_while_update_stays_manifest_only() -> None:
    module = load()
    value_under_test = checkpoint(module, "half", 50)
    receipt = {
        "path": "/tmp/work/snapshot_joint_recurrent_update_050.npz",
        "sha256": "c" * 64,
        "bytes": 162114,
        "array_count": 34,
        "bit_exact_readback": True,
    }
    value_under_test["snapshot"] = receipt
    module.validate_checkpoint_snapshot_binding(
        value_under_test, {"update": 50, **receipt}, "half"
    )


def test_checkpoint_snapshot_rejects_manifest_payload_drift() -> None:
    module = load()
    value_under_test = checkpoint(module, "half", 50)
    receipt = {
        "path": "/tmp/work/snapshot_joint_recurrent_update_050.npz",
        "sha256": "c" * 64,
        "bytes": 162114,
        "array_count": 34,
        "bit_exact_readback": True,
    }
    value_under_test["snapshot"] = receipt
    with pytest.raises(ValueError):
        module.validate_checkpoint_snapshot_binding(
            value_under_test, {"update": 50, **receipt, "bytes": 162115}, "half"
        )


def test_imported_training_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    attribution = value["repository_attribution"]
    assert attribution["repository"] == "RobVanProd/open-duck-mini-rdkx5"
    assert attribution["github_run_attempt"] == 1
    assert attribution["artifact_zip_sha256"] == attribution[
        "github_artifact_digest"
    ].removeprefix("sha256:")
    assert attribution["preregistration_lf_sha256"] == module.lf_sha256(
        module.PREREGISTRATION
    )
    assert attribution["workflow_lf_sha256"] == module.lf_sha256(module.WORKFLOW)
    assert attribution["runner_lf_sha256"] == module.lf_sha256(module.RUNNER)
    assert attribution["v15_importer_lf_sha256"] == module.lf_sha256(
        module.V15_IMPORTER
    )
    assert attribution["importer_lf_sha256"] == module.lf_sha256(
        module.Path(module.__file__)
    )
