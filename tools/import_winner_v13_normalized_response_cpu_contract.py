#!/usr/bin/env python3
"""Import one exact Winner-v13 normalized-response CPU-contract result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v13_normalized_response_cpu_contract.json"
RUNNER = ROOT / "tools/run_winner_v13_normalized_response_cpu_contract.py"
PRIMITIVES = ROOT / "patches/winner_v13_normalized_calibrator_training.py"
WORKFLOW = ROOT / ".github/workflows/winner-v13-normalized-response-cpu-contract.yml"
OUTPUT_JSON = ANALYSIS / "winner_v13_normalized_response_cpu_contract_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v13-normalized-response-cpu-result.json"
RAW_RECEIPT_NAME = "winner-v13-normalized-response-cpu-result.sha256"
RAW_GRAPH_NAME = (
    "winner-v13-normalized-response-cpu-work/"
    "winner_v13_normalized_response_zero_cell.onnx"
)
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
EXPECTED_CHECKS = {
    "action_head_bit_exact",
    "all_stage1_gradients_nonzero",
    "contact_targets_exactly_one",
    "contact_targets_normalize_to_exact_zero",
    "exact_80_episode_training_population",
    "exported_action_exact_zero",
    "normalized_initial_loss_below_raw_initial_loss",
    "one_adam_update_exact",
    "one_update_reduces_same_batch_normalized_loss",
    "onnx_abi_exact",
    "onnx_jax_error_at_most_1e_7",
    "onnx_previous_action_chain_exact",
    "onnx_training_only_tensors_absent",
    "valid_transition_count_nonzero",
    "zero_contact_prediction_has_exact_zero_error",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def lf_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def read_result_artifact(path: Path) -> tuple[bytes, bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME, RAW_GRAPH_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v13 CPU artifact inventory changed")
        if sum(item.file_size for item in infos) > 10_000_000:
            raise ValueError("Winner-v13 CPU artifact exceeds the size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            file_type = stat.S_IFMT(mode)
            if (
                member.is_absolute()
                or ".." in member.parts
                or "." in member.parts
                or "\\" in info.filename
                or info.flag_bits & 0x1
                or info.is_dir()
                or file_type == stat.S_IFLNK
                or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v13 CPU artifact has an unsafe member")
        return (
            archive.read(RAW_RESULT_NAME),
            archive.read(RAW_RECEIPT_NAME),
            archive.read(RAW_GRAPH_NAME),
        )


def repository_attribution(
    *,
    run_id: int,
    run_attempt: int,
    run_head_sha: str,
    artifact_id: int,
    artifact_name: str,
    artifact_digest: str,
    artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v13 CPU artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v13-normalized-response-cpu-contract-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v13 CPU workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def validate_result(result: Mapping[str, Any]) -> None:
    expected_fields = {
        "authority",
        "checks",
        "decision",
        "execution",
        "failed_checks",
        "graph_contract",
        "objective_evidence",
        "schema_version",
        "sources",
        "status",
    }
    checks = result.get("checks")
    if (
        set(result) != expected_fields
        or result.get("schema_version")
        != "winner_v13.normalized_response_cpu_contract_result.v1"
        or result.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT"
        or result.get("decision")
        != "AUTHORIZE_NORMALIZED_RESPONSE_STAGE1_PREREGISTRATION_ONLY"
        or not isinstance(checks, dict)
        or set(checks) != EXPECTED_CHECKS
        or not all(type(value) is bool for value in checks.values())
        or not all(checks.values())
        or result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v13 CPU result did not pass exactly")
    if result.get("execution") != {
        "cpu_contract_optimizer_updates": 1,
        "full_training_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v13 CPU execution boundary changed")
    if result.get("authority") != {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": "a separate normalized-response Stage-1 preregistration",
    }:
        raise ValueError("Winner-v13 CPU authority changed")
    if result.get("sources") != {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "v13_primitives_lf_sha256": lf_sha256(PRIMITIVES),
    }:
        raise ValueError("Winner-v13 CPU source identities changed")
    evidence = result.get("objective_evidence", {})
    values = [
        evidence.get("v12_raw_coordinate_initial_loss"),
        evidence.get("v13_normalized_coordinate_initial_loss"),
        evidence.get("v13_normalized_coordinate_post_update_loss"),
        evidence.get("v12_to_v13_initial_loss_ratio"),
    ]
    if (
        evidence.get("all_values_finite") is not True
        or not all(isinstance(value, (int, float)) and float(value) > 0.0 for value in values)
        or not values[2] < values[1] < values[0]
        or evidence.get("contact_contract")
        != {
            "all_targets_exactly_one": True,
            "normalized_targets_exactly_zero": True,
            "target_mean": [1.0, 1.0],
            "target_std": [9.999999974752427e-07, 9.999999974752427e-07],
            "zero_prediction_error_exactly_zero": True,
        }
    ):
        raise ValueError("Winner-v13 CPU objective evidence changed")
    graph = result.get("graph_contract", {})
    require_sha256(graph.get("sha256"), "Winner-v13 CPU graph")
    if (
        graph.get("bytes") != 54896
        or graph.get("abi_exact") is not True
        or graph.get("training_only_tensors_absent") is not True
        or graph.get("jax_onnx_at_most_1e_7") is not True
        or graph.get("previous_action_out_equals_action_bit_exact") is not True
        or graph.get("chain_ticks") != 256
    ):
        raise ValueError("Winner-v13 CPU graph contract changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-artifact-zip", type=Path, required=True)
    parser.add_argument("--verification-run-id", type=int, required=True)
    parser.add_argument("--verification-run-attempt", type=int, required=True)
    parser.add_argument("--verification-run-head-sha", required=True)
    parser.add_argument("--verification-artifact-id", type=int, required=True)
    parser.add_argument("--verification-artifact-name", required=True)
    parser.add_argument("--verification-artifact-digest", required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v13 CPU result is already imported")
    artifact_zip_sha = sha256(args.result_artifact_zip)
    attribution = repository_attribution(
        run_id=args.verification_run_id,
        run_attempt=args.verification_run_attempt,
        run_head_sha=args.verification_run_head_sha,
        artifact_id=args.verification_artifact_id,
        artifact_name=args.verification_artifact_name,
        artifact_digest=args.verification_artifact_digest,
        artifact_zip_sha256=artifact_zip_sha,
    )
    raw_bytes, receipt_bytes, graph_bytes = read_result_artifact(
        args.result_artifact_zip
    )
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v13 CPU raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"))
    validate_result(result)
    if (
        sha256_bytes(graph_bytes) != result["graph_contract"]["sha256"]
        or len(graph_bytes) != result["graph_contract"]["bytes"]
    ):
        raise ValueError("Winner-v13 CPU graph artifact changed")
    payload = dict(result)
    payload["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": artifact_zip_sha,
        "artifact_zip_bytes": args.result_artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "graph_artifact_sha256": sha256_bytes(graph_bytes),
        "contract_path": str(CONTRACT.relative_to(ROOT)).replace("\\", "/"),
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    evidence = payload["objective_evidence"]
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v13 normalized-response CPU-contract result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / attempt: `{args.verification_run_id} / 1`",
                f"- Artifact ID / ZIP SHA-256: `{args.verification_artifact_id}` / `{artifact_zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                f"- v12 raw-coordinate initial loss: `{evidence['v12_raw_coordinate_initial_loss']}`",
                f"- v13 normalized initial / one-update loss: `{evidence['v13_normalized_coordinate_initial_loss']} / {evidence['v13_normalized_coordinate_post_update_loss']}`",
                f"- Initial loss ratio: `{evidence['v12_to_v13_initial_loss_ratio']}`",
                f"- ONNX SHA-256 / JAX max error: `{payload['graph_contract']['sha256']} / {payload['graph_contract']['jax_onnx_max_abs_error']}`",
                "- Full training / formal support / locomotion / robot access: `0 / 0 / 0 / 0`",
                "",
                "This pass authorizes only a separate normalized-response Stage-1",
                "preregistration. It does not authorize support training, locomotion,",
                "checkpoint selection, deployment, Gate 5, or hardware access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
