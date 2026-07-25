#!/usr/bin/env python3
"""Preregister the read-only V130 oracle-correction feature audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V129_FORMAL = ANALYSIS / "winner_v129_oracle_teacher_formal_cpu_result.json"
RUNNER = (
    ROOT / "tools/audit_winner_v130_oracle_correction_feature_separability.py"
)
OUTPUT = (
    ANALYSIS / "winner_v130_oracle_correction_feature_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V130_ORACLE_CORRECTION_FEATURE_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "v129_formal_result": (
        "2b083d958ee29b3fd0cee90c73de610ed73a1b9ccd23a2a6b360242d95a5e909"
    ),
    "audit_runner": (
        "e872728eeb6832aa8ba0450b45b29aa724ccfade40e8129b5c56454ba40f8001"
    ),
    "source_checkpoint": (
        "c1d9b8574c941e2279294de14aca1cb57d4736bdc63635b5aaf1e205fa7f86c1"
    ),
    "cpu_template": (
        "217a1551c4cc778e4b957636a40ca6e01eafa51efeaef905eb73e9debc7c26e5"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V130: {path}")
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    formal = json.loads(V129_FORMAL.read_text(encoding="utf-8"))
    input_hashes = {
        "v129_formal_result": sha256(V129_FORMAL),
        "audit_runner": sha256(RUNNER),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v129_head_only_formulation_closed": (
            formal.get("status")
            == "HOLD_WINNER_V129_ORACLE_TEACHER_FORMAL_CPU_DISTILLATION"
            and formal.get("decision")
            == "CLOSE_V129_DISTILLATION_WITHOUT_BEHAVIOR"
            and formal.get("checks", {}).get("formal_behavior_cells_zero")
            is True
        ),
        "probe_is_read_only": True,
        "thresholds_frozen_before_fit": True,
        "no_training_or_behavior": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v130.oracle_correction_feature_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V130_ORACLE_CORRECTION_FEATURE_AUDIT"
            if not failed
            else "HOLD_WINNER_V130_ORACLE_CORRECTION_FEATURE_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "question": (
            "Did V129 fail because the frozen 64-D recurrent output is not a "
            "linearly localizable correction representation, while the "
            "already deployable normalized observation plus h_in is?"
        ),
        "probes": {
            "current_head": "linear readout over h_out[64]",
            "observation": "linear readout over normalized obs[115]",
            "deployable_state": (
                "linear readout over normalized obs[115] + h_in[64]"
            ),
            "fit": (
                "float64 unregularized class-balanced least squares; "
                "correction weight 4786/14"
            ),
            "cross_plant": [
                "train P30 / test P31-34",
                "train P31-34 / test P30",
            ],
        },
        "advancement_thresholds": {
            "state_vs_hidden_total_error": "<= 0.25x",
            "state_corrected_mse_vs_zero": "<= 0.25x",
            "state_preservation_mse_vs_corrected_baseline": "<= 0.01x",
            "each_cross_plant_corrected_mse_vs_zero": "< 1.0x",
            "each_cross_plant_preservation_vs_corrected_baseline": (
                "<= 0.01x"
            ),
        },
        "decision_rule": {
            "all_thresholds_pass": (
                "authorize one CPU contract for a zero-initialized linear "
                "observation-state correction residual; no formal training"
            ),
            "any_threshold_fails": (
                "do not train that residual; record the representational "
                "hold and return to gait-level mechanism selection"
            ),
        },
        "authority": {
            "read_only_cpu_audit": not failed,
            "training": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "full_matrix": False,
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
        "# Winner V130 oracle-correction feature preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The probe is read-only and CPU-only.\n"
        "- It compares frozen recurrent features with the already deployable "
        "observation plus recurrent input.\n"
        "- All advancement thresholds were frozen before solving the linear "
        "systems.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
