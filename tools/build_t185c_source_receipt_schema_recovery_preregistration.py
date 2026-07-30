#!/usr/bin/env python3
"""Preregister T185C's receipt-schema-only recovery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
)


T185B = (
    ANALYSIS
    / "t185b_jit_phase_diagnostic_recovery_preregistration.json"
)
RECOVERY = ANALYSIS / "t185b_source_receipt_schema_recovery_20260730.json"
OUTPUT = (
    ANALYSIS
    / "t185c_source_receipt_schema_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T185C_SOURCE_RECEIPT_SCHEMA_RECOVERY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t185_in_episode_single_support_cpu_contract.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root is not an object: {path}")
    return value


def canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T185C: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T185C preregistration requires clean worktree")

    t185b = load(T185B)
    recovery = load(RECOVERY)
    if (
        canonical_without(t185b, "preregistered_contract_sha256")
        != t185b["preregistered_contract_sha256"]
        or canonical_without(recovery, "result_sha256")
        != recovery["result_sha256"]
    ):
        raise RuntimeError("T185B or recovery canonical identity changed")
    if (
        t185b["status"]
        != "PREREGISTERED_T185B_JIT_PHASE_DIAGNOSTIC_RECOVERY"
        or recovery["status"]
        != "INVALIDATE_T185B_SOURCE_RECEIPT_SCHEMA_BEFORE_EXECUTION"
        or recovery["evidence"][
            "source_preregistered_contract_sha256"
        ]
        != t185b["preregistered_contract_sha256"]
        or any(
            recovery["execution"][key] != 0
            for key in (
                "environment_contract_transitions",
                "optimizer_steps",
                "formal_behavior_cells",
                "hosted_compute_units",
                "robot_or_rdk_access",
            )
        )
    ):
        raise RuntimeError("T185B recovery authority or provenance changed")

    basis = {
        key: value
        for key, value in t185b.items()
        if key
        not in (
            "schema_version",
            "status",
            "sources",
            "checks",
            "failed_checks",
            "recovery_contract",
            "preregistered_contract_sha256",
        )
    }
    basis["schema_version"] = (
        "open_duck.t185c_source_receipt_schema_recovery_"
        "preregistration.v1"
    )
    basis["status"] = (
        "PREREGISTERED_T185C_SOURCE_RECEIPT_SCHEMA_RECOVERY"
    )
    sources: dict[str, dict[str, Any]] = {}
    for name, item in t185b["sources"].items():
        if name in ("builder", "runner"):
            continue
        sources[name] = {"kind": "file", **item}
    sources.update(
        {
            "builder": file_receipt(BUILDER),
            "runner": file_receipt(RUNNER),
            "t185b_preregistration": file_receipt(T185B),
            "t185b_source_receipt_schema_recovery": file_receipt(RECOVERY),
        }
    )
    basis["sources"] = sources
    basis["checks"] = {
        **t185b["checks"],
        "all_source_receipts_have_kind": all(
            item.get("kind") in ("file", "directory")
            for item in sources.values()
        ),
        "preexecution_stop_recorded": (
            recovery["execution"]["environment_contract_transitions"] == 0
            and recovery["execution"]["optimizer_steps"] == 0
            and not recovery["execution"]["result_artifact_written"]
            and not recovery["execution"]["work_directory_created"]
        ),
        "receipt_schema_only_change": (
            not recovery["correction"]["mechanism_change"]
            and not recovery["correction"]["scientific_contract_change"]
        ),
        "policy_and_cpu_contract_unchanged": (
            basis["mechanism"] == t185b["mechanism"]
            and basis["cpu_contract"] == t185b["cpu_contract"]
            and basis["decision_rule"] == t185b["decision_rule"]
            and basis["authority"] == t185b["authority"]
        ),
    }
    basis["failed_checks"] = sorted(
        name for name, passed in basis["checks"].items() if not passed
    )
    basis["recovery_contract"] = {
        "prior_jit_diagnostic_recovery": t185b["recovery_contract"],
        "only_new_change": (
            "add kind=file to file receipts and freeze the updated runner "
            "and builder receipts"
        ),
        "mechanism_unchanged": basis["mechanism"] == t185b["mechanism"],
        "playground_unchanged": basis["playground"] == t185b["playground"],
        "cpu_contract_unchanged": (
            basis["cpu_contract"] == t185b["cpu_contract"]
        ),
        "decision_rule_unchanged": (
            basis["decision_rule"] == t185b["decision_rule"]
        ),
        "authority_unchanged": basis["authority"] == t185b["authority"],
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
        "# T185C source-receipt schema recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Only new change: add `kind=file` to complete file receipts\n"
        "- JIT diagnostic recovery, mechanism, CPU contract, decision rule, "
        "and authority: unchanged\n"
        "- Environment / optimizer / behavior / hosted / robot now: "
        "`0/0/0/0/0`\n"
        f"- Failed preregistration checks: `{basis['failed_checks']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={basis['failed_checks']}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not basis["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
