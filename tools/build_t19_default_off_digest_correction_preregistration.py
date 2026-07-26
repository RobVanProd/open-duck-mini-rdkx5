#!/usr/bin/env python3
"""Preregister T19's reporting-only default-off digest correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS / "t19_default_off_digest_correction_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T19_DEFAULT_OFF_DIGEST_CORRECTION_PREREGISTRATION_20260726.md"
)
ATTRIBUTION = ANALYSIS / "t19_default_off_digest_attribution.json"
FORMAL_RESULT = ANALYSIS / "t19_support_trainthrough_cpu_result.json"
RECOVERY_PREREG = (
    ANALYSIS / "t19_support_trainthrough_cpu_recovery_preregistration.json"
)
BASE = Path("D:/CodexProjects/Open_Duck_Playground-composed-v175")
COMPOSED = Path("D:/CodexProjects/Open_Duck_Playground-composed-t19-v3")
MANIFEST = COMPOSED / "T19_COMPOSED_SOURCE_MANIFEST.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
FORMAL_RUNNER = ROOT / "tools" / "run_t19_support_trainthrough_cpu_contract.py"
CORRECTION_RUNNER = ROOT / "tools" / "run_t19_default_off_digest_correction.py"
BUILDER = (
    ROOT
    / "tools"
    / "build_t19_default_off_digest_correction_preregistration.py"
)


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
            raise FileExistsError(
                f"refusing to overwrite T19 correction preregistration: {path}"
            )
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY_PREREG.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    enabled = formal["enabled"]
    checks = {
        "attribution_gate_passed": (
            attribution.get("status")
            == "PASS_T19_DEFAULT_OFF_DIGEST_INVALIDATION"
            and attribution.get("decision")
            == "PREREGISTER_CANONICAL_LEAF_DIGEST_CORRECTION"
            and attribution.get("failed_checks") == []
        ),
        "formal_hold_is_default_off_only": (
            formal.get("status")
            == "HOLD_T19_SUPPORT_TRAINTHROUGH_CPU_CONTRACT"
            and formal.get("failed_checks")
            == ["default_off_trajectory_bit_exact"]
        ),
        "enabled_mechanism_evidence_is_green": (
            enabled.get("failed_checks") == []
            and enabled.get("prefix_valid_count") == 64
            and enabled.get("episode_reset_count") == 64
            and all(enabled.get("checks", {}).values())
        ),
        "enabled_mechanism_is_cpu_only": (
            enabled.get("platforms") == ["cpu"]
        ),
        "recovery_identity_is_green": (
            recovery.get("status")
            == "PREREGISTERED_T19_SUPPORT_TRAINTHROUGH_CPU_RECOVERY"
            and recovery.get("failed_checks") == []
            and formal.get("preregistered_contract_sha256")
            == recovery.get("preregistered_contract_sha256")
        ),
        "composed_schema_exact": (
            manifest.get("schema_version")
            == "open_duck.t19_composed_source.v1"
        ),
        "correction_is_reporting_only": (
            "leaf_count" in FORMAL_RUNNER.read_text(encoding="utf-8")
            and "str(structure)" not in FORMAL_RUNNER.read_text(
                encoding="utf-8"
            )
        ),
        "no_enabled_rerun_or_optimizer_authority": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        "attribution": receipt(ATTRIBUTION),
        "formal_result": receipt(FORMAL_RESULT),
        "recovery_preregistration": receipt(RECOVERY_PREREG),
        "reference": receipt(REFERENCE),
        "composed_manifest": receipt(MANIFEST),
        "formal_runner_with_canonical_digest": receipt(FORMAL_RUNNER),
        "correction_runner": receipt(CORRECTION_RUNNER),
        "builder": receipt(BUILDER),
    }
    basis = {
        "schema_version": (
            "open_duck.t19_default_off_digest_correction_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T19_DEFAULT_OFF_DIGEST_CORRECTION"
            if not failed
            else "HOLD_T19_DEFAULT_OFF_DIGEST_CORRECTION_PREREGISTRATION"
        ),
        "question": (
            "Does replacing process-local PyTreeDef text with an ordered "
            "leaf-count digest restore exact default-off equality between "
            "the frozen V175 base and T19 v3?"
        ),
        "causal_basis": {
            "formal_hold": (
                "T19's enabled 64-environment mechanism screen passed every "
                "semantic check; only the cross-process default-off digest "
                "comparison failed."
            ),
            "attribution": (
                "Two unchanged V175 default-off executions produced 0/9 "
                "matching hashes because the digest included process-local "
                "PyTreeDef text."
            ),
            "correction": (
                "Hash ordered leaf names, dtypes, shapes, and bytes plus a "
                "canonical leaf count. Change no transition or mechanism."
            ),
        },
        "sources": sources,
        "playgrounds": {
            "base": recovery["playgrounds"]["base"],
            "composed": recovery["playgrounds"]["composed"],
        },
        "contract": {
            "reference_path": str(REFERENCE.resolve()),
            "seed": recovery["contract"]["seed"],
            "expected_observation_shape": [115],
            "expected_trajectory_digest_count": 9,
            "workers": ["base_default_off", "composed_default_off"],
            "enabled_worker_rerun": False,
            "enabled_evidence_source": str(FORMAL_RESULT.resolve()),
            "canonical_digest": (
                "ordered flattened leaves with indexed names, dtype, shape, "
                "raw bytes, and an int64 leaf-count sentinel"
            ),
            "worker_processes_are_separate": True,
        },
        "decision_rule": {
            "pass": (
                "All nine canonical trajectory digests match exactly; both "
                "workers are finite CPU-only 115-D runs; and the frozen "
                "enabled evidence remains 64/64 green."
            ),
            "pass_status": (
                "PASS_T19_SUPPORT_TRAINTHROUGH_CPU_CONTRACT_CORRECTED"
            ),
            "pass_decision": "EARN_T19_ONE_UPDATE_CPU_CONTRACT",
            "failure_decision": "KEEP_T19_IMPLEMENTATION_CLOSED",
        },
        "authority": {
            "cpu_only": True,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "policy_motion": 0,
        },
        "checks": checks,
        "failed_checks": failed,
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T19 default-off digest correction preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Scope: `two default-off CPU workers only`",
                "- Enabled 64-environment screen: `reused by frozen receipt`",
                "- Optimizer/hosted/robot execution: `0/0/0`",
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
