#!/usr/bin/env python3
"""Build and verify T72's two signed recurrent-core mirror graphs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t72_signed_core_mirror_preregistration.json"
OUTPUT = ANALYSIS / "t72_signed_core_mirror_result.json"
MARKDOWN = ANALYSIS / "T72_SIGNED_CORE_MIRROR_RESULT_20260728.md"
DEFAULT_WORK = (
    Path("D:/CodexArtifacts/open-duck-policy") / "t72_signed_core_mirror_v1"
)
sys.path.insert(0, str(ROOT / "tools"))
import run_t31_action_margin_trainthrough_cpu_smoke as t31  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def verify_receipt(item: dict[str, Any]) -> bool:
    path = Path(item["path"])
    return (
        path.is_file()
        and path.stat().st_size == item["bytes"]
        and sha256(path) == item["sha256"]
    )


def verify_preregistration(value: dict[str, Any]) -> None:
    expected = value["preregistered_contract_sha256"]
    actual = hashlib.sha256(
        json.dumps(
            {
                key: item
                for key, item in value.items()
                if key != "preregistered_contract_sha256"
            },
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if (
        actual != expected
        or value["status"] != "PREREGISTERED_T72_SIGNED_CORE_MIRROR"
        or value["failed_checks"]
    ):
        raise RuntimeError("T72 preregistration changed or is not green")
    for population in ("frozen_inputs", "closed_mechanisms", "raw_graphs"):
        for name, item in value[population].items():
            if not verify_receipt(item):
                raise RuntimeError(f"changed T72 {population}: {name}")
    for key, item in value["direction_contract"]["trace_population"].items():
        if not verify_receipt(item):
            raise RuntimeError(f"changed T72 direction trace: {key}")


def require_clean_worktree() -> str:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    if status.strip():
        raise RuntimeError("T72 execution requires a clean worktree")
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def initializer_map(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: numpy_helper.to_array(item).copy()
        for item in model.graph.initializer
    }


def build_mirror(
    source_path: Path,
    endpoint_path: Path,
    output_path: Path,
    core_names: set[str],
) -> dict[str, Any]:
    source = onnx.load(str(source_path))
    endpoint = onnx.load(str(endpoint_path))
    source_values = initializer_map(source)
    endpoint_values = initializer_map(endpoint)
    if source_values.keys() != endpoint_values.keys():
        raise RuntimeError("T72 initializer inventory mismatch")
    changed: list[str] = []
    delta_metrics: dict[str, Any] = {}
    for index, initializer in enumerate(source.graph.initializer):
        name = initializer.name
        source_value = source_values[name]
        endpoint_value = endpoint_values[name]
        endpoint_changed = not np.array_equal(source_value, endpoint_value)
        if name in core_names:
            if not endpoint_changed:
                raise RuntimeError(f"T72 expected changed core tensor: {name}")
            mirrored = (
                np.float32(2.0) * source_value - endpoint_value
            ).astype(source_value.dtype)
            source.graph.initializer[index].CopyFrom(
                numpy_helper.from_array(mirrored, name=name)
            )
            changed.append(name)
            delta_metrics[name] = {
                "endpoint_delta_linf": float(
                    np.max(np.abs(endpoint_value - source_value))
                ),
                "mirror_delta_linf": float(
                    np.max(np.abs(mirrored - source_value))
                ),
                "mirror_formula_max_abs_error": float(
                    np.max(
                        np.abs(
                            mirrored
                            - (
                                np.float32(2.0) * source_value
                                - endpoint_value
                            )
                        )
                    )
                ),
            }
        elif endpoint_changed:
            raise RuntimeError(f"T72 non-core endpoint tensor changed: {name}")
    if set(changed) != core_names:
        raise RuntimeError("T72 exact core inventory not mirrored")
    onnx.checker.check_model(source)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(source, output_path)
    mirrored_values = initializer_map(onnx.load(str(output_path)))
    checks = {
        "exact_core_initializer_set": set(changed) == core_names,
        "all_noncore_initializers_source_exact": all(
            np.array_equal(mirrored_values[name], source_values[name])
            for name in source_values
            if name not in core_names
        ),
        "all_mirror_formulas_exact": all(
            item["mirror_formula_max_abs_error"] == 0.0
            for item in delta_metrics.values()
        ),
        "graph_checker_passed": True,
    }
    return {
        "raw": receipt(output_path),
        "changed_initializers": sorted(changed),
        "delta_metrics": delta_metrics,
        "checks": checks,
    }


def raw_session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path), sess_options=options, providers=["CPUExecutionProvider"]
    )


def read_ticks(path: Path, wanted: set[int]) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if int(row["tick"]) in wanted:
                rows.append(row)
    return rows


def direction_audit(
    prereg: dict[str, Any],
    source_path: Path,
    endpoint_path: Path,
    mirror_path: Path,
) -> dict[str, Any]:
    sessions = [
        raw_session(path)
        for path in (source_path, endpoint_path, mirror_path)
    ]
    wanted = set(prereg["direction_contract"]["sample_ticks"])
    commands = set(prereg["direction_contract"]["commands"])
    cosines: list[float] = []
    source_to_endpoint: list[float] = []
    source_to_mirror: list[float] = []
    for key, item in sorted(
        prereg["direction_contract"]["trace_population"].items()
    ):
        command = float(key.split("|")[-1])
        if command not in commands:
            continue
        for row in read_ticks(Path(item["path"]), wanted):
            state = row["policy_state_input"]
            feed = {
                "obs": np.asarray(row["obs_state"], dtype=np.float32)[None, :],
                "previous_action": np.asarray(
                    state["previous_action"], dtype=np.float32
                ),
                "h_in": np.asarray(state["h_in"], dtype=np.float32),
            }
            actions = [
                session.run(["continuous_actions"], feed)[0].ravel()
                for session in sessions
            ]
            plus = actions[1] - actions[0]
            minus = actions[2] - actions[0]
            plus_norm = float(np.linalg.norm(plus))
            minus_norm = float(np.linalg.norm(minus))
            denominator = plus_norm * minus_norm
            if denominator <= 1.0e-10:
                continue
            cosines.append(float(np.dot(plus, minus) / denominator))
            source_to_endpoint.append(plus_norm)
            source_to_mirror.append(minus_norm)
    return {
        "nonzero_pairs": len(cosines),
        "fraction_negative_cosine": float(
            np.mean(np.asarray(cosines) < 0.0)
        ),
        "cosine": {
            "minimum": min(cosines),
            "median": float(np.median(cosines)),
            "maximum": max(cosines),
        },
        "action_delta_l2": {
            "source_to_endpoint_median": float(
                np.median(source_to_endpoint)
            ),
            "source_to_mirror_median": float(np.median(source_to_mirror)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T72 transform requires --execute")
    work = args.work_root.resolve()
    for path in (OUTPUT, MARKDOWN, work):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T72: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    commit = require_clean_worktree()
    work.mkdir(parents=True)

    source_path = Path(prereg["raw_graphs"]["source"]["path"])
    endpoints = {
        "T72_SIGNED_CORE_MIRROR_HALF": Path(
            prereg["raw_graphs"]["endpoint_half"]["path"]
        ),
        "T72_SIGNED_CORE_MIRROR_FINAL": Path(
            prereg["raw_graphs"]["endpoint_final"]["path"]
        ),
    }
    core = set(prereg["core_initializers"])
    candidates: list[dict[str, Any]] = []
    for checkpoint_id, endpoint_path in endpoints.items():
        label = "half" if checkpoint_id.endswith("HALF") else "final"
        raw_path = work / "raw" / f"{label}.onnx"
        transform = build_mirror(
            source_path, endpoint_path, raw_path, core
        )
        deployment = t31.deployment_graph(
            raw_path, work / "deployment" / label
        )
        direction = direction_audit(
            prereg, source_path, endpoint_path, raw_path
        )
        candidates.append(
            {
                "checkpoint_id": checkpoint_id,
                "endpoint_label": label,
                "endpoint_raw": receipt(endpoint_path),
                "transform": transform,
                "direction_audit": direction,
                "deployment": deployment,
                "policy": {
                    **deployment["wrapped"],
                    "checkpoint_id": checkpoint_id,
                    "step": (
                        1_003_520 if label == "half" else 2_007_040
                    ),
                },
            }
        )

    direction_contract = prereg["direction_contract"]
    checks = {
        "exact_two_mirrored_candidates": len(candidates) == 2,
        "all_initializer_contracts_pass": all(
            all(row["transform"]["checks"].values()) for row in candidates
        ),
        "all_deployment_contracts_pass": all(
            row["deployment"]["source_deployment"]["inference"]["pass"]
            and row["deployment"]["context_parity"]["all_outputs_bit_exact"]
            and row["deployment"]["verification"]["outputs_exact"]
            and row["deployment"]["margin_contract"]["pass"]
            for row in candidates
        ),
        "both_directions_predominantly_opposite": all(
            row["direction_audit"]["nonzero_pairs"]
            >= direction_contract["minimum_nonzero_pairs_per_endpoint"]
            and row["direction_audit"]["fraction_negative_cosine"]
            >= direction_contract[
                "minimum_fraction_negative_cosine_per_endpoint"
            ]
            and row["direction_audit"]["cosine"]["median"]
            <= direction_contract["maximum_median_cosine_per_endpoint"]
            for row in candidates
        ),
        "no_behavior_training_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t72_signed_core_mirror_result.v1",
        "status": (
            "PASS_T72_SIGNED_CORE_MIRROR"
            if not failed
            else "HOLD_T72_SIGNED_CORE_MIRROR"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if not failed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": commit,
        "source_raw": receipt(source_path),
        "candidates": candidates,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "onnx_raw_transforms": 2,
            "onnx_deployment_transforms": 2,
            "simulator_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "condition7_behavior_preregistration": not failed,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T72 signed recurrent-core mirror result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                (
                    "- Negative-cosine fractions: `"
                    + ", ".join(
                        f"{row['endpoint_label']}="
                        f"{row['direction_audit']['fraction_negative_cosine']:.6f}"
                        for row in candidates
                    )
                    + "`"
                ),
                "- Behavior / optimizer / Colab / robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    for row in candidates:
        print(
            f"{row['endpoint_label']}_negative_cosine_fraction="
            f"{row['direction_audit']['fraction_negative_cosine']}"
        )
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
