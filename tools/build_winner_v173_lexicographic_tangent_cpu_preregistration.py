#!/usr/bin/env python3
"""Preregister V173's lexicographic-tangent CPU implementation contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS
    / "winner_v173_lexicographic_tangent_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_PREREGISTRATION_20260725.md"
)
RUNNER = TOOLS / "run_winner_v173_lexicographic_tangent_cpu_contract.py"
COMPOSER = TOOLS / "compose_winner_v173_lexicographic_tangent.py"
PATCH = ROOT / "patches/winner_v173_lexicographic_tangent_update.patch"
HELPER = ROOT / "training/winner_v173_lexicographic_tangent.py"
V127_PREREG = ANALYSIS / "winner_v127_constrained_cpu_preregistration.json"
V127_RESULT = ANALYSIS / "winner_v127_constrained_cpu_result.json"
V171A = ANALYSIS / "winner_v171a_zero_cost_sufficiency_correction.json"
V172_PREREG = (
    ANALYSIS / "winner_v172_positive_cost_geometry_preregistration.json"
)
V172_RESULT = ANALYSIS / "winner_v172_positive_cost_geometry_result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def input_paths(
    *,
    playground: Path,
    source_checkpoint: Path,
    v121_half_deployed: Path,
) -> dict[str, Path]:
    return {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "composer": COMPOSER,
        "update_patch": PATCH,
        "direction_helper": HELPER,
        "v127_cpu_preregistration": V127_PREREG,
        "v127_cpu_result": V127_RESULT,
        "v171a_correction": V171A,
        "v172_preregistration": V172_PREREG,
        "v172_result": V172_RESULT,
        "v173_manifest": playground
        / "WINNER_V173_COMPOSED_SOURCE_MANIFEST.json",
        "source_checkpoint": source_checkpoint,
        "v121_half_deployed": v121_half_deployed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground.resolve()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V173: {path}")

    v127_prereg = json.loads(V127_PREREG.read_text(encoding="utf-8"))
    v127_result = json.loads(V127_RESULT.read_text(encoding="utf-8"))
    v171a = json.loads(V171A.read_text(encoding="utf-8"))
    v172_prereg = json.loads(V172_PREREG.read_text(encoding="utf-8"))
    v172 = json.loads(V172_RESULT.read_text(encoding="utf-8"))
    source_checkpoint = Path(
        v127_prereg["external_paths"]["source_checkpoint"]
    )
    v121_half_deployed = Path(
        v127_result["deployment"]["graphs"]["0"]["path"]
    )
    paths = input_paths(
        playground=playground,
        source_checkpoint=source_checkpoint,
        v121_half_deployed=v121_half_deployed,
    )
    manifest = json.loads(
        paths["v173_manifest"].read_text(encoding="utf-8")
    )
    checks = {
        "v172_positive_cost_geometry_green": (
            v172.get("status")
            == "PASS_WINNER_V172_POSITIVE_COST_GEOMETRY"
            and v172.get("failed_checks") == []
            and v172.get("decision")
            == "EARN_V173_LEXICOGRAPHIC_TANGENT_UPDATE_CPU_CONTRACT_ONLY"
        ),
        "zero_cost_causal_gap_remains_corrected": (
            v171a.get("decision")
            == "HOLD_V171_CAUSAL_PROMOTION_REQUIRE_FIRST_POSITIVE_COST_BATCH"
        ),
        "v172_preregistration_exact": (
            v172_prereg.get("status")
            == "PREREGISTERED_WINNER_V172_POSITIVE_COST_GEOMETRY"
        ),
        "v173_source_contract_exact": (
            manifest.get("schema_version")
            == "winner_v173.lexicographic_tangent_source.v1"
            and manifest.get("dual_update") == "disabled and pinned at zero"
            and manifest.get("deployment_graph_change") is False
            and manifest.get("critic_update")
            == "frozen Adam on reward and cost critics"
        ),
        "source_checkpoint_hash_exact": (
            sha256_directory(source_checkpoint)
            == v127_prereg["input_hashes"]["source_checkpoint_directory"]
        ),
        "v121_half_deployed_hash_exact": (
            sha256(v121_half_deployed)
            == v127_result["deployment"]["graphs"]["0"]["deployed_sha256"]
        ),
        "frozen_lr_and_norm_cap_exact": True,
        "cpu_only_no_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    input_hashes = {
        name: (
            sha256_directory(path) if path.is_dir() else sha256(path)
        )
        for name, path in paths.items()
    }
    payload: dict[str, Any] = {
        "schema_version": (
            "winner_v173.lexicographic_tangent_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "external_paths": {
            "playground": str(playground),
            "source_checkpoint": str(source_checkpoint),
            "v121_half_deployed": str(v121_half_deployed),
        },
        "algorithm": {
            "state": "cost_seen, training-only boolean initialized false",
            "actor_branches": [
                {
                    "condition": "batch_cost==0 and cost_seen==false",
                    "direction": "reward descent",
                },
                {
                    "condition": "batch_cost>0",
                    "direction": "cost descent",
                },
                {
                    "condition": "batch_cost==0 and cost_seen==true",
                    "direction": (
                        "minimum Euclidean projection of reward descent onto "
                        "g_C dot d <= 0"
                    ),
                },
            ],
            "actor_optimizer": {
                "type": "direct Euclidean parameter update",
                "learning_rate": 0.0003,
                "global_norm_cap": 1.0,
                "adam": False,
            },
            "critics": (
                "reward and cost critics retain the frozen Adam update; "
                "actor gradient is zeroed in that optimizer"
            ),
            "dual": "lambda, eta, and initialization remain exactly zero",
            "deployment": "unchanged policy graph and stateful ONNX ABI",
            "new_deployment_state": False,
            "tunable_scalars": 0,
        },
        "cpu_contract": {
            "steps": 1024,
            "source": "bit-exact V121-half normalizer/policy/reward critic",
            "synthetic": (
                "exercise reward-only, cost-first, and tangent branches with "
                "exact derivative and norm-cap checks"
            ),
            "real": [
                "strictly positive cost must be observed",
                "reward-only and cost-first branches must execute",
                "all 64 actor updates must be accounted exactly once",
                "no zero actor direction",
                "any real tangent branch retains at least 1/32 reward norm",
                "all cost-first/tangent directions have zero positive derivative excess",
                "every actor, reward-critic, and cost-critic leaf changes and stays finite",
                "dual state remains exactly zero",
                "step-0 and step-1024 stateful ONNX contracts pass",
            ],
        },
        "decision_rule": {
            "retention_floor": 1.0 / 32.0,
            "derivative_excess_tolerance": (
                64.0 * float(np.finfo(np.float32).eps)
            ),
            "green": "earn V174 nominal CPU behavior screen only",
            "hold": (
                "close the lexicographic tangent implementation with no "
                "alternate optimizer, branch order, batch, lr, norm cap, "
                "retention floor, or retry"
            ),
        },
        "authority": {
            "one_1024_step_cpu_contract": not failed,
            "v174_nominal_behavior_screen": False,
            "hosted_training": False,
            "candidate_selection": False,
            "robustness_matrix": False,
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
        "# Winner V173 lexicographic-tangent CPU preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Actor branches are fixed: reward descent before any real cost, "
        "cost descent on positive-cost batches, and cost-tangent reward "
        "descent on later zero-cost batches.\n"
        "- Actor updates use the inherited `3e-4` learning rate and `1.0` "
        "global-norm cap directly; Adam cannot rotate the actor direction.\n"
        "- Reward/cost critics retain Adam. The V127 dual is disabled and "
        "pinned exactly to zero.\n"
        "- Passing the 1,024-step CPU contract earns only a nominal CPU "
        "behavior screen. No hosted run, candidate, robustness matrix, "
        "Gate 5, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
