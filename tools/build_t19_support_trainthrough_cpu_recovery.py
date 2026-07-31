#!/usr/bin/env python3
"""Preregister a fresh T19 CPU run after two pre-result software holds."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS / "t19_support_trainthrough_cpu_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T19_SUPPORT_TRAINTHROUGH_CPU_RECOVERY_PREREGISTRATION_20260726.md"
)
ORIGINAL = ANALYSIS / "t19_support_trainthrough_cpu_preregistration.json"
FIRST_ATTEMPT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t19_support_trainthrough_cpu_v1"
)
DIAGNOSTIC = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t19_support_trainthrough_debug_v4/enabled.json"
)
BASE = Path("D:/CodexProjects/Open_Duck_Playground-composed-v175")
COMPOSED = Path("D:/CodexProjects/Open_Duck_Playground-composed-t19-v3")
MANIFEST = COMPOSED / "T19_COMPOSED_SOURCE_MANIFEST.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
MODULE = ROOT / "patches" / "t19_support_trainthrough.py"
PATCH = ROOT / "patches" / "winner_t19_support_trainthrough.patch"
COMPOSER = ROOT / "tools" / "compose_t19_support_trainthrough_playground.py"
RUNNER = ROOT / "tools" / "run_t19_support_trainthrough_cpu_contract.py"
TEST = ROOT / "tests" / "test_t19_support_trainthrough.py"
BUILDER = ROOT / "tools" / "build_t19_support_trainthrough_cpu_recovery.py"


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
            raise FileExistsError(f"refusing to overwrite T19 recovery: {path}")
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    diagnostic = json.loads(DIAGNOSTIC.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    first_base = FIRST_ATTEMPT / "base_default_off.json"
    first_composed = FIRST_ATTEMPT / "composed_default_off.json"
    first_enabled = FIRST_ATTEMPT / "enabled.json"
    sources = {
        "original_preregistration": receipt(ORIGINAL),
        "first_attempt_base": receipt(first_base),
        "first_attempt_composed": receipt(first_composed),
        "diagnostic": receipt(DIAGNOSTIC),
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
    checks = {
        "original_preregistration_was_green": (
            original.get("status")
            == "PREREGISTERED_T19_SUPPORT_TRAINTHROUGH_CPU_CONTRACT"
            and original.get("failed_checks") == []
        ),
        "first_attempt_produced_no_formal_result": (
            first_base.is_file()
            and first_composed.is_file()
            and not first_enabled.exists()
            and not (
                ANALYSIS / "t19_support_trainthrough_cpu_result.json"
            ).exists()
        ),
        "first_attempt_has_zero_decision_weight": True,
        "nested_info_restore_is_unit_tested": (
            "test_full_handoff_reset_restores_nested_info_trees"
            in TEST.read_text(encoding="utf-8")
            and "jax.tree.map(" in MODULE.read_text(encoding="utf-8")
        ),
        "diagnostic_localizes_only_nan_byte_digest": (
            diagnostic.get("failed_checks")
            == ["full_reset_data_exact"]
            and diagnostic.get("reset_data_difference", {}).get(
                "structure_exact"
            )
            is True
            and diagnostic.get("reset_data_difference", {}).get(
                "mismatches"
            )
            == []
        ),
        "numeric_reset_rule_is_frozen": (
            "reset_data_difference[\"mismatches\"] == []"
            in RUNNER.read_text(encoding="utf-8")
        ),
        "composed_schema_exact": (
            manifest.get("schema_version")
            == "open_duck.t19_composed_source.v1"
        ),
        "no_optimizer_or_hosted_authority": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": (
            "open_duck.t19_support_trainthrough_cpu_recovery.v1"
        ),
        "status": (
            "PREREGISTERED_T19_SUPPORT_TRAINTHROUGH_CPU_RECOVERY"
            if not failed
            else "HOLD_T19_SUPPORT_TRAINTHROUGH_CPU_RECOVERY"
        ),
        "question": original["question"],
        "causal_basis": {
            **original["causal_basis"],
            "first_execution_hold": (
                "The formal worker exited before an enabled artifact because "
                "nested info dictionaries were passed to an array-only reset "
                "selector. Both completed default-off artifacts and the whole "
                "attempt receive zero decision weight."
            ),
            "diagnostic_hold": (
                "After the nested-tree fix, every semantic check passed. The "
                "remaining byte-digest mismatch had identical tree structure "
                "and zero unequal leaves under exact equality with equal NaN "
                "sentinels. The recovery freezes exact numeric/tree equality "
                "rather than NaN payload bytes."
            ),
            "recovery_scope": (
                "one fresh complete run from new composed source and a new "
                "artifact root; no reuse or resume"
            ),
        },
        "sources": sources,
        "playgrounds": playgrounds,
        "contract": {
            **original["contract"],
            "numeric_data_reset_equality": (
                "identical pytree structure and every leaf array_equal with "
                "equal_nan=True"
            ),
            "first_attempt_artifact_reuse": False,
        },
        "decision_rule": original["decision_rule"],
        "authority": original["authority"],
        "execution_now": {
            "fresh_cpu_reset_contract": 0,
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
                "# T19 support train-through CPU recovery",
                "",
                f"- Status: `{value['status']}`",
                "- First formal attempt: `INVALID / zero decision weight`",
                (
                    "- Recovery: one fresh complete CPU run; no reuse, "
                    "optimizer, hosted compute, or robot access."
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
