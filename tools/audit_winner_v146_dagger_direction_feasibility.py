#!/usr/bin/env python3
"""Audit whether any preservation-feasible point exists on V145's direction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import onnx
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRAINING = ROOT / "training"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TRAINING))

from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
)
from run_winner_v134_full_actor_teacher_cpu_contract import (  # noqa: E402
    action_metrics,
)
from audit_winner_v140_preservation_projected_actor import (  # noqa: E402
    interpolate_model,
    make_dynamic_batch,
)
import winner_v134_full_actor_teacher_distillation as v134  # noqa: E402
import winner_v145_on_policy_dagger as dagger  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v146_dagger_direction_preregistration.json"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V145_RESULT = ANALYSIS / "winner_v145_on_policy_dagger_cpu_result.json"
OUTPUT = ANALYSIS / "winner_v146_dagger_direction_result.json"
MARKDOWN = ANALYSIS / "WINNER_V146_DAGGER_DIRECTION_RESULT_20260725.md"
PRESERVATION_LIMIT = 0.01
CORRECTION_LIMIT = 0.95
BISECTION_STEPS = 20


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def infer(path: Path, data: dict) -> tuple[np.ndarray, np.ndarray]:
    session = ort.InferenceSession(
        path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    action, _, hidden = session.run(
        None,
        {
            "obs": data["obs"].astype(np.float32),
            "previous_action": data["previous_action"].astype(np.float32),
            "h_in": data["h_in"].astype(np.float32),
        },
    )
    return action, hidden


def metrics(action: np.ndarray, dataset: dict, selection: np.ndarray) -> dict:
    return action_metrics(
        action[selection],
        dataset["target_action"][selection],
        dataset["base_action"][selection],
        dataset["corrected"][selection],
    )


def save_trial(
    *,
    source: onnx.ModelProto,
    candidate: onnx.ModelProto,
    alpha: float,
    label: str,
    work: Path,
    transform: dict,
) -> tuple[Path, dict]:
    model, _ = interpolate_model(source, candidate, alpha)
    raw = work / f"winner_v146_raw_{label}.onnx"
    deployed = work / f"winner_v146_deployed_{label}.onnx"
    dynamic = work / f"winner_v146_dynamic_{label}.onnx"
    onnx.save(model, raw)
    contract = deploy_graph(raw, deployed, transform)
    onnx.save(make_dynamic_batch(onnx.load(deployed)), dynamic)
    return dynamic, contract


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    parser.add_argument("--shadow-trace", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V146: {path}")
    teacher_root = args.teacher_run_root.resolve()
    shadow_trace = args.shadow_trace.resolve()
    work = args.work_root.resolve()
    v145 = json.loads(V145_RESULT.read_text(encoding="utf-8"))
    source_raw = Path(v145["exports"]["0"]["raw_path"])
    candidate_raw = Path(v145["exports"]["2"]["raw_path"])
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v121_transform": sha256(V121_TRANSFORM),
        "v145_result": sha256(V145_RESULT),
        "v134_loader": sha256(
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "v145_loader": sha256(
            TRAINING / "winner_v145_on_policy_dagger.py"
        ),
        "source_raw": sha256(source_raw),
        "candidate_raw": sha256(candidate_raw),
        "shadow_trace": sha256(shadow_trace),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V146_DAGGER_DIRECTION_FEASIBILITY"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V146 preregistration changed")
    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    work.mkdir(parents=True)
    source_model = onnx.load(source_raw)
    candidate_model = onnx.load(candidate_raw)
    source_dynamic, source_contract = save_trial(
        source=source_model,
        candidate=candidate_model,
        alpha=0.0,
        label="source",
        work=work,
        transform=transform,
    )
    teacher = v134.load_teacher_dataset(teacher_root)
    shadow = dagger.load_shadow_dataset(shadow_trace)
    teacher_action, teacher_hidden = infer(source_dynamic, teacher)
    shadow_action, shadow_hidden = infer(source_dynamic, shadow)
    dataset = dagger.build_aggregated_dataset(
        teacher_root=teacher_root,
        shadow_trace=shadow_trace,
        teacher_baseline_action=teacher_action,
        teacher_baseline_hidden=teacher_hidden,
        shadow_baseline_action=shadow_action,
        shadow_baseline_hidden=shadow_hidden,
    )
    teacher_selection = dataset["source"] == "teacher"
    shadow_selection = dataset["source"] == "shadow"

    def evaluate_alpha(alpha: float, label: str) -> tuple[dict, dict]:
        dynamic, contract = save_trial(
            source=source_model,
            candidate=candidate_model,
            alpha=alpha,
            label=label,
            work=work,
            transform=transform,
        )
        action, _ = infer(dynamic, dataset)
        row = {
            "alpha": alpha,
            "all": metrics(
                action, dataset, np.ones(len(action), dtype=np.bool_)
            ),
            "teacher": metrics(action, dataset, teacher_selection),
            "shadow": metrics(action, dataset, shadow_selection),
        }
        row["maximum_preservation_ratio"] = max(
            row[name]["preservation_ratio_to_corrected_baseline"]
            for name in ("all", "teacher", "shadow")
        )
        row["maximum_correction_ratio"] = max(
            row[name]["corrected_ratio_to_zero_predictor"]
            for name in ("all", "teacher", "shadow")
        )
        return row, contract

    source_metrics, _ = evaluate_alpha(0.0, "alpha_0")
    full_metrics, _ = evaluate_alpha(1.0, "alpha_1")
    lower = 0.0
    upper = 1.0
    trials = []
    for index in range(BISECTION_STEPS):
        alpha = (lower + upper) / 2.0
        row, _ = evaluate_alpha(alpha, f"bisect_{index:02d}")
        trials.append(row)
        if row["maximum_preservation_ratio"] <= PRESERVATION_LIMIT:
            lower = alpha
        else:
            upper = alpha
    selected, selected_contract = evaluate_alpha(lower, "selected")
    checks = {
        "source_preservation_exact": (
            source_metrics["maximum_preservation_ratio"] == 0.0
        ),
        "source_correction_ratio_exact_one": (
            source_metrics["maximum_correction_ratio"] == 1.0
        ),
        "full_reproduces_v145_shadow_preservation_hold": (
            full_metrics["shadow"][
                "preservation_ratio_to_corrected_baseline"
            ]
            > PRESERVATION_LIMIT
        ),
        "selected_preservation_all_subsets_green": (
            selected["maximum_preservation_ratio"] <= PRESERVATION_LIMIT
        ),
        "selected_correction_all_subsets_green": (
            selected["maximum_correction_ratio"] <= CORRECTION_LIMIT
        ),
        "selected_export_contract_green": selected_contract["inference"][
            "pass"
        ],
        "selection_uses_only_preservation": True,
        "no_training_behavior_or_hosted_compute": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v146.dagger_direction_result.v1",
        "status": (
            "PASS_WINNER_V146_DAGGER_DIRECTION_FEASIBILITY"
            if not failed
            else "HOLD_WINNER_V146_DAGGER_DIRECTION_FEASIBILITY"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "method": {
            "path": "exact ONNX initializer interpolation V140->V145",
            "selection": (
                "largest alpha satisfying <=0.01 preservation on overall, "
                "teacher, and shadow subsets"
            ),
            "bisection_steps": BISECTION_STEPS,
            "correction_selection_weight": 0,
        },
        "source": source_metrics,
        "full": full_metrics,
        "selected": selected,
        "selected_upper_bound": upper,
        "trials": trials,
        "artifact": {
            "deployed": selected_contract,
            "work_root": str(work),
        },
        "decision": (
            "EARN_ONE_V147_PROJECTED_DAGGER_BEHAVIOR_PREREGISTRATION"
            if not failed
            else "CLOSE_GLOBAL_DAGGER_DIRECTION"
        ),
        "authority": {
            "behavior_preregistration": not failed,
            "behavior": False,
            "training": False,
            "hosted_training": False,
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
        "# Winner V146 DAgger direction feasibility\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Selected alpha: `{selected['alpha']}`.\n"
        f"- Worst preservation ratio: "
        f"`{selected['maximum_preservation_ratio']}`.\n"
        f"- Worst correction ratio: "
        f"`{selected['maximum_correction_ratio']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Exact CPU graph interpolation only; no training, behavior, "
        "Colab, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
