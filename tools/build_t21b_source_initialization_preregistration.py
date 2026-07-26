#!/usr/bin/env python3
"""Preregister T21b's corrected source-coordinate CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS / "t21b_source_initialization_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T21B_SOURCE_INITIALIZATION_CPU_PREREGISTRATION_20260726.md"
)
ATTRIBUTION = ANALYSIS / "t21_source_initialization_attribution.json"
T21_RESULT = ANALYSIS / "t21_two_rate_separation_cpu_result.json"
BASE = Path("D:/CodexProjects/Open_Duck_Playground-composed-v175")
COMPOSED = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v6"
)
MANIFEST = COMPOSED / "T19_COMPOSED_SOURCE_MANIFEST.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
MODULE = ROOT / "patches" / "t19_support_trainthrough.py"
PATCH = ROOT / "patches" / "winner_t19_support_trainthrough.patch"
COMPOSER = ROOT / "tools" / "compose_t19_support_trainthrough_playground.py"
RUNNER = ROOT / "tools" / "run_t21b_source_initialization_cpu_contract.py"
TEST = ROOT / "tests" / "test_t21_two_rate_separation.py"
BUILDER = (
    ROOT / "tools" / "build_t21b_source_initialization_preregistration.py"
)
SOURCE_RATES = [
    1.0,
    0.75,
    1.4736209064722061,
    1.4300791546702385,
    1.3976470567286015,
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.75,
    1.25,
    1.0,
    1.2215287424623966,
]
EXTERNAL_RATES = [
    1.0,
    0.75,
    1.5,
    1.5,
    1.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.75,
    1.25,
    1.0,
    1.25,
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T21b: {path}")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    t21 = json.loads(T21_RESULT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = {
        "attribution": receipt(ATTRIBUTION),
        "t21_formal_result": receipt(T21_RESULT),
        "reference": receipt(REFERENCE),
        "module": receipt(MODULE),
        "patch": receipt(PATCH),
        "composer": receipt(COMPOSER),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "builder": receipt(BUILDER),
        "composed_manifest": receipt(MANIFEST),
    }
    base_required = (
        BASE / "playground" / "common" / "runner.py",
        BASE / "playground" / "open_duck_mini_v2" / "joystick.py",
        BASE / "playground" / "open_duck_mini_v2" / "runner.py",
    )
    playgrounds = {
        "base": {
            "path": str(BASE.resolve()),
            "required_file_sha256": {
                path.relative_to(BASE).as_posix(): sha256(path)
                for path in base_required
            },
        },
        "composed": {
            "path": str(COMPOSED.resolve()),
            "manifest_sha256": sha256(MANIFEST),
            "final_python_hashes": manifest["final_python_hashes"],
        },
    }
    module_text = MODULE.read_text(encoding="utf-8")
    checks = {
        "attribution_passed": (
            attribution.get("status")
            == "PASS_T21_SOURCE_INITIALIZATION_ATTRIBUTION"
            and attribution.get("decision")
            == "PREREGISTER_T21B_SOURCE_COORDINATE_INITIALIZATION"
            and attribution.get("failed_checks") == []
        ),
        "t21_partial_result_has_zero_weight": (
            t21.get("status")
            == "HOLD_T21_TWO_RATE_SEPARATION_CPU_CONTRACT"
            and attribution.get("attribution", {}).get(
                "t21_partial_or_policy_selection_weight"
            )
            == 0
        ),
        "correction_is_prefix_initialization_only": (
            "def _prepare_prefix_initial(" in module_text
            and "source_action = inverse_action(" in module_text
            and module_text.count(
                "initial = self._prepare_prefix_initial(initial)"
            )
            == 2
        ),
        "algebraic_falsifier_was_exact": (
            attribution.get("attribution", {}).get(
                "maximum_coherent_initial_excess_normalized"
            )
            == 0.0
        ),
        "source_and_external_vectors_remain_distinct": (
            SOURCE_RATES != EXTERNAL_RATES
            and all(
                source <= external
                for source, external in zip(
                    SOURCE_RATES,
                    EXTERNAL_RATES,
                    strict=True,
                )
            )
        ),
        "composed_schema_exact": (
            manifest.get("schema_version")
            == "open_duck.t19_composed_source.v1"
        ),
        "no_optimizer_hosted_or_robot_authority": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": (
            "open_duck.t21b_source_initialization_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T21B_SOURCE_INITIALIZATION_CPU_CONTRACT"
            if not failed
            else "HOLD_T21B_SOURCE_INITIALIZATION_CPU_CONTRACT"
        ),
        "question": (
            "Does initializing the unscored prefix's source target at "
            "home + inverse_action(external_zero)*0.25 eliminate T21's sole "
            "source-rate violation while preserving every green T21 check?"
        ),
        "causal_basis": {
            "t21_hold": (
                "T21 passed default-off 9/9, all 64 variable configurations, "
                "and every external prefix check; only the source-rate history "
                "failed."
            ),
            "exact_attribution": (
                "The zero-source initialization predicted the measured "
                "0.041666664-rad excess. The coherent inverse-coordinate "
                "initialization has exactly zero algebraic excess."
            ),
            "correction": (
                "Initialize only the internal source-coordinate state for the "
                "unscored prefix; physical state, action scale, both rate "
                "vectors, source transition, and final reset remain frozen."
            ),
            "scope": (
                "fresh complete CPU contract with zero optimizer steps and no "
                "reuse of partial T21 worker results"
            ),
        },
        "sources": sources,
        "playgrounds": playgrounds,
        "contract": {
            "reference_path": str(REFERENCE.resolve()),
            "seed": 100,
            "default_off_states": 9,
            "variable_configuration_envs": 64,
            "prefix_ticks": 250,
            "action_size": 14,
            "observation_size": 115,
            "source_rate_limits_rad_s": SOURCE_RATES,
            "external_rate_limits_rad_s": EXTERNAL_RATES,
            "control_period_s": 0.02,
            "action_scale_rad": 0.25,
            "source_prefix_initialization": (
                "home + inverse_action(zeros(14))*0.25"
            ),
            "default_off_requirement": (
                "all nine canonical state digests byte-exact"
            ),
            "enabled_requirement": (
                "all existing checks pass for all 64 frozen variable "
                "configurations"
            ),
            "prefix_requirement": (
                "all 250 external targets and both rate histories pass; final "
                "support and source-home states are exact"
            ),
            "float_tolerance": "64 * float32 epsilon",
        },
        "decision_rule": {
            "pass": (
                "earn exactly one separately preregistered corrected 1,024-step "
                "CPU restore/update/export smoke (T22)"
            ),
            "fail": (
                "close T21b; no optimizer, hosted training, or behavior run"
            ),
            "partial_results": "zero decision weight",
        },
        "authority": {
            "cpu_only": True,
            "optimizer_steps_authorized": 0,
            "hosted_or_colab_compute_authorized": 0,
            "robot_or_rdk_access_authorized": 0,
        },
        "execution_now": {
            "fresh_formal_cpu_contract": 1,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "checks": checks,
        "failed_checks": failed,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T21b source-coordinate initialization preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Optimizer/hosted/robot authority: `0/0/0`",
                (
                    "- Pass earns only one separately preregistered "
                    "1,024-step CPU smoke."
                ),
                (
                    "- Contract SHA-256: "
                    f"`{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
