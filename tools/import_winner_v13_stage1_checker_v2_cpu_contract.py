#!/usr/bin/env python3
"""Import the exact passing Winner-v13 Stage-1 checker-v2 CPU result."""

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
CONTRACT = ANALYSIS / "winner_v13_stage1_checker_v2_cpu_contract.json"
INVALID = ANALYSIS / "winner_v13_normalized_response_stage1_invalid_attribution.json"
RUNNER = ROOT / "tools/run_winner_v13_stage1_checker_v2_cpu_contract.py"
PRIMITIVES = ROOT / "patches/winner_v13_normalized_calibrator_training.py"
WORKFLOW = ROOT / ".github/workflows/winner-v13-stage1-checker-v2-cpu-contract.yml"
OUTPUT_JSON = ANALYSIS / "winner_v13_stage1_checker_v2_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V13_STAGE1_CHECKER_V2_CPU_RESULT_20260721.md"
RAW_RESULT = "winner-v13-stage1-checker-v2-result.json"
RAW_RECEIPT = "winner-v13-stage1-checker-v2-result.sha256"
RAW_GRAPH = (
    "winner-v13-stage1-checker-v2-work/"
    "winner_v13_stage1_checker_v2_zero_cell.onnx"
)
EXPECTED_CHECKS = {
    "action_head_parameters_exact_zero",
    "all_outputs_finite",
    "declared_learning_rate_matches_executed_constant",
    "exact_256_same_input_cases",
    "graph_previous_action_out_equals_action_bit_exact",
    "nonzero_previous_action_can_produce_nonzero_bounded_action",
    "same_input_action_error_at_most_1e_7",
    "same_input_hidden_error_at_most_1e_7",
    "same_input_previous_action_out_error_at_most_1e_7",
    "standard_graph_contract_passes",
    "zero_previous_action_produces_exact_zero_action",
}
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


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


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = {RAW_RESULT, RAW_RECEIPT, RAW_GRAPH}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("checker-v2 CPU artifact inventory changed")
        if sum(item.file_size for item in infos) > 10_000_000:
            raise ValueError("checker-v2 CPU artifact exceeds size ceiling")
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
                raise ValueError("checker-v2 CPU artifact has unsafe member")
        return {name: archive.read(name) for name in names}


def validate_result(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v13.stage1_checker_v2_cpu_result.v2"
        or value.get("status")
        != "PASS_WINNER_V13_STAGE1_CHECKER_V2_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_FRESH_STAGE1_V2_PREREGISTRATION_ONLY"
        or value.get("failed_checks") != []
        or not isinstance(value.get("checks"), dict)
        or set(value["checks"]) != EXPECTED_CHECKS
        or not all(type(item) is bool and item for item in value["checks"].values())
    ):
        raise ValueError("checker-v2 CPU result did not pass exactly")
    if value.get("execution") != {
        "optimizer_updates": 0,
        "simulation_cells": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("checker-v2 CPU execution boundary changed")
    if value.get("authority") != {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": "a fresh corrected Stage-1 v2 preregistration",
    }:
        raise ValueError("checker-v2 CPU authority changed")
    if value.get("sources") != {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "invalid_attribution_lf_sha256": lf_sha256(INVALID),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "v13_primitives_lf_sha256": lf_sha256(PRIMITIVES),
    }:
        raise ValueError("checker-v2 CPU source identities changed")
    proof = value.get("proof", {})
    graph = proof.get("standard_graph_contract", {})
    if (
        proof.get("same_input_cases") != 256
        or proof.get("root_seed") != 131314
        or proof.get("maximum_action_error") != 0.0
        or proof.get("maximum_previous_action_out_error") != 0.0
        or proof.get("maximum_hidden_error", 1.0) > 1e-7
        or proof.get("nonzero_graph_action_cases") != 256
        or proof.get("executed_stage1_learning_rate") != 0.0001
        or graph.get("abi_exact") is not True
        or graph.get("training_only_tensors_absent") is not True
        or graph.get("jax_onnx_at_most_1e_7") is not True
        or graph.get("previous_action_out_equals_action_bit_exact") is not True
        or HEX64.fullmatch(str(graph.get("sha256"))) is None
        or graph.get("bytes") != 54896
    ):
        raise ValueError("checker-v2 CPU proof changed")


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
        raise FileExistsError("checker-v2 CPU result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != f"winner-v13-stage1-checker-v2-cpu-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("checker-v2 CPU repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(members[RAW_RESULT])
    if members[RAW_RECEIPT] != f"{raw_sha}  /tmp/{RAW_RESULT}\n".encode():
        raise ValueError("checker-v2 CPU result receipt changed")
    result = json.loads(members[RAW_RESULT].decode("utf-8"))
    validate_result(result)
    graph = result["proof"]["standard_graph_contract"]
    if sha256_bytes(members[RAW_GRAPH]) != graph["sha256"] or len(
        members[RAW_GRAPH]
    ) != graph["bytes"]:
        raise ValueError("checker-v2 graph artifact changed")
    payload = dict(result)
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
        "graph_artifact_sha256": sha256_bytes(members[RAW_GRAPH]),
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v13 Stage-1 checker-v2 CPU result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / attempt: `{args.run_id} / 1`",
                f"- Artifact ID / ZIP SHA-256: `{args.artifact_id}` / `{zip_sha}`",
                f"- Same-input action / previous-action error: `{payload['proof']['maximum_action_error']} / {payload['proof']['maximum_previous_action_out_error']}`",
                f"- Same-input hidden error: `{payload['proof']['maximum_hidden_error']}`",
                f"- Nonzero bounded-action cases: `{payload['proof']['nonzero_graph_action_cases']} / 256`",
                "- Optimizer / simulation / locomotion / robot access: `0 / 0 / 0 / 0`",
                "",
                "This pass authorizes only a fresh corrected Stage-1 v2 preregistration.",
                "It does not authorize support training, locomotion, deployment, or hardware.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
