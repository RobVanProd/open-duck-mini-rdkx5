#!/usr/bin/env python3
"""Strictly import one exact Winner-v14 support-action diagnostic result."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping
import zipfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v14_support_action_diagnostic_preregistration.json"
FORMAL_RESULT = ANALYSIS / "winner_v13_support_controller_gate_result.json"
TRAINING_RESULT = ANALYSIS / "winner_v13_support_controller_training_result.json"
RUNNER = ROOT / "tools/run_winner_v14_support_action_diagnostic.py"
WORKFLOW = ROOT / ".github/workflows/winner-v14-support-action-diagnostic.yml"
OUTPUT_JSON = ANALYSIS / "winner_v14_support_action_diagnostic_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v14-support-action-diagnostic-result.json"
RAW_RECEIPT_NAME = "winner-v14-support-action-diagnostic-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
SCALES = [0.0, 0.25, 0.5, 0.75, 1.0]
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")


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


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def read_result_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v14 diagnostic artifact inventory changed")
        if sum(item.file_size for item in infos) > 25_000_000:
            raise ValueError("Winner-v14 diagnostic artifact exceeds size ceiling")
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
                raise ValueError("Winner-v14 diagnostic artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


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
    require_sha256(artifact_zip_sha256, "Winner-v14 diagnostic artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v14-support-action-diagnostic-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v14 diagnostic workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def cell_key(cell: Mapping[str, Any]) -> tuple[str, str, str | None]:
    condition = cell.get("condition")
    return (
        str(cell["configuration_id"]),
        str(cell["plant"]),
        None if condition is None else str(condition["id"]),
    )


def formal_cell_index(
    formal_checkpoint: Mapping[str, Any],
) -> dict[tuple[str, str, str | None], Mapping[str, Any]]:
    rows = (
        formal_checkpoint["core_model_plant_cells"]
        + formal_checkpoint["sensor_transport_plant_cells"]
    )
    index = {cell_key(row): row for row in rows}
    if len(rows) != 124 or len(index) != 124:
        raise ValueError("Winner-v13 formal cell index changed")
    return index


def scale_one_matches_formal(
    diagnostic: Mapping[str, Any], formal: Mapping[str, Any]
) -> bool:
    scalar_fields = (
        "configuration_id",
        "configuration_sha256",
        "plant",
        "condition",
        "terminal",
        "episode",
        "support_pass",
        "maximum_jax_onnx_hidden_error",
        "final_h_out",
        "constant_normalized_prediction_mse",
    )
    if any(diagnostic[name] != formal[name] for name in scalar_fields):
        return False
    if diagnostic["source_previous_action_out_exact"] is not True:
        return False
    return all(
        diagnostic["trace_hashes"][name] == formal["trace_hashes"][name]
        for name in ("observations", "actions", "predictions", "hidden")
    )


def require_finite(value: Any, label: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} is not finite")
    return number


def validate_cell(row: Mapping[str, Any], scale: float, *, sensor: bool) -> None:
    fields = {
        "condition",
        "configuration_id",
        "configuration_sha256",
        "constant_normalized_prediction_mse",
        "corrected_learned_normalized_prediction_mse",
        "episode",
        "final_h_out",
        "maximum_action_delta_excess",
        "maximum_jax_onnx_hidden_error",
        "plant",
        "scale",
        "scale_one_source_action_bit_exact",
        "source_previous_action_out_exact",
        "support_pass",
        "terminal",
        "trace_hashes",
        "transformed_previous_action_chain_exact",
    }
    if sensor:
        fields.add("prng")
    if set(row) != fields or row["scale"] != scale or row["plant"] not in PLANTS:
        raise ValueError("Winner-v14 diagnostic cell schema changed")
    require_sha256(row["configuration_sha256"], "configuration")
    if (
        type(row["support_pass"]) is not bool
        or type(row["scale_one_source_action_bit_exact"]) is not bool
        or type(row["source_previous_action_out_exact"]) is not bool
        or type(row["transformed_previous_action_chain_exact"]) is not bool
        or row["support_pass"] != (row["terminal"] is None)
        or not isinstance(row["final_h_out"], list)
        or len(row["final_h_out"]) != 64
    ):
        raise ValueError("Winner-v14 diagnostic cell accounting changed")
    for name in (
        "constant_normalized_prediction_mse",
        "corrected_learned_normalized_prediction_mse",
        "maximum_action_delta_excess",
        "maximum_jax_onnx_hidden_error",
    ):
        require_finite(row[name], name)
    if set(row["trace_hashes"]) != {
        "actions",
        "hidden",
        "observations",
        "predictions",
        "source_actions",
    }:
        raise ValueError("Winner-v14 diagnostic trace schema changed")
    for name, value in row["trace_hashes"].items():
        require_sha256(value, f"{name} trace")
    terminal = row["terminal"]
    if terminal is not None:
        if (
            not isinstance(terminal, dict)
            or not isinstance(terminal.get("checks"), dict)
            or all(terminal["checks"].values())
            or not isinstance(terminal.get("tick"), int)
            or not 0 <= terminal["tick"] < 250
        ):
            raise ValueError("Winner-v14 diagnostic terminal accounting changed")


def rederive_checkpoint(
    row: Mapping[str, Any],
    *,
    label: str,
    scale: float,
    formal_checkpoint: Mapping[str, Any],
) -> int:
    expected_fields = {
        "checkpoint_sha256",
        "checks",
        "core_model_plant_cells",
        "failed_checks",
        "heldout_context_separation",
        "heldout_prediction_corrected",
        "heldout_repeatability",
        "label",
        "onnx_sha256",
        "sensor_transport_plant_cells",
        "update",
    }
    if (
        set(row) != expected_fields
        or row["label"] != label
        or row["update"] != {"half": 50, "final": 100}[label]
        or row["checkpoint_sha256"] != formal_checkpoint["checkpoint_sha256"]
        or row["onnx_sha256"] != formal_checkpoint["onnx_sha256"]
    ):
        raise ValueError(f"Winner-v14 {scale}/{label} checkpoint identity changed")
    core = row["core_model_plant_cells"]
    sensor = row["sensor_transport_plant_cells"]
    repeats = row["heldout_repeatability"]
    contexts = row["heldout_context_separation"]
    predictor = row["heldout_prediction_corrected"]
    if (
        len(core) != 112
        or len(sensor) != 12
        or len(repeats) != 32
        or len(contexts) != 16
        or set(predictor) != set(PLANTS)
    ):
        raise ValueError(f"Winner-v14 {scale}/{label} population changed")
    for cell in core:
        validate_cell(cell, scale, sensor=False)
    for cell in sensor:
        validate_cell(cell, scale, sensor=True)
    all_cells = core + sensor
    formal_index = formal_cell_index(formal_checkpoint)
    diagnostic_index = {cell_key(cell): cell for cell in all_cells}
    if len(diagnostic_index) != 124 or set(diagnostic_index) != set(formal_index):
        raise ValueError(f"Winner-v14 {scale}/{label} cell keys changed")
    formal_matches = 0
    if scale == 1.0:
        for key, cell in diagnostic_index.items():
            comparable = dict(cell)
            comparable.pop("prng", None)
            if not scale_one_matches_formal(comparable, formal_index[key]):
                raise ValueError(f"Winner-v14 scale-one formal reproduction changed: {key}")
            formal_matches += 1
    for repeat in repeats:
        if (
            set(repeat)
            != {
                "bit_exact",
                "configuration_id",
                "first_trace_hashes",
                "plant",
                "repeat_trace_hashes",
            }
            or repeat["plant"] not in PLANTS
            or repeat["bit_exact"] is not True
            or repeat["first_trace_hashes"] != repeat["repeat_trace_hashes"]
        ):
            raise ValueError(f"Winner-v14 {scale}/{label} repeat changed")
    context_ids = []
    for context in contexts:
        if set(context) != {
            "configuration_id",
            "final_h_out_linf_separation",
            "separation_above_1e_7",
        }:
            raise ValueError(f"Winner-v14 {scale}/{label} context schema changed")
        configuration_id = context["configuration_id"]
        context_ids.append(configuration_id)
        pair = {
            cell["plant"]: cell
            for cell in core
            if cell["configuration_id"] == configuration_id
        }
        if set(pair) != set(PLANTS):
            raise ValueError(f"Winner-v14 {scale}/{label} context pair changed")
        separation = float(
            np.max(
                np.abs(
                    np.asarray(pair[PLANTS[0]]["final_h_out"], dtype=np.float32)
                    - np.asarray(pair[PLANTS[1]]["final_h_out"], dtype=np.float32)
                )
            )
        )
        if (
            context["final_h_out_linf_separation"] != separation
            or context["separation_above_1e_7"] != (separation > 1.0e-7)
        ):
            raise ValueError(f"Winner-v14 {scale}/{label} context was not rederived")
    for plant in PLANTS:
        heldout = [
            cell
            for cell in core
            if cell["configuration_id"] in context_ids and cell["plant"] == plant
        ]
        learned = float(
            np.mean(
                [cell["corrected_learned_normalized_prediction_mse"] for cell in heldout]
            )
        )
        constant = float(
            np.mean([cell["constant_normalized_prediction_mse"] for cell in heldout])
        )
        expected = {
            "corrected_learned_normalized_prediction_mse": learned,
            "constant_normalized_prediction_mse": constant,
            "learned_strictly_below_constant": learned < constant,
        }
        if predictor[plant] != expected:
            raise ValueError(f"Winner-v14 {scale}/{label} predictor was not rederived")
    expected_checks = {
        "exact_124_main_cells": len(all_cells) == 124,
        "all_support_cells_pass": all(cell["support_pass"] for cell in all_cells),
        "all_transformed_action_chains_exact": all(
            cell["transformed_previous_action_chain_exact"] for cell in all_cells
        ),
        "all_action_deltas_within_graph_bounds": all(
            cell["maximum_action_delta_excess"] <= 5.0e-7 for cell in all_cells
        ),
        "all_jax_onnx_hidden_errors_at_most_1e_7": all(
            cell["maximum_jax_onnx_hidden_error"] <= 1.0e-7 for cell in all_cells
        ),
        "all_32_heldout_repeats_bit_exact": len(repeats) == 32
        and all(repeat["bit_exact"] for repeat in repeats),
        "all_16_heldout_contexts_separate": len(contexts) == 16
        and all(context["separation_above_1e_7"] for context in contexts),
        "corrected_prediction_beats_constant_per_plant": all(
            value["learned_strictly_below_constant"] for value in predictor.values()
        ),
        "scale_one_source_action_bit_exact": scale != 1.0
        or all(cell["scale_one_source_action_bit_exact"] for cell in all_cells),
    }
    if (
        row["checks"] != expected_checks
        or row["failed_checks"]
        != sorted(name for name, passed in expected_checks.items() if not passed)
    ):
        raise ValueError(f"Winner-v14 {scale}/{label} checks were not rederived")
    return formal_matches


def validate_result(result: Mapping[str, Any]) -> None:
    expected_fields = {
        "authority",
        "decision",
        "execution",
        "failed_validity_checks",
        "passing_scales",
        "scale_results",
        "schema_version",
        "selected_scale",
        "sources",
        "status",
        "validity_checks",
    }
    if set(result) != expected_fields:
        raise ValueError("Winner-v14 diagnostic result schema changed")
    if (
        result["schema_version"] != "winner_v14.support_action_diagnostic_result.v1"
        or result["status"] != "PASS_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC"
        or result["execution"]
        != {
            "optimizer_updates": 0,
            "main_cells": 1240,
            "repeat_cells": 320,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or result["authority"]
        != {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes_only": (
                "a separate graph-transform contract for the selected scale, or a "
                "separate support-objective preregistration if no scale passes"
            ),
        }
    ):
        raise ValueError("Winner-v14 diagnostic authority or execution changed")
    expected_sources = {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "formal_result_sha256": lf_sha256(FORMAL_RESULT),
        "training_result_lf_sha256": lf_sha256(TRAINING_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }
    if result["sources"] != expected_sources:
        raise ValueError("Winner-v14 diagnostic source identities changed")
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    formal_rows = {row["label"]: row for row in formal["checkpoint_results"]}
    scale_results = result["scale_results"]
    if [row.get("scale") for row in scale_results] != SCALES:
        raise ValueError("Winner-v14 diagnostic scale order changed")
    formal_matches = 0
    main_cells = 0
    repeat_cells = 0
    for scale_result, scale in zip(scale_results, SCALES, strict=True):
        if set(scale_result) != {"scale", "complete_pass", "checkpoint_results"}:
            raise ValueError("Winner-v14 scale-result schema changed")
        checkpoints = scale_result["checkpoint_results"]
        if [row.get("label") for row in checkpoints] != ["half", "final"]:
            raise ValueError(f"Winner-v14 {scale} checkpoint order changed")
        for checkpoint in checkpoints:
            label = checkpoint["label"]
            formal_matches += rederive_checkpoint(
                checkpoint,
                label=label,
                scale=scale,
                formal_checkpoint=formal_rows[label],
            )
            main_cells += len(checkpoint["core_model_plant_cells"]) + len(
                checkpoint["sensor_transport_plant_cells"]
            )
            repeat_cells += len(checkpoint["heldout_repeatability"])
        complete = all(not checkpoint["failed_checks"] for checkpoint in checkpoints)
        if scale_result["complete_pass"] is not complete:
            raise ValueError(f"Winner-v14 {scale} complete-pass flag changed")
    passing = [row["scale"] for row in scale_results if row["complete_pass"]]
    selected = max(passing) if passing else None
    expected_validity = {
        "exact_scale_order": True,
        "exact_1240_main_cells": main_cells == 1240,
        "exact_320_repeat_cells": repeat_cells == 320,
        "scale_one_reproduces_all_248_formal_cells": formal_matches == 248,
        "cpu_only": True,
    }
    if (
        result["passing_scales"] != passing
        or result["selected_scale"] != selected
        or result["validity_checks"] != expected_validity
        or result["failed_validity_checks"]
        != sorted(name for name, passed in expected_validity.items() if not passed)
    ):
        raise ValueError("Winner-v14 diagnostic selection was not rederived")
    expected_decision = (
        "SELECT_MAXIMUM_FULL_PASS_SCALE_FOR_SEPARATE_TRANSFORM_CONTRACT"
        if selected is not None
        else "NO_SCALE_PASSES_PREREGISTER_SUPPORT_OBJECTIVE_REPAIR"
    )
    if result["decision"] != expected_decision:
        raise ValueError("Winner-v14 diagnostic decision was not rederived")


def compact_summary(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    summary = []
    for scale_result in result["scale_results"]:
        checkpoints = []
        for checkpoint in scale_result["checkpoint_results"]:
            cells = (
                checkpoint["core_model_plant_cells"]
                + checkpoint["sensor_transport_plant_cells"]
            )
            failures = [cell for cell in cells if not cell["support_pass"]]
            terminal_checks = Counter(
                name
                for cell in failures
                for name, passed in cell["terminal"]["checks"].items()
                if not passed
            )
            configurations = Counter(cell["configuration_id"] for cell in failures)
            separations = [
                row["final_h_out_linf_separation"]
                for row in checkpoint["heldout_context_separation"]
            ]
            checkpoints.append(
                {
                    "label": checkpoint["label"],
                    "checks": checkpoint["checks"],
                    "failed_checks": checkpoint["failed_checks"],
                    "support_failure_count": len(failures),
                    "support_failure_configuration_counts": dict(
                        sorted(configurations.items())
                    ),
                    "terminal_failed_check_counts": dict(sorted(terminal_checks.items())),
                    "failure_tick_range": (
                        [
                            min(cell["terminal"]["tick"] for cell in failures),
                            max(cell["terminal"]["tick"] for cell in failures),
                        ]
                        if failures
                        else None
                    ),
                    "failure_pitch_rad_range": (
                        [
                            min(cell["terminal"]["pitch_rad"] for cell in failures),
                            max(cell["terminal"]["pitch_rad"] for cell in failures),
                        ]
                        if failures
                        else None
                    ),
                    "heldout_context_separation_range": [
                        min(separations),
                        max(separations),
                    ],
                    "heldout_prediction_corrected": checkpoint[
                        "heldout_prediction_corrected"
                    ],
                }
            )
        summary.append(
            {
                "scale": scale_result["scale"],
                "complete_pass": scale_result["complete_pass"],
                "checkpoint_results": checkpoints,
            }
        )
    return summary


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
        raise FileExistsError("Winner-v14 diagnostic result is already imported")
    zip_sha = sha256(args.artifact_zip)
    attribution = repository_attribution(
        run_id=args.run_id,
        run_attempt=args.run_attempt,
        run_head_sha=args.run_head_sha,
        artifact_id=args.artifact_id,
        artifact_name=args.artifact_name,
        artifact_digest=args.artifact_digest,
        artifact_zip_sha256=zip_sha,
    )
    raw_bytes, receipt_bytes = read_result_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v14 diagnostic raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"))
    validate_result(result)
    payload = {
        "schema_version": "winner_v14.support_action_diagnostic_import.v1",
        "status": result["status"],
        "decision": result["decision"],
        "selected_scale": result["selected_scale"],
        "passing_scales": result["passing_scales"],
        "validity_checks": result["validity_checks"],
        "failed_validity_checks": result["failed_validity_checks"],
        "execution": result["execution"],
        "scale_summary": compact_summary(result),
        "repository_attribution": {
            **attribution,
            "artifact_zip_sha256": zip_sha,
            "artifact_zip_bytes": args.artifact_zip.stat().st_size,
            "raw_result_sha256": raw_sha,
            "raw_result_bytes": len(raw_bytes),
            "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "workflow_lf_sha256": lf_sha256(WORKFLOW),
            "runner_lf_sha256": lf_sha256(RUNNER),
            "importer_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": result["authority"],
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v14 support-action diagnostic result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Selected / passing scales: `{payload['selected_scale']} / {payload['passing_scales']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                "- Main / repeat cells: `1,240 / 320`",
                "- Optimizer / locomotion / robot access: `0 / 0 / 0`",
                "",
                "No candidate scale passed the unchanged gate. Every nonzero scale",
                "preserved heldout response context and beat the corrected constant",
                "predictor baseline, but every scale retained early pitch-only support",
                "failures. Inference amplitude scaling is closed; only a separately",
                "preregistered support-objective repair is authorized next.",
                "",
                "The 6.17 MB raw cell result remains hash-bound in the downloaded",
                "GitHub artifact; this repository stores the strictly rederived compact",
                "summary rather than duplicating the raw result.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"DECISION={payload['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
