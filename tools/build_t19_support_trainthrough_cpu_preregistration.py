#!/usr/bin/env python3
"""Preregister T19's zero-optimizer support train-through CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t19_support_trainthrough_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T19_SUPPORT_TRAINTHROUGH_CPU_PREREGISTRATION_20260726.md"
)
BASE = Path("D:/CodexProjects/Open_Duck_Playground-composed-v175")
COMPOSED = Path("D:/CodexProjects/Open_Duck_Playground-composed-t19-v2")
MANIFEST = COMPOSED / "T19_COMPOSED_SOURCE_MANIFEST.json"
T8_RESULT = ANALYSIS / "t8_state_coherent_handoff_result.json"
T18_PREREGISTRATION = (
    ANALYSIS / "t18_rate_coherent_support_preregistration.json"
)
T18_RESULT = ANALYSIS / "t18_rate_coherent_support_result.json"
V3_RESULT = (
    ANALYSIS / "winner_v3_variable_configuration_result_corrected.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
CALIBRATOR = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v96-response-conditioned-mechanics/"
    "winner_v96_universal_calibrator.onnx"
)
MODULE = ROOT / "patches" / "t19_support_trainthrough.py"
PATCH = ROOT / "patches" / "winner_t19_support_trainthrough.patch"
COMPOSER = ROOT / "tools" / "compose_t19_support_trainthrough_playground.py"
RUNNER = ROOT / "tools" / "run_t19_support_trainthrough_cpu_contract.py"
TEST = ROOT / "tests" / "test_t19_support_trainthrough.py"


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
            raise FileExistsError(f"refusing to overwrite T19: {path}")
    t8 = json.loads(T8_RESULT.read_text(encoding="utf-8"))
    t18_prereg = json.loads(
        T18_PREREGISTRATION.read_text(encoding="utf-8")
    )
    t18 = json.loads(T18_RESULT.read_text(encoding="utf-8"))
    v3 = json.loads(V3_RESULT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    sources = {
        "t8_result": receipt(T8_RESULT),
        "t18_preregistration": receipt(T18_PREREGISTRATION),
        "t18_result": receipt(T18_RESULT),
        "v3_result": receipt(V3_RESULT),
        "reference": receipt(REFERENCE),
        "calibrator": receipt(CALIBRATOR),
        "module": receipt(MODULE),
        "patch": receipt(PATCH),
        "composer": receipt(COMPOSER),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
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
    checks = {
        "t8_state_handoff_passed": (
            t8.get("status")
            == "HOLD_T8_STATE_COHERENT_HANDOFF"
            and t8.get("summary", {}).get(
                "all_handoff_contracts_pass"
            )
            is True
            and t8.get("decision")
            == "CLOSE_DIRECT_STATE_COHERENT_V121_HANDOFF_WITHOUT_TRAINING"
        ),
        "t18_formal_result_complete": (
            t18.get("status")
            == "HOLD_T18_RATE_COHERENT_SUPPORT_SCREEN"
            and t18.get("decision")
            == "CLOSE_ZERO_TRAINING_RATE_COHERENT_SUPPORT_COMPOSITION"
            and t18.get("summary", {}).get("green_cells") == 25
            and t18.get("summary", {}).get("total_cells") == 32
            and t18.get("execution", {}).get("optimizer_steps") == 0
        ),
        "t18_handoff_is_exact_250_plus_zero": (
            t18_prereg.get("handoff_contract", {}).get(
                "calibration_ticks"
            )
            == 250
            and t18_prereg.get("handoff_contract", {}).get(
                "home_return_ticks"
            )
            == 0
            and t18_prereg.get("handoff_contract", {})
            .get("boundary", {})
            .get("preserve_final_support_action_as_policy_previous_action")
            is True
            and t18_prereg.get("handoff_contract", {})
            .get("boundary", {})
            .get("preserve_applied_target_observer_bridge_state")
            is True
        ),
        "prior_full_variable_route_was_not_green": (
            v3.get("status")
            in {
                "HOLD_WINNER_V3_VARIABLE_CONFIGURATION",
                "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_RESULT",
            }
            or v3.get("failed_checks") not in (None, [])
            or v3.get("decision")
            not in {
                "PASS_WINNER_V3_VARIABLE_CONFIGURATION",
                "ADVANCE_WINNER_V3_VARIABLE_CONFIGURATION",
            }
        ),
        "composed_schema_exact": (
            manifest.get("schema_version")
            == "open_duck.t19_composed_source.v1"
        ),
        "all_source_receipts_present": all(
            item["bytes"] > 0 for item in sources.values()
        ),
        "no_optimizer_or_hosted_execution_authorized": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": (
            "open_duck.t19_support_trainthrough_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T19_SUPPORT_TRAINTHROUGH_CPU_CONTRACT"
            if not failed
            else "HOLD_T19_SUPPORT_TRAINTHROUGH_CPU_PREREGISTRATION"
        ),
        "question": (
            "Can the exact T18 support-coordinate transition be represented "
            "inside the V121 training environment with a complete support "
            "handoff on every episode reset, while remaining bit-exact when "
            "disabled?"
        ),
        "causal_basis": {
            "t18_result": "25/32 green; five misses are saturation-only and two are falls",
            "training_mismatch": (
                "the prior variable-configuration route began from home and "
                "did not train through T18's 250-tick support handoff"
            ),
            "reset_hazard": (
                "the stock Brax auto-reset restores data and observations but "
                "does not restore actuator, bridge, action-history, phase, or "
                "policy-state info"
            ),
            "selected_mechanism": (
                "source-coordinate V121 rate->G3->rate, bounded support map, "
                "physical final-rate transition, inverse observation map, "
                "and complete handoff reset"
            ),
        },
        "sources": sources,
        "playgrounds": playgrounds,
        "contract": {
            "seed": 100,
            "variable_configuration_envs": 64,
            "reference_path": str(REFERENCE.resolve()),
            "calibration_ticks": 250,
            "home_return_ticks": 0,
            "episode_length_for_reset_falsifier": 2,
            "required_enabled_checks": [
                "all prefixes survive",
                "final physical action equals universal support",
                "source target returns to home-coordinate zero",
                "source delay history is zero",
                "phase and policy hidden reset exactly",
                "applied-target observation equals the inverse physical bridge state",
                "data, observation and dynamic info restore exactly at the episode boundary",
            ],
            "default_off": (
                "base and composed 9-state reset/step trajectories are "
                "bit-exact over all common transition leaves"
            ),
            "execution_platform": "CPU only",
            "optimizer_steps": 0,
        },
        "decision_rule": {
            "pass": (
                "Every default-off, enabled-prefix, and full-reset check passes; "
                "earn a separately preregistered one-update CPU restore/export "
                "contract only."
            ),
            "fail": (
                "Close this implementation without tuning the support action, "
                "prefix length, coordinate map, rate vector, or reset rule."
            ),
            "hosted_training_earned_by_this_contract": False,
        },
        "authority": {
            "cpu_contract_authorized": not failed,
            "optimizer_step_authorized": False,
            "hosted_or_colab_training": False,
            "robot_or_rdk": False,
            "gate5": False,
            "torque_or_motion": False,
        },
        "execution_now": {
            "cpu_reset_contract": 0,
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
                "# T19 support train-through CPU preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Formal optimizer steps: `0`",
                "- Hosted/robot authority: `none`",
                (
                    "- Decision: pass earns only a separate one-update CPU "
                    "restore/export contract."
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
