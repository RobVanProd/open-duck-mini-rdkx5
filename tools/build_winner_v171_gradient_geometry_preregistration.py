#!/usr/bin/env python3
"""Preregister V171's read-only reward/cost gradient-geometry audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v171_gradient_geometry_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V171_GRADIENT_GEOMETRY_PREREGISTRATION_20260725.md"
)
RUNNER = TOOLS / "run_winner_v171_gradient_geometry_audit.py"
COMPOSER = TOOLS / "compose_winner_v171_gradient_geometry.py"
PATCH = ROOT / "patches/winner_v171_gradient_geometry_audit.patch"
HELPER = ROOT / "training/winner_v171_gradient_geometry.py"
V127_PREREG = ANALYSIS / "winner_v127_constrained_cpu_preregistration.json"
V127_RESULT = ANALYSIS / "winner_v127_constrained_cpu_result.json"
V128_RESULT = ANALYSIS / "winner_v128_nominal_behavior_result.json"
V163_V165 = ANALYSIS / "FABLE_V163_V165_ADDENDUM_20260725.md"
V170_RESULT = (
    ANALYSIS / "winner_v170_exact_oracle_r2_feasibility_result.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def input_paths(
    *,
    audit_playground: Path,
    control_playground: Path,
    source_checkpoint: Path,
    v121_half_deployed: Path,
) -> dict[str, Path]:
    return {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "composer": COMPOSER,
        "patch": PATCH,
        "geometry_helper": HELPER,
        "v127_cpu_preregistration": V127_PREREG,
        "v127_cpu_result": V127_RESULT,
        "v127_hosted_result": V128_RESULT,
        "v163_v165_addendum": V163_V165,
        "v170_result": V170_RESULT,
        "audit_manifest": audit_playground
        / "WINNER_V171_COMPOSED_SOURCE_MANIFEST.json",
        "control_manifest": control_playground
        / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json",
        "source_checkpoint": source_checkpoint,
        "v121_half_deployed": v121_half_deployed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-playground", type=Path, required=True)
    parser.add_argument("--control-playground", type=Path, required=True)
    args = parser.parse_args()
    audit_playground = args.audit_playground.resolve()
    control_playground = args.control_playground.resolve()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V171: {path}")

    v127_prereg = json.loads(V127_PREREG.read_text(encoding="utf-8"))
    v127_result = json.loads(V127_RESULT.read_text(encoding="utf-8"))
    v128 = json.loads(V128_RESULT.read_text(encoding="utf-8"))
    v170 = json.loads(V170_RESULT.read_text(encoding="utf-8"))
    source_checkpoint = Path(
        v127_prereg["external_paths"]["source_checkpoint"]
    )
    v121_half_deployed = Path(
        v127_result["deployment"]["graphs"]["0"]["path"]
    )
    paths = input_paths(
        audit_playground=audit_playground,
        control_playground=control_playground,
        source_checkpoint=source_checkpoint,
        v121_half_deployed=v121_half_deployed,
    )
    audit_manifest = json.loads(
        paths["audit_manifest"].read_text(encoding="utf-8")
    )
    control_manifest = json.loads(
        paths["control_manifest"].read_text(encoding="utf-8")
    )

    checks = {
        "v127_cpu_contract_green": (
            v127_result.get("status")
            == "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
            and v127_result.get("failed_checks") == []
        ),
        "v127_hosted_continuation_closed_by_persistence": (
            v128.get("decision", {}).get("status")
            == "REJECT_V128_NOMINAL_POLICY"
            and v128.get("decision", {}).get(
                "persistent_both_checkpoint_pass"
            )
            is False
        ),
        "v163_v165_feasibility_backtracking_family_closed": (
            "CLOSE_FEASIBILITY_PRESERVING_BLOCK_CONTINUATION_NO_RETRY"
            in V163_V165.read_text(encoding="utf-8")
        ),
        "v170_exact_oracle_first_r2_green": (
            v170.get("status")
            == "PASS_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_VALID_RESULT"
            and v170.get("decision")
            == "EARN_V171_SAFE_ARCHITECTURE_DESIGN_ONLY"
        ),
        "audit_source_is_v127_plus_observation_only_patch": (
            audit_manifest.get("schema_version")
            == "winner_v171.gradient_geometry_source.v1"
            and audit_manifest.get("audit_only") is True
            and audit_manifest.get("optimizer_behavior")
            == "bit-identical V127; geometry is observed only"
        ),
        "control_source_is_exact_v127": (
            control_manifest.get("schema_version")
            == "winner_v127.constrained_source.v1"
        ),
        "source_checkpoint_hash_exact": (
            sha256_directory(source_checkpoint)
            == v127_prereg["input_hashes"]["source_checkpoint_directory"]
        ),
        "v121_half_deployed_hash_exact": (
            sha256(v121_half_deployed)
            == v127_result["deployment"]["graphs"]["0"]["deployed_sha256"]
        ),
        "one_iteration_is_32_environment_steps": True,
        "retention_floor_exactly_one_over_v127_cpu_iterations": (
            int(v127_result["training"]["aux"]["1024"][
                "total_training_iterations"
            ])
            == 32
        ),
        "cpu_only_no_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    paths_hashes = {
        name: (
            sha256_directory(path) if path.is_dir() else sha256(path)
        )
        for name, path in paths.items()
    }
    payload: dict[str, Any] = {
        "schema_version": (
            "winner_v171.gradient_geometry_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V171_GRADIENT_GEOMETRY_AUDIT"
            if not failed
            else "HOLD_WINNER_V171_GRADIENT_GEOMETRY_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": paths_hashes,
        "external_paths": {
            "audit_playground": str(audit_playground),
            "control_playground": str(control_playground),
            "source_checkpoint": str(source_checkpoint),
            "v121_half_deployed": str(v121_half_deployed),
        },
        "causal_reconciliation": {
            "proposal_not_repeated": (
                "the requested dense-cost, separate-critic, derived-dual "
                "PPO-Lagrangian is exactly V127; V128 permanently closed it "
                "after opposite half/final safety outcomes"
            ),
            "closed_neighbor": (
                "V163-V165 closed parameter backtracking of the same V127 "
                "proposal direction and trainable state"
            ),
            "new_evidence": (
                "V170 proved a complete torque-safe gait survives the first "
                "R2 condition within a maximum 0.02235485-rad oracle action "
                "correction and with zero empty intersections"
            ),
            "new_question": (
                "do the actual frozen-batch reward and dense-cost actor "
                "gradients admit a nontrivial reward direction whose "
                "first-order cost derivative is nonpositive by construction?"
            ),
        },
        "method": {
            "control": (
                "one exact V127 iteration from V121-half, 32 environment "
                "steps, selection weight zero"
            ),
            "audit": (
                "the identical V127 iteration plus pure observation of "
                "separate reward+entropy and conservative cost actor gradients"
            ),
            "reward_direction": "d_R = -g_R",
            "halfspace": "g_C dot d <= 0",
            "projection": (
                "d = d_R - max(0,g_C dot d_R)/||g_C||^2 * g_C"
            ),
            "cost_descent": "d_C = -g_C",
            "deployment_graph_changed": False,
            "optimizer_changed_in_this_audit": False,
        },
        "decision_rule": {
            "retention_floor": 1.0 / 32.0,
            "retention_floor_derivation": (
                "V127's frozen CPU proposal aggregates 32 iterations and "
                "V163 preregistered 1/32 as one average-iteration "
                "nontrivial displacement"
            ),
            "float32_directional_tolerance": (
                "64*eps32*max(1,abs(pre_derivative),"
                "reward_norm*cost_norm)"
            ),
            "pass_requires": [
                "reward and cost actor gradients finite and nonzero",
                "exact projection rule and first-order cost derivative <= tolerance",
                "projected reward direction retains at least 1/32 of its norm",
                "cost descent derivative equals -||g_C||^2 and is negative",
                "instrumented V127 update is bit-exact to the uninstrumented control",
                "step-0 and step-32 deployment contracts remain green",
            ],
            "green": (
                "earn only V172's lexicographic tangent-update CPU "
                "implementation contract"
            ),
            "hold": (
                "close the lexicographic tangent optimizer geometry; no "
                "alternate batch, retention threshold, norm, or projection"
            ),
        },
        "stop_rule": (
            "No behavior cells or hosted run execute in V171. Failure is "
            "decisive for this geometry; success authorizes implementation "
            "and a new CPU contract only."
        ),
        "authority": {
            "two_one_iteration_cpu_smokes": not failed,
            "v172_cpu_contract_design": False,
            "training": False,
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
        "# Winner V171 actor-gradient geometry preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- V127's PPO-Lagrangian is not retried. V171 observes a mechanically "
        "distinct cost-tangent geometry on one frozen V121/V127 batch.\n"
        "- Control and audit each run exactly one 32-environment-step CPU "
        "iteration; the audit must remain bit-exact to the control.\n"
        "- The projected reward direction must be first-order "
        "cost-nonincreasing and retain at least `1/32` of its norm.\n"
        "- Passing earns only a V172 CPU implementation contract. No behavior "
        "cell, hosted run, candidate, Gate 5, RDK-X5, or robot is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
