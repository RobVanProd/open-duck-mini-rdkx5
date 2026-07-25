#!/usr/bin/env python3
"""Preregister V146's zero-training DAgger direction feasibility audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/audit_winner_v146_dagger_direction_feasibility.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V145_RESULT = ANALYSIS / "winner_v145_on_policy_dagger_cpu_result.json"
V134_LOADER = (
    ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
)
V145_LOADER = ROOT / "training/winner_v145_on_policy_dagger.py"
OUTPUT = ANALYSIS / "winner_v146_dagger_direction_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V146_DAGGER_DIRECTION_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "f059ae7c256b2938c1cfce1716d239cebb8d1394ad2b4eb9feb74d8292a034f7"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v145_result": (
        "d1b9ee041130fd50b8be357749f2c8cdf38a884b8bde527eabfb19c80a3b14a8"
    ),
    "v134_loader": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
    ),
    "v145_loader": (
        "b6f0cb28e86bc3561009af87ad5cc5136641e08057d54c81d74b119d627ded4c"
    ),
    "source_raw": (
        "aa1025ae4bd2daf1c513cd81374e8eb7961308a41ca10bbe55f6284944fd6460"
    ),
    "candidate_raw": (
        "229564750101b99e215c159c640d2af457d4acd5b2d7a993346e02b83d0a6c5b"
    ),
    "shadow_trace": (
        "eb432bdb64c251dcbb466bd795db381891837086dae9dcc7a2564a7f2a2930b5"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shadow-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V146: {path}")
    shadow_trace = args.shadow_trace.resolve()
    v145 = json.loads(V145_RESULT.read_text(encoding="utf-8"))
    source_raw = Path(v145["exports"]["0"]["raw_path"])
    candidate_raw = Path(v145["exports"]["2"]["raw_path"])
    input_hashes = {
        "runner": sha256(RUNNER),
        "v121_transform": sha256(V121_TRANSFORM),
        "v145_result": sha256(V145_RESULT),
        "v134_loader": sha256(V134_LOADER),
        "v145_loader": sha256(V145_LOADER),
        "source_raw": sha256(source_raw),
        "candidate_raw": sha256(candidate_raw),
        "shadow_trace": sha256(shadow_trace),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v145_closed_only_on_shadow_preservation": (
            v145.get("failed_checks")
            == ["shadow_preservation_ratio_at_most_point01"]
        ),
        "source_and_candidate_exports_exist": (
            source_raw.is_file() and candidate_raw.is_file()
        ),
        "selection_uses_only_preservation": True,
        "fixed_twenty_step_bisection": True,
        "training_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v146.dagger_direction_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V146_DAGGER_DIRECTION_FEASIBILITY"
            if not failed
            else "HOLD_WINNER_V146_DAGGER_DIRECTION_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "question": (
            "Does any point on the already-computed V140-to-V145 actor "
            "direction satisfy both the frozen 1% preservation and 5% "
            "correction-improvement rules on overall, teacher, and shadow "
            "subsets?"
        ),
        "method": {
            "path": "exact ONNX initializer interpolation",
            "selection": (
                "largest alpha satisfying all three preservation ratios "
                "<=0.01"
            ),
            "bisection_steps": 20,
            "correction_selection_weight": 0,
            "optimizer_or_training": False,
        },
        "pass_rule": {
            "preservation": (
                "overall, teacher, and shadow ratios all <=0.01"
            ),
            "correction": (
                "overall, teacher, and shadow ratios all <=0.95"
            ),
            "export": "selected stateful ONNX contract passes",
        },
        "stop_rule": (
            "if the preservation-selected point misses any correction "
            "gate, close the entire global V145 direction; do not adjust "
            "alpha using correction outcomes and do not run behavior"
        ),
        "authority": {
            "cpu_graph_audit": not failed,
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
        "# Winner V146 DAgger direction preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Exact graph interpolation; alpha selected only by preservation.\n"
        "- No training, behavior, Colab, policy deployment, or hardware "
        "authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
