#!/usr/bin/env python3
"""Build and audit V161's common trust-projected checkpoint pair."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import onnx
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from audit_winner_v140_preservation_projected_actor import (  # noqa: E402
    interpolate_model,
    make_dynamic_batch,
)
from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v161_uniform_trust_projection_preregistration.json"
)
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
OUTPUT = ANALYSIS / "winner_v161_uniform_trust_projection_result.json"
MARKDOWN = ANALYSIS / "WINNER_V161_UNIFORM_TRUST_PROJECTION_RESULT_20260725.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_source_dataset(manifest: list[dict[str, Any]]) -> dict[str, np.ndarray]:
    obs = []
    previous = []
    hidden = []
    action = []
    commands = []
    for item in manifest:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"V161 source trace changed: {path}")
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        if len(rows) != item["rows"]:
            raise ValueError(f"V161 source trace row count changed: {path}")
        for row in rows:
            obs.append(row["obs_state"])
            previous.append(
                row["policy_state_input"]["previous_action"][0]
            )
            hidden.append(row["policy_state_input"]["h_in"][0])
            action.append(row["action"])
            commands.append(float(row["obs_state"][6]))
    return {
        "obs": np.asarray(obs, dtype=np.float32),
        "previous_action": np.asarray(previous, dtype=np.float32),
        "h_in": np.asarray(hidden, dtype=np.float32),
        "action": np.asarray(action, dtype=np.float32),
        "command_x": np.asarray(commands, dtype=np.float32),
    }


def infer(path: Path, dataset: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    session = ort.InferenceSession(
        path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    action, hidden = session.run(
        ["continuous_actions", "h_out"],
        {
            "obs": dataset["obs"],
            "previous_action": dataset["previous_action"],
            "h_in": dataset["h_in"],
        },
    )
    return {"action": action, "hidden": hidden}


def build_pair(
    *,
    source: onnx.ModelProto,
    candidates: list[onnx.ModelProto],
    alpha: float,
    label: str,
    work: Path,
    transform: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[list[str]]]:
    rows = []
    changed_sets = []
    for candidate_id, candidate in zip(
        ("half", "final"), candidates, strict=True
    ):
        raw, changed = interpolate_model(source, candidate, alpha)
        raw_path = work / f"winner_v161_{candidate_id}_{label}_raw.onnx"
        deployed_path = (
            work / f"winner_v161_{candidate_id}_{label}_deployed.onnx"
        )
        dynamic_path = (
            work / f"winner_v161_{candidate_id}_{label}_dynamic.onnx"
        )
        onnx.save(raw, raw_path)
        contract = deploy_graph(raw_path, deployed_path, transform)
        onnx.save(make_dynamic_batch(onnx.load(deployed_path)), dynamic_path)
        rows.append(
            {
                "id": candidate_id,
                "raw": {"path": str(raw_path), "sha256": sha256(raw_path)},
                "deployed": contract,
                "dynamic": {
                    "path": str(dynamic_path),
                    "sha256": sha256(dynamic_path),
                },
            }
        )
        changed_sets.append(changed)
    return rows, changed_sets


def evaluate_pair(
    rows: list[dict[str, Any]],
    dataset: dict[str, np.ndarray],
    source_output: dict[str, np.ndarray],
    limit: float,
) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        output = infer(Path(row["dynamic"]["path"]), dataset)
        action_delta = output["action"] - source_output["action"]
        hidden_delta = output["hidden"] - source_output["hidden"]
        mse = float(np.mean(np.square(action_delta)))
        x0 = np.abs(dataset["command_x"]) <= 0.01
        result.append(
            {
                "id": row["id"],
                "action_mse": mse,
                "action_mse_to_limit": mse / limit,
                "action_linf": float(np.max(np.abs(action_delta))),
                "hidden_mse": float(np.mean(np.square(hidden_delta))),
                "hidden_linf": float(np.max(np.abs(hidden_delta))),
                "x0_nonzero_values": int(
                    np.count_nonzero(output["action"][x0])
                ),
                "all_outputs_finite": bool(
                    np.all(np.isfinite(output["action"]))
                    and np.all(np.isfinite(output["hidden"]))
                ),
            }
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    work = args.work_root.resolve()
    for path in (OUTPUT, MARKDOWN, work):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V161: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    input_paths = {
        "builder": TOOLS
        / "build_winner_v161_uniform_trust_projection_preregistration.py",
        "runner": Path(__file__).resolve(),
        "v140_runner": TOOLS
        / "audit_winner_v140_preservation_projected_actor.py",
        "deploy_tool": TOOLS
        / "run_winner_v129_oracle_teacher_cpu_contract.py",
        "v121_transform": V121_TRANSFORM,
        "v121_behavior": ANALYSIS / "winner_v121_nominal_behavior_result.json",
        "v128_transform": ANALYSIS
        / "winner_v128_deployment_transform_contract.json",
        "v128_behavior": ANALYSIS
        / "winner_v128_nominal_behavior_result.json",
        "v128_attribution": ANALYSIS
        / "winner_v128_nominal_failure_attribution.json",
        "v140_result": ANALYSIS
        / "winner_v140_preservation_projected_actor_result.json",
        "v160_result": ANALYSIS
        / "winner_v160_remaining_shadow_census_result.json",
        "source_raw": Path(
            prereg["sources"]["green_anchor"]["raw_path"]
        ),
        "half_raw": Path(
            prereg["sources"]["candidates"][0]["raw_path"]
        ),
        "final_raw": Path(
            prereg["sources"]["candidates"][1]["raw_path"]
        ),
    }
    observed_hashes = {
        name: sha256(path) for name, path in input_paths.items()
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V161_UNIFORM_TRUST_PROJECTION"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V161 preregistration changed")
    work.mkdir(parents=True)
    dataset = load_source_dataset(
        prereg["source_dataset"]["traces"]
    )
    source_model = onnx.load(input_paths["source_raw"])
    candidates = [
        onnx.load(input_paths["half_raw"]),
        onnx.load(input_paths["final_raw"]),
    ]
    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    source_rows, source_changed = build_pair(
        source=source_model,
        candidates=candidates,
        alpha=0.0,
        label="source",
        work=work,
        transform=transform,
    )
    source_output = infer(
        Path(source_rows[0]["dynamic"]["path"]), dataset
    )
    source_reproduction_linf = float(
        np.max(np.abs(source_output["action"] - dataset["action"]))
    )
    limit = float(prereg["projection"]["absolute_action_mse_limit"])
    full_rows, full_changed = build_pair(
        source=source_model,
        candidates=candidates,
        alpha=1.0,
        label="full",
        work=work,
        transform=transform,
    )
    full_metrics = evaluate_pair(full_rows, dataset, source_output, limit)
    lower = 0.0
    upper = 1.0
    trials = []
    selected_changed = None
    for index in range(int(prereg["projection"]["bisection_steps"])):
        alpha = (lower + upper) / 2.0
        rows, changed = build_pair(
            source=source_model,
            candidates=candidates,
            alpha=alpha,
            label=f"bisect_{index:02d}",
            work=work,
            transform=transform,
        )
        metrics = evaluate_pair(rows, dataset, source_output, limit)
        maximum = max(item["action_mse"] for item in metrics)
        trials.append(
            {
                "iteration": index,
                "alpha": alpha,
                "maximum_action_mse": maximum,
                "maximum_action_mse_to_limit": maximum / limit,
            }
        )
        if maximum <= limit:
            lower = alpha
            selected_changed = changed
        else:
            upper = alpha
    selected_alpha = lower
    selected_rows, selected_changed_final = build_pair(
        source=source_model,
        candidates=candidates,
        alpha=selected_alpha,
        label="selected",
        work=work,
        transform=transform,
    )
    selected_metrics = evaluate_pair(
        selected_rows, dataset, source_output, limit
    )
    maximum_selected_ratio = max(
        item["action_mse_to_limit"] for item in selected_metrics
    )
    selected_pair_outputs = [
        infer(Path(row["dynamic"]["path"]), dataset)
        for row in selected_rows
    ]
    selected_pair_action_linf = float(
        np.max(
            np.abs(
                selected_pair_outputs[0]["action"]
                - selected_pair_outputs[1]["action"]
            )
        )
    )
    selected_pair_hidden_linf = float(
        np.max(
            np.abs(
                selected_pair_outputs[0]["hidden"]
                - selected_pair_outputs[1]["hidden"]
            )
        )
    )
    changed_equal = (
        source_changed
        == full_changed
        == selected_changed_final
        and selected_changed is not None
        and selected_changed == selected_changed_final
    )
    checks = {
        "dataset_exact_4800x115": (
            dataset["obs"].shape == (4_800, 115)
            and dataset["previous_action"].shape == (4_800, 14)
            and dataset["h_in"].shape == (4_800, 64)
        ),
        "source_trace_reproduction_linf": (
            source_reproduction_linf <= 1.0e-6
        ),
        "full_pair_outside_common_budget": (
            max(item["action_mse"] for item in full_metrics) > limit
        ),
        "selected_alpha_strictly_between_zero_and_one": (
            0.0 < selected_alpha < 1.0
        ),
        "selected_pair_inside_common_budget": all(
            item["action_mse"] <= limit for item in selected_metrics
        ),
        "selected_common_budget_utilization_at_least_point99": (
            maximum_selected_ratio >= 0.99
        ),
        "initializer_change_sets_exact_and_nonempty": (
            changed_equal
            and all(bool(changed) for changed in selected_changed_final)
        ),
        "selected_pair_action_distinct": selected_pair_action_linf > 0.0,
        "selected_pair_hidden_distinct": selected_pair_hidden_linf > 0.0,
        "selected_x0_exact": all(
            item["x0_nonzero_values"] == 0 for item in selected_metrics
        ),
        "all_outputs_finite": all(
            item["all_outputs_finite"]
            for item in full_metrics + selected_metrics
        ),
        "both_deployment_graph_contracts_green": all(
            row["deployed"]["inference"]["pass"]
            for row in selected_rows
        ),
        "no_behavior_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v161.uniform_trust_projection_result.v1",
        "status": (
            "PASS_WINNER_V161_UNIFORM_TRUST_PROJECTION"
            if not failed
            else "HOLD_WINNER_V161_UNIFORM_TRUST_PROJECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "summary": {
            "absolute_action_mse_limit": limit,
            "source_trace_reproduction_linf": source_reproduction_linf,
            "selected_alpha": selected_alpha,
            "selected_upper_bound": upper,
            "maximum_selected_action_mse_to_limit": (
                maximum_selected_ratio
            ),
            "selected_pair_action_linf": selected_pair_action_linf,
            "selected_pair_hidden_linf": selected_pair_hidden_linf,
            "changed_initializers": selected_changed_final,
            "full_metrics": full_metrics,
            "selected_metrics": selected_metrics,
            "trials": trials,
        },
        "artifacts": {
            "work_root": str(work),
            "selected": selected_rows,
        },
        "decision": (
            "EARN_V162_UNIFORM_TRUST_PROJECTED_DUAL_CHECKPOINT_NOMINAL"
            if not failed
            else "CLOSE_UNIFORM_TRUST_PROJECTION_WITHOUT_BEHAVIOR"
        ),
        "authority": {
            "behavior_preregistration": not failed,
            "behavior": False,
            "training": False,
            "hosted_training": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V161 uniform trust projection result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Common alpha: `{selected_alpha:.9f}`.\n"
        "- Maximum selected preservation-budget use: "
        f"`{maximum_selected_ratio:.9f}`.\n"
        f"- Pair action separation: `{selected_pair_action_linf:.9f}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU graph transform only; no behavior, training, Colab, "
        "deployment, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
