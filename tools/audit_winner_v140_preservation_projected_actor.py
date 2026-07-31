#!/usr/bin/env python3
"""Project the V134 actor update onto the frozen preservation boundary."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRAINING = ROOT / "training"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TRAINING))

from build_winner_v113_postexport_policies import sha256  # noqa: E402
from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
)
import winner_v134_full_actor_teacher_distillation as teacher  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v140_preservation_projected_actor_preregistration.json"
)
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V134_RESULT = ANALYSIS / "winner_v134_full_actor_teacher_cpu_result_v3.json"
V139_RESULT = ANALYSIS / "winner_v139_reference_input_controllability_result.json"
OUTPUT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V140_PRESERVATION_PROJECTED_ACTOR_RESULT_20260725.md"
)
BISECTION_STEPS = 20
PRESERVATION_LIMIT = 0.01


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def interpolate_model(
    source: onnx.ModelProto,
    candidate: onnx.ModelProto,
    alpha: float,
) -> tuple[onnx.ModelProto, list[str]]:
    if len(source.graph.initializer) != len(candidate.graph.initializer):
        raise ValueError("V140 initializer count changed")
    result = copy.deepcopy(source)
    changed = []
    for target, left, right in zip(
        result.graph.initializer,
        source.graph.initializer,
        candidate.graph.initializer,
        strict=True,
    ):
        if left.name != right.name or left.name != target.name:
            raise ValueError("V140 initializer ordering changed")
        left_array = numpy_helper.to_array(left)
        right_array = numpy_helper.to_array(right)
        if left_array.shape != right_array.shape:
            raise ValueError(f"V140 initializer shape changed: {left.name}")
        if np.array_equal(left_array, right_array):
            continue
        if not np.issubdtype(left_array.dtype, np.floating):
            raise ValueError(f"V140 nonfloating initializer changed: {left.name}")
        interpolated = (
            left_array.astype(np.float64)
            + float(alpha)
            * (
                right_array.astype(np.float64)
                - left_array.astype(np.float64)
            )
        ).astype(left_array.dtype)
        target.CopyFrom(numpy_helper.from_array(interpolated, left.name))
        changed.append(left.name)
    onnx.checker.check_model(result)
    return result, changed


def make_dynamic_batch(model: onnx.ModelProto) -> onnx.ModelProto:
    result = copy.deepcopy(model)
    for value in list(result.graph.input) + list(result.graph.output):
        first = value.type.tensor_type.shape.dim[0]
        first.ClearField("dim_value")
        first.dim_param = "batch"
    onnx.checker.check_model(result)
    return result


def evaluate(
    model_path: Path,
    dataset: dict,
    source_action: np.ndarray,
    baseline_mse: float,
) -> tuple[dict, np.ndarray]:
    session = ort.InferenceSession(
        model_path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    action = session.run(
        ["continuous_actions"],
        {
            "obs": dataset["obs"].astype(np.float32),
            "previous_action": dataset["previous_action"].astype(np.float32),
            "h_in": dataset["h_in"].astype(np.float32),
        },
    )[0]
    corrected = dataset["corrected"]
    target = dataset["target_action"]
    corrected_mse = float(
        np.mean(np.square(action[corrected] - target[corrected]))
    )
    preservation_mse = float(
        np.mean(np.square(action[~corrected] - source_action[~corrected]))
    )
    x0 = np.abs(dataset["obs"][:, 6]) <= 0.01
    return (
        {
            "corrected_mse": corrected_mse,
            "corrected_ratio_to_source": corrected_mse / baseline_mse,
            "preservation_mse": preservation_mse,
            "preservation_ratio_to_corrected_baseline": (
                preservation_mse / baseline_mse
            ),
            "x0_nonzero_values": int(np.count_nonzero(action[x0])),
            "candidate_vs_source_linf": float(
                np.max(np.abs(action - source_action))
            ),
            "all_actions_finite": bool(np.all(np.isfinite(action))),
        },
        action,
    )


def save_trial(
    *,
    source_model: onnx.ModelProto,
    candidate_model: onnx.ModelProto,
    alpha: float,
    label: str,
    work: Path,
    transform: dict,
) -> tuple[Path, dict, list[str]]:
    raw_model, changed = interpolate_model(source_model, candidate_model, alpha)
    raw_path = work / f"winner_v140_raw_{label}.onnx"
    deployed_path = work / f"winner_v140_deployed_{label}.onnx"
    dynamic_path = work / f"winner_v140_dynamic_{label}.onnx"
    onnx.save(raw_model, raw_path)
    contract = deploy_graph(raw_path, deployed_path, transform)
    onnx.save(make_dynamic_batch(onnx.load(deployed_path)), dynamic_path)
    return dynamic_path, contract, changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-raw", type=Path, required=True)
    parser.add_argument("--candidate-raw", type=Path, required=True)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V140: {path}")
    source_raw = args.source_raw.resolve()
    candidate_raw = args.candidate_raw.resolve()
    teacher_root = args.teacher_run_root.resolve()
    work = args.work_root.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {
        "runner": file_sha256(Path(__file__).resolve()),
        "v121_transform": file_sha256(V121_TRANSFORM),
        "v131_behavior_result": file_sha256(V131_RESULT),
        "v134_cpu_result": file_sha256(V134_RESULT),
        "v139_reference_result": file_sha256(V139_RESULT),
        "teacher_loader": file_sha256(
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "source_raw": file_sha256(source_raw),
        "candidate_raw": file_sha256(candidate_raw),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V140 preregistration changed")
    work.mkdir(parents=True)
    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    dataset = teacher.load_teacher_dataset(teacher_root)
    source_model = onnx.load(source_raw)
    candidate_model = onnx.load(candidate_raw)
    source_dynamic, source_contract, changed = save_trial(
        source_model=source_model,
        candidate_model=candidate_model,
        alpha=0.0,
        label="source",
        work=work,
        transform=transform,
    )
    source_session = ort.InferenceSession(
        source_dynamic.read_bytes(), providers=["CPUExecutionProvider"]
    )
    source_action = source_session.run(
        ["continuous_actions"],
        {
            "obs": dataset["obs"].astype(np.float32),
            "previous_action": dataset["previous_action"].astype(np.float32),
            "h_in": dataset["h_in"].astype(np.float32),
        },
    )[0]
    corrected = dataset["corrected"]
    baseline_mse = float(
        np.mean(
            np.square(
                source_action[corrected]
                - dataset["target_action"][corrected]
            )
        )
    )
    source_metrics, _ = evaluate(
        source_dynamic, dataset, source_action, baseline_mse
    )
    full_dynamic, full_contract, full_changed = save_trial(
        source_model=source_model,
        candidate_model=candidate_model,
        alpha=1.0,
        label="full",
        work=work,
        transform=transform,
    )
    full_metrics, _ = evaluate(
        full_dynamic, dataset, source_action, baseline_mse
    )
    if full_metrics["preservation_ratio_to_corrected_baseline"] <= (
        PRESERVATION_LIMIT
    ):
        raise ValueError("V140 full update unexpectedly inside boundary")
    lower = 0.0
    upper = 1.0
    trials = []
    for index in range(BISECTION_STEPS):
        alpha = (lower + upper) / 2.0
        dynamic_path, _, _ = save_trial(
            source_model=source_model,
            candidate_model=candidate_model,
            alpha=alpha,
            label=f"bisect_{index:02d}",
            work=work,
            transform=transform,
        )
        metrics, _ = evaluate(
            dynamic_path, dataset, source_action, baseline_mse
        )
        trials.append(
            {
                "iteration": index,
                "alpha": alpha,
                "preservation_ratio": metrics[
                    "preservation_ratio_to_corrected_baseline"
                ],
            }
        )
        if (
            metrics["preservation_ratio_to_corrected_baseline"]
            <= PRESERVATION_LIMIT
        ):
            lower = alpha
        else:
            upper = alpha
    selected_alpha = lower
    selected_dynamic, selected_contract, selected_changed = save_trial(
        source_model=source_model,
        candidate_model=candidate_model,
        alpha=selected_alpha,
        label="selected",
        work=work,
        transform=transform,
    )
    selected_metrics, _ = evaluate(
        selected_dynamic, dataset, source_action, baseline_mse
    )
    source_reproduction = float(
        np.max(np.abs(source_action - dataset["base_action"]))
    )
    checks = {
        "dataset_exact_4800_with_71_corrections": (
            dataset["obs"].shape == (4_800, 115)
            and int(np.sum(corrected)) == 71
        ),
        "source_reproduces_recorded_base": source_reproduction <= 1.0e-6,
        "source_and_full_initializer_delta_sets_exact": (
            changed == full_changed == selected_changed and len(changed) > 0
        ),
        "full_update_reproduces_preservation_failure": (
            full_metrics["preservation_ratio_to_corrected_baseline"]
            > PRESERVATION_LIMIT
        ),
        "selected_alpha_strictly_between_zero_and_one": (
            0.0 < selected_alpha < 1.0
        ),
        "selected_preservation_within_one_percent": (
            selected_metrics["preservation_ratio_to_corrected_baseline"]
            <= PRESERVATION_LIMIT
        ),
        "selected_corrected_ratio_at_most_point95": (
            selected_metrics["corrected_ratio_to_source"] <= 0.95
        ),
        "selected_x0_exact": selected_metrics["x0_nonzero_values"] == 0,
        "all_actions_finite": (
            source_metrics["all_actions_finite"]
            and full_metrics["all_actions_finite"]
            and selected_metrics["all_actions_finite"]
        ),
        "all_export_contracts_pass": all(
            row["inference"]["pass"]
            for row in (
                source_contract,
                full_contract,
                selected_contract,
            )
        ),
        "no_training_behavior_or_hosted_compute": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v140.preservation_projected_actor.v1",
        "status": (
            "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
            if not failed
            else "HOLD_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "method": {
            "source": "V134 raw step 0 / V121 final",
            "candidate": "V134 raw two-update full-actor smoke",
            "path": "linear interpolation of changed ONNX initializers",
            "constraint": (
                "largest alpha whose full 4,729-row preservation MSE is "
                "<=0.01 times the 71-row source corrected baseline"
            ),
            "bisection_steps": BISECTION_STEPS,
            "selection_uses_corrected_error": False,
            "optimizer_or_training": False,
        },
        "summary": {
            "baseline_corrected_mse": baseline_mse,
            "source_reproduction_linf": source_reproduction,
            "changed_initializers": changed,
            "full_metrics": full_metrics,
            "selected_alpha": selected_alpha,
            "selected_upper_bound": upper,
            "selected_metrics": selected_metrics,
            "trials": trials,
        },
        "artifacts": {
            "work_root": str(work),
            "selected_dynamic": {
                "path": str(selected_dynamic),
                "sha256": sha256(selected_dynamic),
            },
            "selected_deployed": selected_contract,
        },
        "decision": (
            "EARN_ONE_V141_DUAL_CHECKPOINT_BEHAVIOR_PREREGISTRATION"
            if not failed
            else "CLOSE_PRESERVATION_PROJECTED_ACTOR"
        ),
        "authority": {
            "behavior_preregistration": not failed,
            "behavior_evaluation": False,
            "training": False,
            "hosted_training": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V140 preservation-projected actor\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Selected alpha: `{selected_alpha:.9f}`.\n"
        f"- Corrected ratio: "
        f"`{selected_metrics['corrected_ratio_to_source']:.9f}`.\n"
        f"- Preservation ratio: "
        f"`{selected_metrics['preservation_ratio_to_corrected_baseline']:.9f}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU graph projection only; no training, behavior, Colab, or "
        "hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
