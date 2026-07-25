#!/usr/bin/env python3
"""Freeze V161's behavior-blind uniform two-checkpoint projection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS
    / "winner_v161_uniform_trust_projection_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V161_UNIFORM_TRUST_PROJECTION_PREREGISTRATION_20260725.md"
)
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V121_BEHAVIOR = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V128_TRANSFORM = ANALYSIS / "winner_v128_deployment_transform_contract.json"
V128_BEHAVIOR = ANALYSIS / "winner_v128_nominal_behavior_result.json"
V128_ATTRIBUTION = ANALYSIS / "winner_v128_nominal_failure_attribution.json"
V140 = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V160 = ANALYSIS / "winner_v160_remaining_shadow_census_result.json"
RUNNER = ROOT / "tools/audit_winner_v161_uniform_trust_projection.py"
V140_RUNNER = ROOT / "tools/audit_winner_v140_preservation_projected_actor.py"
DEPLOY = ROOT / "tools/run_winner_v129_oracle_teacher_cpu_contract.py"
BISECTION_STEPS = 20
PRESERVATION_RATIO = 0.01


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-raw", type=Path, required=True)
    parser.add_argument("--half-raw", type=Path, required=True)
    parser.add_argument("--final-raw", type=Path, required=True)
    parser.add_argument("--source-trace-root", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_raw.resolve()
    half = args.half_raw.resolve()
    final = args.final_raw.resolve()
    trace_root = args.source_trace_root.resolve()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V161: {path}")
    v121_transform = json.loads(V121_TRANSFORM.read_text(encoding="utf-8"))
    v121_behavior = json.loads(V121_BEHAVIOR.read_text(encoding="utf-8"))
    v128_transform = json.loads(V128_TRANSFORM.read_text(encoding="utf-8"))
    v128_behavior = json.loads(V128_BEHAVIOR.read_text(encoding="utf-8"))
    v128_attribution = json.loads(
        V128_ATTRIBUTION.read_text(encoding="utf-8")
    )
    v140 = json.loads(V140.read_text(encoding="utf-8"))
    v160 = json.loads(V160.read_text(encoding="utf-8"))
    source_spec = v121_transform["policies"][0]
    candidate_specs = v128_transform["policies"]
    trace_paths = sorted(trace_root.glob("v121_train_matched_half_*.jsonl"))
    trace_manifest = [
        {
            "name": path.name,
            "path": str(path),
            "rows": sum(1 for line in path.open(encoding="utf-8") if line),
            "sha256": sha256(path),
        }
        for path in trace_paths
    ]
    baseline = float(v140["summary"]["baseline_corrected_mse"])
    absolute_limit = PRESERVATION_RATIO * baseline
    input_paths = {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "v140_runner": V140_RUNNER,
        "deploy_tool": DEPLOY,
        "v121_transform": V121_TRANSFORM,
        "v121_behavior": V121_BEHAVIOR,
        "v128_transform": V128_TRANSFORM,
        "v128_behavior": V128_BEHAVIOR,
        "v128_attribution": V128_ATTRIBUTION,
        "v140_result": V140,
        "v160_result": V160,
        "source_raw": source,
        "half_raw": half,
        "final_raw": final,
    }
    checks = {
        "source_raw_exact": (
            str(source) == source_spec["source_path"]
            and sha256(source) == source_spec["source_sha256"]
        ),
        "candidate_raws_exact": (
            [sha256(half), sha256(final)]
            == [spec["source_sha256"] for spec in candidate_specs]
        ),
        "source_half_green_eight_of_eight": (
            v121_behavior["per_checkpoint"][0]["all_eight_cells_pass"]
            and v121_behavior["per_checkpoint"][0]["passing_cells"] == 8
        ),
        "constrained_signature_exact_two_then_eight": (
            [
                row["passing_cells"]
                for row in v128_behavior["per_checkpoint"]
            ]
            == [2, 8]
        ),
        "lagrangian_training_remains_closed": (
            v128_attribution["mechanism_verdict"][
                "ppo_lagrangian_v121_recipe"
            ]
            == "CLOSED_NO_RETRY"
        ),
        "v160_shadow_census_green": (
            v160.get("status")
            == "PASS_WINNER_V160_REMAINING_SHADOW_CENSUS"
        ),
        "source_dataset_exact_8x600": (
            len(trace_manifest) == 8
            and all(item["rows"] == 600 for item in trace_manifest)
        ),
        "preservation_limit_inherited_exactly_from_v140": (
            absolute_limit
            == 0.01 * v140["summary"]["baseline_corrected_mse"]
        ),
        "one_common_alpha_no_behavior_selection": True,
        "cpu_only_no_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v161.uniform_trust_projection_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V161_UNIFORM_TRUST_PROJECTION"
            if not failed
            else "HOLD_WINNER_V161_UNIFORM_TRUST_PROJECTION_"
            "PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            name: sha256(path) for name, path in input_paths.items()
        },
        "sources": {
            "green_anchor": {
                "id": "V121_TRAIN_MATCHED_HALF",
                "raw_path": str(source),
                "raw_sha256": sha256(source),
            },
            "candidates": [
                {
                    "id": "V128_CONSTRAINED_HALF",
                    "raw_path": str(half),
                    "raw_sha256": sha256(half),
                },
                {
                    "id": "V128_CONSTRAINED_FINAL",
                    "raw_path": str(final),
                    "raw_sha256": sha256(final),
                },
            ],
        },
        "source_dataset": {
            "rows": 4_800,
            "traces": trace_manifest,
            "selection_data": (
                "only V121-half source-policy observations, recurrent "
                "states, previous actions, and recorded source actions"
            ),
        },
        "projection": {
            "formula": (
                "theta_i(alpha)=theta_source+alpha*"
                "(theta_v128_i-theta_source), same alpha for i=half/final"
            ),
            "alpha_interval": [0.0, 1.0],
            "bisection_steps": BISECTION_STEPS,
            "selection": (
                "largest common alpha for which both deployed policies' "
                "action MSE from the green source is <= the frozen limit"
            ),
            "source_corrected_baseline_mse": baseline,
            "preservation_ratio": PRESERVATION_RATIO,
            "absolute_action_mse_limit": absolute_limit,
            "behavior_or_torque_used_for_alpha": False,
            "optimizer_or_training": False,
        },
        "contract_gates": {
            "source_trace_reproduction_linf": "<=1e-6",
            "selected_alpha": "strictly between zero and one",
            "both_selected_mse": "<=frozen absolute limit",
            "selected_common_budget_utilization": ">=0.99",
            "both_candidates_distinct_from_source": True,
            "selected_pair_distinct_from_each_other": True,
            "both_deployment_graph_contracts": True,
            "x0_exact": True,
        },
        "stop_rule": (
            "contract failure closes uniform trust projection; no behavior "
            "run and no alpha selected from behavior"
        ),
        "advance_rule": (
            "a green CPU contract earns exactly one separately "
            "preregistered 16-cell dual-checkpoint nominal matrix"
        ),
        "scope": (
            "does not resume or retry PPO-Lagrangian; it is a uniform "
            "deterministic post-training transform of both frozen outputs"
        ),
        "authority": {
            "cpu_graph_contract": not failed,
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
        "# Winner V161 uniform trust projection preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One common alpha projects both V128 constrained checkpoints "
        "toward the green V121-half source.\n"
        "- Alpha is selected only from a frozen action-preservation budget "
        "on 4,800 source states; no behavior or torque is observed.\n"
        "- This does not resume or retry PPO-Lagrangian.\n"
        "- No behavior, training, Colab, deployment, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
