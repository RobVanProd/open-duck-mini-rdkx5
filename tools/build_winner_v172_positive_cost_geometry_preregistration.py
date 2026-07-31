#!/usr/bin/env python3
"""Preregister V172's first-positive-cost gradient-geometry audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS / "winner_v172_positive_cost_geometry_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V172_POSITIVE_COST_GEOMETRY_PREREGISTRATION_20260725.md"
)
RUNNER = TOOLS / "run_winner_v172_positive_cost_geometry.py"
COMPOSER = TOOLS / "compose_winner_v172_positive_cost_geometry.py"
PATCH = ROOT / "patches/winner_v172_positive_cost_capture.patch"
HELPER = ROOT / "training/winner_v171_gradient_geometry.py"
V127_PREREG = ANALYSIS / "winner_v127_constrained_cpu_preregistration.json"
V127_RESULT = ANALYSIS / "winner_v127_constrained_cpu_result.json"
V171_RESULT = ANALYSIS / "winner_v171_gradient_geometry_result.json"
V171A = ANALYSIS / "winner_v171a_zero_cost_sufficiency_correction.json"


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
    frozen_smoke: Path,
) -> dict[str, Path]:
    return {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "composer": COMPOSER,
        "capture_patch": PATCH,
        "v171_helper": HELPER,
        "v127_cpu_preregistration": V127_PREREG,
        "v127_cpu_result": V127_RESULT,
        "v171_result": V171_RESULT,
        "v171a_correction": V171A,
        "v172_manifest": playground
        / "WINNER_V172_COMPOSED_SOURCE_MANIFEST.json",
        "source_checkpoint": source_checkpoint,
        "frozen_smoke": frozen_smoke,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground.resolve()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V172: {path}")

    v127_prereg = json.loads(V127_PREREG.read_text(encoding="utf-8"))
    v127_result = json.loads(V127_RESULT.read_text(encoding="utf-8"))
    v171 = json.loads(V171_RESULT.read_text(encoding="utf-8"))
    v171a = json.loads(V171A.read_text(encoding="utf-8"))
    source_checkpoint = Path(
        v127_prereg["external_paths"]["source_checkpoint"]
    )
    frozen_smoke = (
        Path(v127_result["deployment"]["graphs"]["0"]["path"]).parent
        / "smoke"
    )
    paths = input_paths(
        playground=playground,
        source_checkpoint=source_checkpoint,
        frozen_smoke=frozen_smoke,
    )
    manifest = json.loads(
        paths["v172_manifest"].read_text(encoding="utf-8")
    )
    frozen_aux = v127_result["training"]["aux"]["1024"]
    checks = {
        "v127_cpu_schedule_green_and_first_positive_cost_present": (
            v127_result.get("status")
            == "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
            and v127_result.get("failed_checks") == []
            and frozen_aux.get("initialized") is True
            and float(frozen_aux.get("initial_cost")) > 0.0
            and frozen_aux.get("total_training_iterations") == 32
        ),
        "v171_stated_geometry_contract_green": (
            v171.get("status")
            == "PASS_WINNER_V171_GRADIENT_GEOMETRY_AUDIT"
            and v171.get("failed_checks") == []
        ),
        "v171a_withdraws_zero_cost_causal_promotion": (
            v171a.get("decision")
            == "HOLD_V171_CAUSAL_PROMOTION_REQUIRE_FIRST_POSITIVE_COST_BATCH"
        ),
        "v172_source_is_audit_only": (
            manifest.get("schema_version")
            == "winner_v172.positive_cost_geometry_source.v1"
            and manifest.get("audit_only") is True
            and manifest.get("optimizer_behavior")
            == "bit-identical V127; geometry is observed only"
            and manifest.get("capture_rule")
            == "first rollout batch with raw batch_cost > 0"
        ),
        "source_checkpoint_hash_exact": (
            sha256_directory(source_checkpoint)
            == v127_prereg["input_hashes"]["source_checkpoint_directory"]
        ),
        "frozen_v127_smoke_hash_exact": (
            sha256_directory(frozen_smoke)
            == v127_prereg["recovery"]["smoke_directory_sha256"]
        ),
        "retention_floor_exactly_one_over_32": True,
        "one_audit_run_only_no_control_rerun": True,
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
            "winner_v172.positive_cost_geometry_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V172_POSITIVE_COST_GEOMETRY"
            if not failed
            else "HOLD_WINNER_V172_POSITIVE_COST_GEOMETRY_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "external_paths": {
            "playground": str(playground),
            "source_checkpoint": str(source_checkpoint),
            "frozen_v127_smoke": str(frozen_smoke),
        },
        "correction_scope": {
            "defect": (
                "V171 captured a zero-realized-cost batch, so its cost "
                "gradient could be induced by the fresh cost-value baseline"
            ),
            "single_change": (
                "capture geometry only on the first rollout batch whose raw "
                "mean episode torque-exceedance cost is strictly positive"
            ),
            "unchanged": [
                "V127 rollout, policy update, cost critic, dual, RNG, and export",
                "V171 reward/cost objective definitions and tangent equation",
                "32-iteration 1024-step CPU schedule",
            ],
        },
        "method": {
            "run": "one 1024-step instrumented CPU smoke",
            "control": (
                "reuse the already hash-frozen V127 1024-step CPU smoke; no "
                "control rerun"
            ),
            "capture_condition": "raw batch_cost > 0, first occurrence only",
            "required_identity": (
                "step-0/1024 policy, normalizer, reward critic, cost critic, "
                "dual state, and raw ONNX are bit-exact to frozen V127"
            ),
        },
        "decision_rule": {
            "retention_floor": 1.0 / 32.0,
            "retention_floor_derivation": (
                "one average iteration of the frozen 32-iteration V127 CPU "
                "proposal, inherited unchanged from V163/V171"
            ),
            "pass_requires": [
                "a strictly positive raw-cost batch is captured",
                "captured cost equals V127's frozen first positive J_C0 exactly",
                "reward and cost actor gradients are finite and nonzero",
                "the tangent direction is first-order cost-nonincreasing",
                "the tangent direction retains at least 1/32 reward norm",
                "the cost-only direction has exact derivative -||g_C||^2",
                "all instrumented train/export artifacts are bit-exact to frozen V127",
            ],
            "green": (
                "earn V173 lexicographic tangent-update CPU implementation "
                "contract only"
            ),
            "hold": (
                "close this optimizer geometry without alternate capture "
                "batch, threshold, projection, retention floor, or rerun"
            ),
        },
        "authority": {
            "one_1024_step_cpu_audit": not failed,
            "v173_cpu_contract_design": False,
            "optimizer_implementation": False,
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
        "# Winner V172 first-positive-cost geometry preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Corrects V171's zero-realized-cost sufficiency gap by capturing "
        "only the first strictly positive raw-cost rollout batch.\n"
        "- Runs one 1,024-step instrumented CPU smoke and reuses the already "
        "frozen V127 smoke as its bit-exact control.\n"
        "- The tangent must remain first-order cost-nonincreasing and retain "
        "at least `1/32` of the reward direction.\n"
        "- Passing earns only V173 CPU implementation work. No hosted run, "
        "candidate, robustness matrix, Gate 5, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
