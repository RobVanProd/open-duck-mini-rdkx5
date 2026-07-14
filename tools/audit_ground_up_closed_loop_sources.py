#!/usr/bin/env python3
"""Audit eligible closed-loop corrective sources for the ground-up search."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ALGORITHMIC_PATTERNS = (
    "closed_loop_weight_transfer_teacher*_score_150.json",
    "com_weight_transfer_controller*_score_150.json",
    "foot_placement_mpc_teacher*_score_150.json",
    "staged_weight_transfer_planner_score_150.json",
    "support_loaded_weight_transfer_probe_score_150.json",
    "support_state_weight_transfer_probe_score_150.json",
    "contact_weight_transfer_sequence_optimizer.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", type=Path, default=Path("outputs/analysis"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = []
    seen = set()
    for pattern in ALGORITHMIC_PATTERNS:
        for path in sorted(args.analysis_dir.glob(pattern)):
            if path in seen:
                continue
            seen.add(path)
            payload = json.loads(path.read_text())
            rows.append({
                "path": str(path),
                "sha256": sha256(path),
                "status": payload.get("status"),
                "eligible": True,
                "source_class": "algorithmic_closed_loop",
            })

    unexpected = [row for row in rows if row["status"] not in {
        "HOLD_NO_SEED_ROBUST_TARGETS",
        "HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET",
    }]
    if unexpected:
        raise AssertionError(f"unexpected algorithmic source result: {unexpected}")

    exact_result = args.analysis_dir / "ground_up_exact_command_reference_result.json"
    exact = json.loads(exact_result.read_text())
    reference_row = {
        "path": str(exact_result),
        "sha256": sha256(exact_result),
        "status": exact["status"],
        "eligible": False,
        "source_class": "open_loop_reference",
        "reason": "fails direct CPU behavior gate",
    }
    baseline = Path("policy/BEST_WALK_ONNX_2.onnx")
    baseline_row = {
        "path": str(baseline),
        "sha256": sha256(baseline),
        "status": "HAS_PERSISTENT_CLOSED_LOOP_PROPULSION_EVIDENCE",
        "eligible": False,
        "source_class": "existing_learned_policy",
        "reason": "frozen comparator; teacher and warm-start use are prohibited",
    }
    dagger = args.analysis_dir / "phase2_rate_bounded_teacher_x008_full8_15s.json"
    dagger_row = None
    if dagger.is_file():
        payload = json.loads(dagger.read_text())
        dagger_row = {
            "path": str(dagger),
            "sha256": sha256(dagger),
            "status": payload.get("status"),
            "eligible": False,
            "source_class": "existing_learned_dagger_policy",
            "reason": "depends on an existing learned-policy/DAgger lineage",
        }

    result = {
        "schema_version": "ground_up_closed_loop_source_audit.v1",
        "status": "NO_ELIGIBLE_VALIDATED_CORRECTIVE_SOURCE",
        "algorithmic_source_results": rows,
        "algorithmic_source_count": len(rows),
        "algorithmic_pass_count": 0,
        "reference_source": reference_row,
        "baseline_source": baseline_row,
        "dagger_source": dagger_row,
        "constraints": {
            "existing_policy_teacher": False,
            "existing_policy_warm_start": False,
            "dagger_teacher": False,
            "robot_access": False,
            "local_gpu_access": False,
        },
        "selected_untried_source_probe": (
            "oracle-dynamics receding-horizon shooting controller with explicit "
            "forward-displacement, stability, lateral, action, and rate objectives"
        ),
        "selection_reason": (
            "It is closed-loop and ground-up, directly addresses the documented "
            "missing propulsion objective, and is materially different from the "
            "failed hand-authored weight-transfer and foot-placement families."
        ),
        "authorization": "CPU_CONTRACT_AND_SOURCE_PROBE_ONLY",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": result["status"],
        "algorithmic_source_count": len(rows),
        "algorithmic_pass_count": 0,
        "selected_untried_source_probe": result["selected_untried_source_probe"],
    }, indent=2))


if __name__ == "__main__":
    main()
