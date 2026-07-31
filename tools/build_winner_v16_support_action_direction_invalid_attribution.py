#!/usr/bin/env python3
"""Attribute the invalid first Winner-v16 direction diagnostic without interpreting it."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Iterator, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
FORMAL = ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json"
OUTPUT = ANALYSIS / "winner_v16_support_action_direction_invalid_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V16_SUPPORT_ACTION_DIRECTION_INVALID_ATTRIBUTION_20260721.md"
RUN_ID = 29845904251
RUN_HEAD = "f19d6ec8a0b7637748896851f479264224aca9d5"
ARTIFACT_ID = 8501416224
ARTIFACT_NAME = "winner-v16-support-action-direction-29845904251"
ARTIFACT_ZIP_BYTES = 217934
ARTIFACT_ZIP_SHA256 = "4288718b49061fe91557c9e7d0fe5553feec9101d8c60669913ddd479bacd86e"
RAW_RESULT_SHA256 = "4d22e4cc2f4b4f317ccd3ad0e8c637c8685db0706118524f9b37acf5c2035130"
RESULT_MEMBER = "winner-v16-support-action-direction-result.json"
DERIVED_FLOAT_ABS_TOLERANCE = 1.0e-12


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cell_key(cell: Mapping[str, Any]) -> tuple[str, str, str | None]:
    condition = cell.get("condition")
    return (
        str(cell["configuration_id"]),
        str(cell["plant"]),
        None if condition is None else str(condition["id"]),
    )


def differences(
    diagnostic: Any, formal: Any, path: str
) -> Iterator[tuple[str, Any, Any]]:
    if type(diagnostic) is not type(formal):
        yield path, diagnostic, formal
    elif isinstance(diagnostic, dict):
        if set(diagnostic) != set(formal):
            yield path, sorted(diagnostic), sorted(formal)
            return
        for name in sorted(diagnostic):
            yield from differences(diagnostic[name], formal[name], f"{path}.{name}")
    elif isinstance(diagnostic, list):
        if len(diagnostic) != len(formal):
            yield path, len(diagnostic), len(formal)
            return
        for index, (left, right) in enumerate(zip(diagnostic, formal, strict=True)):
            yield from differences(left, right, f"{path}[{index}]")
    elif diagnostic != formal:
        yield path, diagnostic, formal


def normalized_path(path: str) -> str:
    return re.sub(r"\[\d+\]", "[]", path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite attribution: {path}")

    artifact = args.artifact_zip.read_bytes()
    if len(artifact) != ARTIFACT_ZIP_BYTES or sha256(artifact) != ARTIFACT_ZIP_SHA256:
        raise ValueError("Winner-v16 artifact ZIP identity changed")
    with zipfile.ZipFile(args.artifact_zip) as archive:
        if sorted(archive.namelist()) != [
            RESULT_MEMBER,
            "winner-v16-support-action-direction-result.sha256",
        ]:
            raise ValueError("Winner-v16 artifact member set changed")
        raw_result = archive.read(RESULT_MEMBER)
    if sha256(raw_result) != RAW_RESULT_SHA256:
        raise ValueError("Winner-v16 raw result identity changed")
    result = json.loads(raw_result)
    if (
        result.get("status") != "INVALID_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC"
        or result.get("decision") != "DO_NOT_INTERPRET_DIRECTION_DIAGNOSTIC"
        or result.get("failed_validity_checks")
        != ["baseline_reproduces_all_24_formal_cells"]
        or result.get("execution")
        != {
            "optimizer_updates": 0,
            "diagnostic_cells": 168,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v16 invalid result contract changed")

    formal = json.loads(FORMAL.read_text(encoding="utf-8"))
    formal_by_label = {row["label"]: row for row in formal["checkpoint_results"]}
    exact_scalar_fields = (
        "configuration_id",
        "configuration_sha256",
        "plant",
        "condition",
        "support_pass",
        "maximum_jax_onnx_hidden_error",
        "final_h_out",
        "constant_normalized_prediction_mse",
    )
    mismatch_counts: Counter[str] = Counter()
    maximum_absolute_difference: defaultdict[str, float] = defaultdict(float)
    baseline_cells = 0
    exact_trace_hash_cells = 0
    exact_scalar_cells = 0
    exact_source_previous_action_cells = 0
    old_comparator_failures = 0
    for checkpoint in result["checkpoint_results"]:
        formal_checkpoint = formal_by_label[checkpoint["label"]]
        formal_rows = (
            formal_checkpoint["core_model_plant_cells"]
            + formal_checkpoint["sensor_transport_plant_cells"]
        )
        formal_index = {cell_key(cell): cell for cell in formal_rows}
        baseline = next(
            row
            for row in checkpoint["intervention_results"]
            if row["intervention"]["id"] == "BASELINE"
        )
        for diagnostic in baseline["cells"]:
            baseline_cells += 1
            expected = formal_index[cell_key(diagnostic)]
            scalar_exact = all(
                diagnostic[name] == expected[name] for name in exact_scalar_fields
            )
            trace_exact = all(
                diagnostic["trace_hashes"][name] == expected["trace_hashes"][name]
                for name in ("observations", "actions", "predictions", "hidden")
            )
            source_previous_exact = diagnostic["source_previous_action_out_exact"] is True
            exact_scalar_cells += int(scalar_exact)
            exact_trace_hash_cells += int(trace_exact)
            exact_source_previous_action_cells += int(source_previous_exact)
            if not scalar_exact or not trace_exact or not source_previous_exact:
                raise ValueError("Winner-v16 mismatch is not confined to derived floats")

            derived_differences = list(
                differences(diagnostic["terminal"], expected["terminal"], "terminal")
            ) + list(differences(diagnostic["episode"], expected["episode"], "episode"))
            old_comparator_failures += int(bool(derived_differences))
            if not derived_differences:
                raise ValueError("expected the frozen exact comparator to fail this cell")
            for path, observed, reference in derived_differences:
                if (
                    type(observed) is not float
                    or type(reference) is not float
                    or not math.isfinite(observed)
                    or not math.isfinite(reference)
                ):
                    raise ValueError("Winner-v16 derived mismatch is not finite float roundoff")
                delta = abs(observed - reference)
                if delta > DERIVED_FLOAT_ABS_TOLERANCE:
                    raise ValueError("Winner-v16 derived float mismatch exceeds correction bound")
                normalized = normalized_path(path)
                mismatch_counts[normalized] += 1
                maximum_absolute_difference[normalized] = max(
                    maximum_absolute_difference[normalized], delta
                )

    if (
        baseline_cells != 24
        or exact_trace_hash_cells != 24
        or exact_scalar_cells != 24
        or exact_source_previous_action_cells != 24
        or old_comparator_failures != 24
    ):
        raise ValueError("Winner-v16 baseline attribution population changed")
    global_maximum = max(maximum_absolute_difference.values())

    payload = {
        "schema_version": "winner_v16.support_action_direction_invalid_attribution.v1",
        "status": "INVALID_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_ATTRIBUTED",
        "decision": "CORRECT_ONLY_BASELINE_DERIVED_FLOAT_COMPARATOR_AND_FRESHLY_PREREGISTER",
        "repository_attribution": {
            "repository": "RobVanProd/open-duck-mini-rdkx5",
            "github_run_id": RUN_ID,
            "github_run_attempt": 1,
            "github_run_head_sha": RUN_HEAD,
            "github_artifact_id": ARTIFACT_ID,
            "github_artifact_name": ARTIFACT_NAME,
            "github_artifact_digest": f"sha256:{ARTIFACT_ZIP_SHA256}",
            "artifact_zip_bytes": ARTIFACT_ZIP_BYTES,
            "artifact_zip_sha256": ARTIFACT_ZIP_SHA256,
            "raw_result_sha256": RAW_RESULT_SHA256,
        },
        "attribution": {
            "baseline_cells": baseline_cells,
            "old_exact_comparator_failure_cells": old_comparator_failures,
            "exact_decision_and_scalar_cells": exact_scalar_cells,
            "exact_observation_action_prediction_hidden_hash_cells": exact_trace_hash_cells,
            "exact_source_previous_action_output_cells": exact_source_previous_action_cells,
            "mismatch_paths": {
                path: {
                    "count": mismatch_counts[path],
                    "maximum_absolute_difference": maximum_absolute_difference[path],
                }
                for path in sorted(mismatch_counts)
            },
            "global_maximum_absolute_difference": global_maximum,
            "cause": (
                "The frozen comparator required bit-exact JSON doubles for derived "
                "terminal and episode summaries even though all policy/observer trace "
                "hashes and every gate-setting categorical result reproduced exactly."
            ),
        },
        "correction": {
            "derived_float_fields": ["terminal", "episode"],
            "finite_absolute_tolerance": DERIVED_FLOAT_ABS_TOLERANCE,
            "all_other_compared_fields": "exact",
            "observation_action_prediction_hidden_trace_hashes": "exact",
            "population_interventions_offset_seeds_thresholds_and_selection_rule": "unchanged",
        },
        "execution": {
            "completed_diagnostic_cells": 168,
            "valid_interpreted_cells": 0,
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "authorizes_only": "one fresh comparator-corrected CPU diagnostic preregistration",
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v16 invalid direction-diagnostic attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / attempt: `{RUN_ID} / 1`",
                "- Completed / interpreted cells: `168 / 0`",
                "- Optimizer / robot access: `0 / 0`",
                "",
                "All 24 baseline observation, action, prediction, and hidden-state hashes",
                "reproduced exactly. Gate-setting results and all other compared fields",
                "also reproduced exactly. Only finite derived JSON doubles in `terminal`",
                f"and `episode` differed, by at most `{global_maximum:.3e}`.",
                "",
                "The only permitted correction is a fresh preregistration retaining exact",
                "trace and categorical comparisons while bounding those derived floats at",
                f"`{DERIVED_FLOAT_ABS_TOLERANCE:.1e}` absolute. The invalid intervention",
                "results remain uninterpreted.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
