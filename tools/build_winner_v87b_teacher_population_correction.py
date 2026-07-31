#!/usr/bin/env python3
"""Freeze the pre-rollout Winner-v87 teacher-population correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v87_pitch_head_linear_feasibility.py"
PREREGISTRATION = ANALYSIS / "winner_v87_pitch_head_linear_feasibility_preregistration.json"
RESULT = ANALYSIS / "winner_v87_pitch_head_linear_feasibility_result.json"
OUTPUT = ANALYSIS / "winner_v87b_teacher_population_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V87B_TEACHER_POPULATION_CORRECTION_20260722.md"
PREREGISTRATION_SHA256 = "6253c0bfa8d8f47c8e941aecd6e68460ce43bd18c4ca243353a35616948de484"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def corrected_source() -> tuple[str, str, str]:
    source = RUNNER.read_text(encoding="utf-8")
    replacements = {
        'or frozen.get("teacher_configuration_count") != 16': (
            'or frozen.get("teacher_configuration_count") != 12'
        ),
        'or frozen.get("teacher_episodes_per_checkpoint") != 32': (
            'or frozen.get("teacher_episodes_per_checkpoint") != 24'
        ),
        'or fit.get("cross_validation_fits_per_checkpoint") != 16': (
            'or fit.get("cross_validation_fits_per_checkpoint") != 12'
        ),
        'or int(np.count_nonzero(selected_environment)) != 32': (
            'or int(np.count_nonzero(selected_environment)) != 24'
        ),
        "preregistration = json.loads(PREREGISTRATION.read_text(encoding=\"utf-8\"))": (
            "preregistration = json.loads(PREREGISTRATION.read_text(encoding=\"utf-8\"))\n"
            "    preregistration[\"frozen_source\"][\"teacher_configuration_count\"] = 12\n"
            "    preregistration[\"frozen_source\"][\"teacher_episodes_per_checkpoint\"] = 24\n"
            "    preregistration[\"fit\"][\"cross_validation_fits_per_checkpoint\"] = 12"
        ),
        "if len(teacher_ids) != 16 or any(name not in teacher_table for name in teacher_ids):": (
            "if len(teacher_ids) != 12 or any(name not in teacher_table for name in teacher_ids):"
        ),
        'row["teacher_episodes"] == 32': 'row["teacher_episodes"] == 24',
        'and len(row["teacher_configuration_ids"]) == 16': (
            'and len(row["teacher_configuration_ids"]) == 12'
        ),
        '"least_squares_fits": 34': '"least_squares_fits": 26',
    }
    corrected = source
    for old, new in replacements.items():
        if corrected.count(old) != 1:
            raise ValueError(f"Winner-v87b correction target changed: {old}")
        corrected = corrected.replace(old, new)
    compile(corrected, "winner_v87b_corrected.py", "exec")
    return (
        corrected,
        hashlib.sha256(source.replace("\r\n", "\n").encode()).hexdigest(),
        hashlib.sha256(corrected.replace("\r\n", "\n").encode()).hexdigest(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v87b correction: {path}")
    corrected, original_hash, corrected_hash = corrected_source()
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        sha256(PREREGISTRATION) != PREREGISTRATION_SHA256
        or preregistration.get("frozen_source", {}).get("teacher_configuration_count")
        != 16
        or preregistration.get("frozen_source", {}).get(
            "teacher_episodes_per_checkpoint"
        )
        != 32
        or RESULT.exists()
    ):
        raise ValueError("Winner-v87b pre-rollout boundary changed")
    source_paths = {
        "correction_builder": Path(
            "tools/build_winner_v87b_teacher_population_correction.py"
        ),
        "correction_runner": Path(
            "tools/run_winner_v87b_teacher_population_correction.py"
        ),
        "correction_tests": Path(
            "tests/test_winner_v87b_teacher_population_correction.py"
        ),
        "v87_runner": RUNNER.relative_to(ROOT),
        "v87_preregistration": PREREGISTRATION.relative_to(ROOT),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v87b.teacher_population_correction.v1",
        "status": "CORRECTED_WINNER_V87_TEACHER_POPULATION_PRE_ROLLOUT",
        "decision": "RERUN_EXACT_V87_AUDIT_ON_TWELVE_SELECTED_TEACHER_CONFIGURATIONS",
        "failure": {
            "stage": "teacher table validation before stage2_rollout",
            "exception": "ValueError: Winner-v87 teacher table changed",
            "stage2_rollout_episodes": 0,
            "least_squares_fits": 0,
            "optimizer_updates": 0,
            "result_written": False,
        },
        "correction": {
            "complete_teacher_table_entries_unchanged": 16,
            "selected_training_teacher_configurations": {"old": 16, "new": 12},
            "selected_teacher_episodes_per_checkpoint": {"old": 32, "new": 24},
            "leave_one_configuration_out_fits_per_checkpoint": {"old": 16, "new": 12},
            "total_least_squares_fits": {"old": 34, "new": 26},
            "reason": (
                "complete_teacher_table contains four entries not selected by the "
                "V80/V84 training objective; the diagnostic must use the exact 12-ID "
                "TRAINING_TEACHER_IDS population, each represented on two plants"
            ),
            "fit_solver_features_targets_thresholds_checkpoints_authority_unchanged": True,
            "original_runner_lf_sha256": original_hash,
            "corrected_runner_lf_sha256": corrected_hash,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": preregistration["authority"],
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v87b teacher-population correction",
                "",
                "- Failed before first rollout or fit: `yes`",
                "- Complete table entries: `16` (unchanged)",
                "- Selected training configurations: `16 -> 12`",
                "- Selected plant episodes per endpoint: `32 -> 24`",
                "- Leave-one-configuration-out folds per endpoint: `16 -> 12`",
                "- Solver / targets / thresholds / checkpoints / authority changed: `no`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
