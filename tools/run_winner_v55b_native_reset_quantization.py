#!/usr/bin/env python3
"""Run the frozen Winner-v55b native reset-quantization attribution on CPU."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

PREREGISTRATION = ANALYSIS / "winner_v55b_native_reset_quantization_preregistration.json"
V55_RESULT = ANALYSIS / "winner_v55_reset_label_handoff_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
FULL_TRAINING_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def array_sha256(value: Any) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(b"\0")
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(b"\0")
    digest.update(array.tobytes())
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v55b.native_reset_quantization_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V55B_NATIVE_RESET_QUANTIZATION_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_30_ROW_CPU_ATTRIBUTION_ONLY"
        or value.get("frozen_attribution", {}).get("rows") != 30
        or value.get("execution_now", {}).get("simulator_steps") != 0
    ):
        raise ValueError("Winner-v55b preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v55b source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v55b source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v55b source manifest changed")


def finite_tree(value: Any) -> bool:
    if isinstance(value, Mapping):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_tree(item) for item in value)
    if isinstance(value, (float, np.floating)):
        return math.isfinite(float(value))
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--quantization-attribution-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.quantization_attribution_authorized:
        raise PermissionError(
            "Winner-v55b requires --offline-cpu-only --quantization-attribution-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v55b result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v55b summary: {markdown}")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v54_residual_teacher_causal as v54
    import winner_v43_static_target_teacher as v43

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v55b requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    if sha256(V55_RESULT) != preregistration["frozen_source"]["v55_result_sha256"]:
        raise ValueError("Winner-v55b V55 source changed")
    v55 = json.loads(V55_RESULT.read_text(encoding="utf-8"))
    raw_rows = {
        (row["configuration_id"], row["plant"]): row
        for row in v55["reset_audit"]["rows"]
    }
    smoke, gate, v53 = v54.configure_v53_modules()
    calibrator_design = gate.load_calibrator_design(
        json.loads(FULL_TRAINING_PREREGISTRATION.read_text(encoding="utf-8"))
    )
    matrix = json.loads(DOMAIN.read_text(encoding="utf-8"))["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    )
    by_id = {row["id"]: row for row in configurations}
    teacher_table = v43.load_teacher_table(
        json.loads(V42_RESULT.read_text(encoding="utf-8"))
    )
    source = preregistration["frozen_source"]
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file():
        raise FileNotFoundError(scene)
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v55b Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v55b canonical fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    checkpoint_path, graph_path = v53.checkpoint_paths(args.training_work_root, "final")
    snapshot = v53.load_snapshot_for_reviewed_gate(checkpoint_path)
    v53.validate_snapshot_for_reviewed_gate(snapshot)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    session = ort.InferenceSession(
        str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
    )

    rows = []
    zero_previous = np.zeros((14,), dtype=np.float32)
    zero_hidden = np.zeros((64,), dtype=np.float32)
    for configuration_id in source["teacher_configuration_ids"]:
        for plant in source["plants"]:
            episode = smoke.Episode(
                mujoco,
                scene,
                by_id[configuration_id],
                plant,
                calibrator_design,
                observer_type,
                args.canonical_fit,
            )
            raw = gate.ObservationTransport(None, None).observe(episode.observation())
            quantized = gate.native_quantize_observation(raw)
            outputs = session.run(
                ["calibration_actions", "previous_action_out", "h_out"],
                {
                    "obs": quantized[None, :],
                    "previous_action": zero_previous[None, :],
                    "h_in": zero_hidden[None, :],
                },
            )
            graph_action = np.asarray(outputs[0][0], dtype=np.float32)
            teacher_action = smoke.bounded_action_numpy(
                np.asarray(teacher_table[configuration_id], dtype=np.float32),
                zero_previous,
            )
            quantized_input = np.concatenate([quantized, zero_previous, zero_hidden])
            rows.append(
                {
                    "configuration_id": configuration_id,
                    "plant": plant,
                    "initial_contacts": list(episode.initial_contacts),
                    "raw_observation_sha256": array_sha256(raw),
                    "raw_hash_matches_v55": (
                        array_sha256(raw)
                        == raw_rows[(configuration_id, plant)]["observation_sha256"]
                    ),
                    "quantized_observation_sha256": array_sha256(quantized),
                    "quantized_input_sha256": array_sha256(quantized_input),
                    "bounded_teacher_action_sha256": array_sha256(teacher_action),
                    "graph_action_sha256": array_sha256(graph_action),
                    "graph_action_within_boundary": np.array_equal(
                        graph_action,
                        smoke.bounded_action_numpy(graph_action, zero_previous),
                    ),
                    "changed_observation_field_count": int(np.count_nonzero(raw != quantized)),
                    "maximum_quantization_delta": float(np.max(np.abs(raw - quantized))),
                }
            )
    groups: dict[str, set[str]] = {}
    members: dict[str, list[str]] = {}
    for row in rows:
        key = row["quantized_input_sha256"]
        groups.setdefault(key, set()).add(row["bounded_teacher_action_sha256"])
        members.setdefault(key, []).append(f"{row['configuration_id']}:{row['plant']}")
    conflicts = [
        {
            "quantized_input_sha256": key,
            "bounded_teacher_label_count": len(labels),
            "members": members[key],
        }
        for key, labels in sorted(groups.items())
        if len(labels) > 1
    ]
    conflict = bool(conflicts)
    classification = (
        "NATIVE_QUANTIZATION_CREATES_RESET_LABEL_CONFLICT"
        if conflict
        else "NATIVE_RESET_LABELS_REMAIN_SEPARABLE"
    )
    decision = (
        "AUTHORIZE_UNIVERSAL_FIRST_ACTION_FEASIBILITY_PREREGISTRATION_ONLY"
        if conflict
        else "AUTHORIZE_FIRST_TICK_TEACHER_MAPPING_CPU_CONTRACT_PREREGISTRATION_ONLY"
    )
    checks = {
        "exact_30_rows": len(rows) == 30,
        "all_raw_observation_hashes_match_v55": all(
            row["raw_hash_matches_v55"] for row in rows
        ),
        "all_initial_contacts_double": all(
            row["initial_contacts"] == [1, 1] for row in rows
        ),
        "all_graph_actions_within_boundary": all(
            row["graph_action_within_boundary"] for row in rows
        ),
        "all_values_finite": finite_tree(rows),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    result = {
        "schema_version": "winner_v55b.native_reset_quantization_result.v1",
        "status": (
            "PASS_WINNER_V55B_NATIVE_RESET_QUANTIZATION_ATTRIBUTION"
            if not failed_checks
            else "HOLD_WINNER_V55B_NATIVE_RESET_QUANTIZATION_ATTRIBUTION"
        ),
        "classification": classification,
        "decision": decision if not failed_checks else "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v55_result_sha256": sha256(V55_RESULT),
            "checkpoint_sha256": sha256(checkpoint_path),
            "onnx_sha256": sha256(graph_path),
        },
        "findings": {
            "raw_unique_input_count": len(
                {row["raw_observation_sha256"] for row in rows}
            ),
            "quantized_unique_input_count": len(groups),
            "quantized_unique_graph_action_count": len(
                {row["graph_action_sha256"] for row in rows}
            ),
            "bounded_teacher_label_count": len(
                {row["bounded_teacher_action_sha256"] for row in rows}
            ),
            "conflict_groups": conflicts,
        },
        "rows": rows,
        "checks": checks,
        "failed_checks": failed_checks,
        "execution": {
            "reset_rows": len(rows),
            "simulator_steps": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes": "one separate prospective CPU mechanism preregistration only",
        },
    }
    if not finite_tree(result):
        raise FloatingPointError("Winner-v55b result contains nonfinite values")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v55b native reset-quantization result",
                "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{classification}`",
                f"- Decision: `{result['decision']}`",
                f"- Raw / quantized inputs: `{result['findings']['raw_unique_input_count']} / {result['findings']['quantized_unique_input_count']}`",
                f"- Teacher labels / quantized graph actions: `{result['findings']['bounded_teacher_label_count']} / {result['findings']['quantized_unique_graph_action_count']}`",
                f"- Conflict groups: `{len(conflicts)}`",
                "- Simulator steps / optimizer / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
