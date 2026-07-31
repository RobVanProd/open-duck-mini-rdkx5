#!/usr/bin/env python3
"""Build and verify T74's fixed negative 3M/4M secant graphs."""

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
PREREG = ANALYSIS / "t74_signed_core_secant_preregistration.json"
OUTPUT = ANALYSIS / "t74_signed_core_secant_result.json"
MARKDOWN = ANALYSIS / "T74_SIGNED_CORE_SECANT_RESULT_20260728.md"
DEFAULT_WORK = (
    Path("D:/CodexArtifacts/open-duck-policy") / "t74_signed_core_secant_v1"
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


def verify_prereg(value: dict[str, Any]) -> None:
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
        actual != value["preregistered_contract_sha256"]
        or value["status"] != "PREREGISTERED_T74_SIGNED_CORE_SECANT"
        or value["failed_checks"]
    ):
        raise RuntimeError("T74 preregistration changed or is not green")
    for population in ("frozen_inputs", "raw_graphs"):
        for name, item in value[population].items():
            if not verify_receipt(item):
                raise RuntimeError(f"changed T74 {population}: {name}")
    for key, item in value["direction_contract"]["trace_population"].items():
        if not verify_receipt(item):
            raise RuntimeError(f"changed T74 direction trace: {key}")


def require_clean_worktree() -> str:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    if status.strip():
        raise RuntimeError("T74 execution requires a clean worktree")
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def values(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: numpy_helper.to_array(item).copy()
        for item in model.graph.initializer
    }


def build(
    source_path: Path,
    half_path: Path,
    final_path: Path,
    output_path: Path,
    coefficients: list[int],
    core: set[str],
) -> dict[str, Any]:
    model = onnx.load(str(source_path))
    source = values(model)
    half = values(onnx.load(str(half_path)))
    final = values(onnx.load(str(final_path)))
    if not (source.keys() == half.keys() == final.keys()):
        raise RuntimeError("T74 initializer inventories differ")
    changed = []
    expected_targets: dict[str, np.ndarray] = {}
    for index, initializer in enumerate(model.graph.initializer):
        name = initializer.name
        endpoint_changed = (
            not np.array_equal(source[name], half[name])
            or not np.array_equal(source[name], final[name])
        )
        if name in core:
            if not endpoint_changed:
                raise RuntimeError(f"T74 unchanged core initializer: {name}")
            c0, c1, c2 = map(np.float32, coefficients)
            target = (
                c0 * source[name] + c1 * half[name] + c2 * final[name]
            ).astype(source[name].dtype)
            model.graph.initializer[index].CopyFrom(
                numpy_helper.from_array(target, name=name)
            )
            changed.append(name)
            expected_targets[name] = target
        elif endpoint_changed:
            raise RuntimeError(f"T74 changed non-core initializer: {name}")
    onnx.checker.check_model(model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, output_path)
    stored = values(onnx.load(str(output_path)))
    formula_errors = {
        name: float(np.max(np.abs(stored[name] - target)))
        for name, target in expected_targets.items()
    }
    checks = {
        "exact_core_set": set(changed) == core,
        "all_noncore_source_exact": all(
            np.array_equal(stored[name], source[name])
            for name in source
            if name not in core
        ),
        "formula_exact": all(error == 0.0 for error in formula_errors.values()),
        "graph_checker_passed": True,
    }
    return {
        "raw": receipt(output_path),
        "coefficients_s_e1_e2": coefficients,
        "changed_initializers": sorted(changed),
        "formula_max_abs_errors": formula_errors,
        "checks": checks,
    }


def session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path), sess_options=options, providers=["CPUExecutionProvider"]
    )


def direction(
    prereg: dict[str, Any],
    source_path: Path,
    positive_final_path: Path,
    candidate_path: Path,
) -> dict[str, Any]:
    sessions = [
        session(path)
        for path in (source_path, positive_final_path, candidate_path)
    ]
    wanted = set(prereg["direction_contract"]["sample_ticks"])
    commands = set(prereg["direction_contract"]["commands"])
    cosines = []
    for key, item in sorted(
        prereg["direction_contract"]["trace_population"].items()
    ):
        if float(key.split("|")[-1]) not in commands:
            continue
        with Path(item["path"]).open("r", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if int(row["tick"]) not in wanted:
                    continue
                state = row["policy_state_input"]
                feed = {
                    "obs": np.asarray(
                        row["obs_state"], dtype=np.float32
                    )[None, :],
                    "previous_action": np.asarray(
                        state["previous_action"], dtype=np.float32
                    ),
                    "h_in": np.asarray(state["h_in"], dtype=np.float32),
                }
                actions = [
                    current.run(["continuous_actions"], feed)[0].ravel()
                    for current in sessions
                ]
                plus = actions[1] - actions[0]
                minus = actions[2] - actions[0]
                denominator = float(
                    np.linalg.norm(plus) * np.linalg.norm(minus)
                )
                if denominator > 1.0e-10:
                    cosines.append(
                        float(np.dot(plus, minus) / denominator)
                    )
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
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T74 transform requires --execute")
    work = args.work_root.resolve()
    for path in (OUTPUT, MARKDOWN, work):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T74: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_prereg(prereg)
    commit = require_clean_worktree()
    work.mkdir(parents=True)
    source = Path(prereg["raw_graphs"]["source"]["path"])
    half = Path(prereg["raw_graphs"]["positive_half"]["path"])
    final = Path(prereg["raw_graphs"]["positive_final"]["path"])
    core = set(prereg["core_initializers"])
    candidates = []
    for spec in prereg["mechanism"]["candidates"]:
        label = "3m" if spec["checkpoint_id"].endswith("3M") else "4m"
        raw_path = work / "raw" / f"{label}.onnx"
        transform = build(
            source,
            half,
            final,
            raw_path,
            spec["coefficients_s_e1_e2"],
            core,
        )
        deployment = t31.deployment_graph(
            raw_path, work / "deployment" / label
        )
        audit = direction(prereg, source, final, raw_path)
        candidates.append(
            {
                **spec,
                "label": label,
                "transform": transform,
                "direction_audit": audit,
                "deployment": deployment,
                "policy": {
                    **deployment["wrapped"],
                    "checkpoint_id": spec["checkpoint_id"],
                    "step": spec["pseudo_step"],
                },
            }
        )
    contract = prereg["direction_contract"]
    checks = {
        "exact_two_secant_candidates": len(candidates) == 2,
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
        "both_directions_remain_opposite": all(
            row["direction_audit"]["nonzero_pairs"]
            >= contract["minimum_nonzero_pairs_per_endpoint"]
            and row["direction_audit"]["fraction_negative_cosine"]
            >= contract[
                "minimum_fraction_negative_cosine_vs_positive_final"
            ]
            and row["direction_audit"]["cosine"]["median"]
            <= contract["maximum_median_cosine_vs_positive_final"]
            for row in candidates
        ),
        "no_behavior_training_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t74_signed_core_secant_result.v1",
        "status": (
            "PASS_T74_SIGNED_CORE_SECANT"
            if not failed
            else "HOLD_T74_SIGNED_CORE_SECANT"
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
                "# T74 signed recurrent-core secant result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                (
                    "- Negative-cosine fractions: `"
                    + ", ".join(
                        f"{row['label']}="
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
            f"{row['label']}_negative_cosine_fraction="
            f"{row['direction_audit']['fraction_negative_cosine']}"
        )
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
