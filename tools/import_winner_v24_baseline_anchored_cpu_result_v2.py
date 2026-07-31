#!/usr/bin/env python3
"""Apply the frozen key-inventory correction, then run the strict importer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FROZEN_IMPORTER = ROOT / "tools/import_winner_v24_baseline_anchored_cpu_result.py"
CORRECTION = ROOT / "outputs/analysis/winner_v24_baseline_importer_correction.json"
CORRECTION_LF_SHA256 = "43d72f94defc642e9b9e4a47a6bc9079153da2e606420d184ffa0537f03615b7"
FROZEN_IMPORTER_LF_SHA256 = "3a96bc18d1d1e7834da934166a7883e84a22c6a99664be3c86a03841ede18cb0"
CORRECTED_GRADIENT_KEYS = {
    "action_bias",
    "action_weight",
    "auxiliary_action_weight",
    "auxiliary_bias",
    "auxiliary_hidden_weight",
    "hidden_bias",
    "hidden_weight",
    "obs_weight",
    "previous_action_weight",
    "training_only_log_std",
    "training_only_value_bias",
    "training_only_value_weight",
}
CORRECTED_RECURRENT_KEYS = {
    "hidden_bias",
    "hidden_weight",
    "obs_weight",
    "previous_action_weight",
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate_correction() -> dict[str, Any]:
    if lf_sha256(CORRECTION) != CORRECTION_LF_SHA256:
        raise ValueError("Winner-v24 importer correction bytes changed")
    if lf_sha256(FROZEN_IMPORTER) != FROZEN_IMPORTER_LF_SHA256:
        raise ValueError("Winner-v24 frozen importer bytes changed")
    value = json.loads(CORRECTION.read_text(encoding="utf-8"))
    if (
        value.get("schema_version")
        != "winner_v24.baseline_importer_correction.v1"
        or value.get("status")
        != "FROZEN_WINNER_V24_BASELINE_IMPORTER_CORRECTION"
        or value.get("failed_checks") != []
        or value.get("correction", {}).get("one_variable")
        != (
            "replace only the importer's gradient-key inventory with the exact "
            "12 leaves emitted by the frozen runner"
        )
        or set(value.get("correction", {}).get("actual_runner_gradient_keys", []))
        != CORRECTED_GRADIENT_KEYS
        or value.get("correction", {}).get("all_other_import_validation_unchanged")
        is not True
        or value.get("correction", {}).get("rejected_before_result_write") is not True
        or value.get("authority")
        != {
            "artifact_or_result_rewritten": False,
            "new_workflow_run_authorized": False,
            "optimizer_or_training_authorized": False,
            "pass_authorizes_only": (
                "strict import of the unchanged first-attempt artifact with the "
                "corrected trainable-leaf inventory"
            ),
            "robot_or_rdk_access": False,
        }
    ):
        raise ValueError("Winner-v24 importer correction authority changed")
    return value


def load_corrected_importer():
    correction = validate_correction()
    spec = importlib.util.spec_from_file_location(
        "winner_v24_baseline_frozen_importer", FROZEN_IMPORTER
    )
    if spec is None or spec.loader is None:
        raise ImportError("cannot load Winner-v24 frozen importer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    frozen_expected = set(correction["correction"]["frozen_importer_expected_keys"])
    if set(module.GRADIENT_KEYS) != frozen_expected:
        raise ValueError("Winner-v24 frozen importer key mismatch changed")
    module.GRADIENT_KEYS = set(CORRECTED_GRADIENT_KEYS)
    module.RECURRENT_KEYS = set(CORRECTED_RECURRENT_KEYS)
    module.OUTPUT_JSON = (
        ROOT / "outputs/analysis/winner_v24_baseline_anchored_cpu_result_v2.json"
    )
    module.OUTPUT_MD = (
        ROOT
        / "outputs/analysis/WINNER_V24_BASELINE_ANCHORED_CPU_RESULT_V2_20260722.md"
    )
    # The unchanged importer's attribution logic binds the active importer.
    # Point its module-global __file__ at this narrowly corrected wrapper.
    module.__file__ = str(Path(__file__).resolve())
    return module


def main() -> int:
    return load_corrected_importer().main()


if __name__ == "__main__":
    raise SystemExit(main())
