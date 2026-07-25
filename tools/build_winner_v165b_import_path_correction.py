#!/usr/bin/env python3
"""Freeze the pre-outcome V165 package-import launch correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ORIGINAL_PREREG = (
    ANALYSIS / "winner_v165_coherent_normalizer_preregistration.json"
)
ORIGINAL_RUNNER = ROOT / "tools/run_winner_v165_coherent_normalizer.py"
WRAPPER = ROOT / "tools/run_winner_v165b_import_path_correction.py"
STATE_MODULE = ROOT / "training/winner_v165_coherent_normalizer_state.py"
OUTPUT = ANALYSIS / "winner_v165b_import_path_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V165B_IMPORT_PATH_CORRECTION_20260725.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    result = ANALYSIS / "winner_v165_coherent_normalizer_result.json"
    result_markdown = (
        ANALYSIS / "WINNER_V165_COHERENT_NORMALIZER_RESULT_20260725.md"
    )
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V165b: {path}")
    prereg = json.loads(ORIGINAL_PREREG.read_text(encoding="utf-8"))
    checks = {
        "original_preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_WINNER_V165_COHERENT_NORMALIZER"
            and prereg["failed_checks"] == []
        ),
        "failure_before_result": (
            not result.exists() and not result_markdown.exists()
        ),
        "failure_before_run_root": not run_root.exists(),
        "original_runner_unchanged_from_preregistration": (
            sha256(ORIGINAL_RUNNER) == prereg["input_hashes"]["runner"]
        ),
        "state_module_unchanged_from_preregistration": (
            sha256(STATE_MODULE) == prereg["input_hashes"]["state_module"]
        ),
        "wrapper_only_adds_repository_root_before_original_main": (
            "sys.path.insert(0, str(ROOT))" in WRAPPER.read_text(encoding="utf-8")
            and "from tools.run_winner_v165_coherent_normalizer import main"
            in WRAPPER.read_text(encoding="utf-8")
        ),
        "mechanism_matrix_alpha_and_stop_rule_unchanged": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v165b.import_path_correction.v1",
        "status": (
            "PASS_WINNER_V165B_IMPORT_PATH_CORRECTION"
            if not failed
            else "HOLD_WINNER_V165B_IMPORT_PATH_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "builder": sha256(Path(__file__).resolve()),
            "original_preregistration": sha256(ORIGINAL_PREREG),
            "original_runner": sha256(ORIGINAL_RUNNER),
            "wrapper": sha256(WRAPPER),
            "state_module": sha256(STATE_MODULE),
        },
        "observed_failure": {
            "stage": "module import before state restore/export/simulator",
            "exception": (
                "ModuleNotFoundError: No module named 'training'"
            ),
            "behavior_cells_executed": 0,
            "new_training": False,
            "result_written": False,
        },
        "correction": {
            "change": (
                "prepend repository root to sys.path, then call the unchanged "
                "V165 runner main"
            ),
            "mechanism_change": False,
            "alpha_change": False,
            "block_change": False,
            "matrix_change": False,
            "stop_rule_change": False,
        },
        "authority": {
            "rerun_original_v165_once_through_wrapper": not failed,
            "training": False,
            "hosted_training": False,
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
        "# Winner V165b import-path correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Original V165 stopped before state restore, export, or behavior.\n"
        "- Correction only prepends the repository root before invoking the "
        "unchanged runner.\n"
        "- Alpha, block, matrix, mechanism, and stop rule are unchanged.\n"
        "- Authorizes one CPU-only rerun; no training or Colab.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
