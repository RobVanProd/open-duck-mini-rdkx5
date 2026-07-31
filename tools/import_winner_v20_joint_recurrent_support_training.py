#!/usr/bin/env python3
"""Safely import a completed Winner-v20 joint-recurrent training artifact."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v20_joint_recurrent_support_training_preregistration.json"
)
CPU_RESULT = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_v2_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
RUNNER = ROOT / "tools/run_winner_v20_joint_recurrent_support_training.py"
WORKFLOW = ROOT / ".github/workflows/winner-v20-joint-recurrent-support-training.yml"
V15_IMPORTER = ROOT / "tools/import_winner_v15_pitch_margin_support_training.py"
OUTPUT_JSON = ANALYSIS / "winner_v20_joint_recurrent_support_training_result.json"
OUTPUT_MD = (
    ANALYSIS / "WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING_RESULT_20260721.md"
)
RAW_RESULT = "winner-v20-joint-recurrent-training-result.json"
RAW_RECEIPT = "winner-v20-joint-recurrent-training-result.sha256"
WORK_PREFIX = "winner-v20-joint-recurrent-training-work"
CHECKS = {
    "exact_100_joint_updates",
    "exact_100_atomic_snapshots",
    "half_and_final_graphs_present",
    "all_updates_finite",
    "all_sampled_hidden_replays_at_most_1e_6",
    "all_action_boundaries_exact",
    "all_pitch_margin_rewards_exact",
    "pitch_margin_signal_nonzero_every_update",
    "update_1_chain_rule_gate_exact",
    "update_2_recurrent_opening_exact",
    "all_joint_leaves_changed_cumulatively",
    "auxiliary_predictor_bit_exact_frozen",
    "formal_support_cells_zero",
    "locomotion_steps_zero",
    "robot_or_rdk_access_zero",
}
RECURRENT_LEAVES = {
    "obs_weight",
    "previous_action_weight",
    "hidden_weight",
    "hidden_bias",
}
JOINT_LEAVES = RECURRENT_LEAVES | {
    "action_weight",
    "action_bias",
    "training_only_log_std",
    "training_only_value_weight",
    "training_only_value_bias",
}
METRIC_KEYS = {
    "update",
    "loss",
    "loss_metrics",
    "sampled_count",
    "valid_transition_count",
    "episode_receipts_sha256",
    "gradient_max_abs",
    "leaf_max_abs_delta",
    "action_boundary",
    "pitch_margin_reward",
}
LOSS_METRIC_KEYS = {
    "policy_loss",
    "value_loss",
    "entropy",
    "ratio_min",
    "ratio_max",
    "sampled_hidden_replay_max_abs_error",
}
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
GRAPH_RECEIPT_KEYS = {
    "label",
    "update",
    "path",
    "sha256",
    "bytes",
    "contract",
}
GRAPH_CONTRACT_KEYS = {
    "abi_exact",
    "all_chain_outputs_finite",
    "all_initializers_finite",
    "bytes",
    "chain_ticks",
    "forbidden_training_or_privileged_tokens",
    "initializer_count",
    "inputs",
    "jax_onnx_at_most_1e_7",
    "jax_onnx_max_abs_error",
    "outputs",
    "path",
    "previous_action_out_equals_action_bit_exact",
    "sha256",
    "training_only_tensors_absent",
}
SNAPSHOT_RECEIPT_KEYS = {
    "path",
    "sha256",
    "bytes",
    "array_count",
    "bit_exact_readback",
}
SNAPSHOT_MANIFEST_KEYS = SNAPSHOT_RECEIPT_KEYS | {"update"}


def _load_v15_importer():
    spec = importlib.util.spec_from_file_location(
        "winner_v15_training_import_helpers", V15_IMPORTER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load reviewed Winner-v15 importer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V15 = _load_v15_importer()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def finite(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(float(value))


def artifact_members() -> set[str]:
    return {
        RAW_RESULT,
        RAW_RECEIPT,
        *(
            f"{WORK_PREFIX}/snapshots/snapshot_joint_recurrent_update_{index:03d}.npz"
            for index in range(1, 101)
        ),
        f"{WORK_PREFIX}/graphs/winner_v20_half.onnx",
        f"{WORK_PREFIX}/graphs/winner_v20_final.onnx",
    }


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = artifact_members()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v20 training artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v20 training artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute()
                or ".." in member.parts
                or "." in member.parts
                or "\\" in info.filename
                or info.flag_bits & 1
                or info.is_dir()
                or file_type == stat.S_IFLNK
                or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v20 training artifact has unsafe member")
        return {name: archive.read(name) for name in names}


def validate_graph(row: Mapping[str, Any], label: str, update: int) -> None:
    if set(row) != {"label", "update", "snapshot", "graph"}:
        raise ValueError(f"Winner-v20 {label} checkpoint schema changed")
    receipt = row.get("graph")
    if not isinstance(receipt, Mapping) or set(receipt) != GRAPH_RECEIPT_KEYS:
        raise ValueError(f"Winner-v20 {label} graph receipt schema changed")
    contract = receipt.get("contract")
    expected_name = f"winner_v20_{label}.onnx"
    if (
        not isinstance(contract, Mapping)
        or set(contract) != GRAPH_CONTRACT_KEYS
        or row.get("label") != label
        or row.get("update") != update
        or receipt.get("label") != label
        or receipt.get("update") != update
        or PurePosixPath(str(receipt.get("path", "")).replace("\\", "/")).name
        != expected_name
        or contract.get("path") != receipt.get("path")
        or contract.get("sha256") != receipt.get("sha256")
        or contract.get("bytes") != receipt.get("bytes")
        or contract.get("initializer_count") != 9
        or contract.get("chain_ticks") != 250
        or contract.get("forbidden_training_or_privileged_tokens") != []
    ):
        raise ValueError(f"Winner-v20 {label} graph receipt changed")
    # Winner-v15's reviewed ABI verifier expects the ONNX contract directly in
    # row["graph"]. Winner-v20 deliberately wraps that contract in a payload
    # receipt so the ZIP bytes can be bound independently. Adapt only that
    # serialization layer; keep every inherited ABI and numerical check.
    V15.validate_graph(
        {"label": label, "update": update, "graph": contract}, label, update
    )


def validate_checkpoint_snapshot_binding(
    row: Mapping[str, Any], manifest_receipt: Mapping[str, Any], label: str
) -> None:
    checkpoint_receipt = row.get("snapshot")
    if (
        not isinstance(checkpoint_receipt, Mapping)
        or set(checkpoint_receipt) != SNAPSHOT_RECEIPT_KEYS
        or set(manifest_receipt) != SNAPSHOT_MANIFEST_KEYS
        or manifest_receipt.get("update") != row.get("update")
        or checkpoint_receipt
        != {key: manifest_receipt[key] for key in SNAPSHOT_RECEIPT_KEYS}
    ):
        raise ValueError(f"Winner-v20 {label} checkpoint snapshot binding changed")


def validate_result(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v20.joint_recurrent_support_training_result.v1"
        or value.get("status")
        != "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING_ARTIFACT"
        or value.get("decision")
        != "AUTHORIZE_SEPARATE_UNCHANGED_124_CELL_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or value.get("failed_checks") != []
    ):
        raise ValueError("Winner-v20 joint-recurrent training did not pass")
    checks = value.get("checks")
    if not isinstance(checks, dict) or set(checks) != CHECKS or not all(checks.values()):
        raise ValueError("Winner-v20 training checks changed")
    if value.get("execution") != {
        "optimizer_updates": 100,
        "scheduled_episode_slots": 2_000_000,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v20 execution boundary changed")
    if value.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "cpu_result_lf_sha256": lf_sha256(CPU_RESULT),
        "stage1_result_lf_sha256": lf_sha256(STAGE1_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v20 training sources changed")
    if value.get("authority") != {
        "formal_support_gate_executed": False,
        "locomotion_executed": False,
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "a separately frozen unchanged 124-cell support/context gate"
        ),
    }:
        raise ValueError("Winner-v20 authority changed")
    if value.get("source_stage1_snapshot") != {
        "sha256": "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af",
        "bytes": 189027,
    }:
        raise ValueError("Winner-v20 Stage-1 source changed")
    population = value.get("population", {})
    if (
        population.get("environments_per_update") != 80
        or population.get("cumulative_sampled_count", 0) <= 0
        or population.get("cumulative_valid_transition_count", 0) <= 0
        or population["cumulative_valid_transition_count"]
        > population["cumulative_sampled_count"]
    ):
        raise ValueError("Winner-v20 population changed")
    metrics = value.get("metrics")
    if (
        not isinstance(metrics, list)
        or len(metrics) != 100
        or [row.get("update") for row in metrics] != list(range(1, 101))
    ):
        raise ValueError("Winner-v20 update sequence changed")
    sampled_total = 0
    valid_total = 0
    for index, row in enumerate(metrics, 1):
        if set(row) != METRIC_KEYS:
            raise ValueError("Winner-v20 metric schema changed")
        sampled = row["sampled_count"]
        valid = row["valid_transition_count"]
        loss_metrics = row["loss_metrics"]
        gradients = row["gradient_max_abs"]
        deltas = row["leaf_max_abs_delta"]
        if (
            type(sampled) is not int
            or type(valid) is not int
            or not sampled >= valid > 0
            or not finite(row["loss"])
            or HEX64.fullmatch(str(row["episode_receipts_sha256"])) is None
            or not isinstance(loss_metrics, dict)
            or set(loss_metrics) != LOSS_METRIC_KEYS
            or not all(finite(item) for item in loss_metrics.values())
            or loss_metrics["sampled_hidden_replay_max_abs_error"] > 1.0e-6
            or not isinstance(gradients, dict)
            or set(gradients) != JOINT_LEAVES
            or not all(finite(item) and item >= 0.0 for item in gradients.values())
            or not isinstance(deltas, dict)
            or set(deltas) != JOINT_LEAVES
            or not all(finite(item) and item >= 0.0 for item in deltas.values())
        ):
            raise ValueError(f"Winner-v20 metric {index} changed")
        if index == 1 and not (
            all(gradients[name] == 0.0 and deltas[name] == 0.0 for name in RECURRENT_LEAVES)
            and all(
                gradients[name] > 0.0 and deltas[name] > 0.0
                for name in JOINT_LEAVES - RECURRENT_LEAVES
            )
        ):
            raise ValueError("Winner-v20 update-1 chain-rule evidence changed")
        if index == 2 and not all(
            gradients[name] > 0.0 and deltas[name] > 0.0 for name in JOINT_LEAVES
        ):
            raise ValueError("Winner-v20 update-2 recurrent evidence changed")
        V15.validate_boundary(row["action_boundary"], sampled)
        V15.validate_reward(row["pitch_margin_reward"], valid)
        sampled_total += sampled
        valid_total += valid
    if (
        sampled_total != population["cumulative_sampled_count"]
        or valid_total != population["cumulative_valid_transition_count"]
    ):
        raise ValueError("Winner-v20 cumulative counts changed")
    cumulative = value.get("joint_leaf_max_abs_delta")
    if (
        not isinstance(cumulative, dict)
        or set(cumulative) != JOINT_LEAVES
        or not all(finite(item) and item > 0.0 for item in cumulative.values())
    ):
        raise ValueError("Winner-v20 cumulative leaf deltas changed")
    snapshots = value.get("snapshot_manifest")
    if not isinstance(snapshots, list) or len(snapshots) != 100:
        raise ValueError("Winner-v20 snapshot manifest changed")
    for index, receipt in enumerate(snapshots, 1):
        if (
            set(receipt) != SNAPSHOT_MANIFEST_KEYS
            or receipt.get("update") != index
            or PurePosixPath(str(receipt.get("path", "")).replace("\\", "/")).name
            != f"snapshot_joint_recurrent_update_{index:03d}.npz"
            or HEX64.fullmatch(str(receipt.get("sha256"))) is None
            or receipt.get("bytes", 0) <= 0
            or receipt.get("array_count", 0) <= 0
            or receipt.get("bit_exact_readback") is not True
        ):
            raise ValueError(f"Winner-v20 snapshot {index} changed")
    checkpoints = value.get("persistent_checkpoints")
    if not isinstance(checkpoints, list) or len(checkpoints) != 2:
        raise ValueError("Winner-v20 checkpoints changed")
    validate_graph(checkpoints[0], "half", 50)
    validate_graph(checkpoints[1], "final", 100)
    validate_checkpoint_snapshot_binding(checkpoints[0], snapshots[49], "half")
    validate_checkpoint_snapshot_binding(checkpoints[1], snapshots[99], "final")
    if not finite(value.get("elapsed_seconds")) or value["elapsed_seconds"] <= 0.0:
        raise ValueError("Winner-v20 elapsed time changed")


def verify_payloads(members: Mapping[str, bytes], value: Mapping[str, Any]) -> None:
    for index, receipt in enumerate(value["snapshot_manifest"], 1):
        payload = members[
            f"{WORK_PREFIX}/snapshots/snapshot_joint_recurrent_update_{index:03d}.npz"
        ]
        if sha256_bytes(payload) != receipt["sha256"] or len(payload) != receipt["bytes"]:
            raise ValueError(f"Winner-v20 snapshot {index} payload changed")
    for row in value["persistent_checkpoints"]:
        graph = row["graph"]
        payload = members[f"{WORK_PREFIX}/graphs/winner_v20_{row['label']}.onnx"]
        if sha256_bytes(payload) != graph["sha256"] or len(payload) != graph["bytes"]:
            raise ValueError(f"Winner-v20 {row['label']} graph payload changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-zip", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--run-attempt", type=int, required=True)
    parser.add_argument("--run-head-sha", required=True)
    parser.add_argument("--artifact-id", type=int, required=True)
    parser.add_argument("--artifact-name", required=True)
    parser.add_argument("--artifact-digest", required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v20 training result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != f"winner-v20-joint-recurrent-training-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v20 repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(members[RAW_RESULT])
    if members[RAW_RECEIPT] != f"{raw_sha}  /tmp/{RAW_RESULT}\n".encode():
        raise ValueError("Winner-v20 result receipt changed")
    value = json.loads(members[RAW_RESULT].decode("utf-8"))
    validate_result(value)
    verify_payloads(members, value)
    payload = dict(value)
    payload["repository_attribution"] = {
        "repository": "RobVanProd/open-duck-mini-rdkx5",
        "github_run_id": args.run_id,
        "github_run_attempt": args.run_attempt,
        "github_run_head_sha": args.run_head_sha,
        "github_artifact_id": args.artifact_id,
        "github_artifact_name": args.artifact_name,
        "github_artifact_digest": args.artifact_digest,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(members[RAW_RECEIPT]),
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "v15_importer_lf_sha256": lf_sha256(V15_IMPORTER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    half, final = payload["persistent_checkpoints"]
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v20 joint-recurrent support-training result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                (
                    "- Sampled / valid transitions: "
                    f"`{payload['population']['cumulative_sampled_count']} / "
                    f"{payload['population']['cumulative_valid_transition_count']}`"
                ),
                (
                    "- Half / final graph SHA-256: "
                    f"`{half['graph']['sha256']} / {final['graph']['sha256']}`"
                ),
                "- Joint leaves: `all nine changed; auxiliary predictor frozen`",
                "- Formal support / locomotion / robot access: `0 / 0 / 0`",
                "",
                "This pass authorizes only a separate unchanged 124-cell-per-checkpoint",
                "support/context-gate preregistration. It is not robot clearance.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
