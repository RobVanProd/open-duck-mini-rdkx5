#!/usr/bin/env python3
"""Preregister T185E's receipt-only recovery of T185D."""

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


T185D = ANALYSIS / "t185d_metric_readback_recovery_preregistration.json"
RECOVERY = ANALYSIS / "t185d_source_receipt_schema_recovery_20260730.json"
OUTPUT = (
    ANALYSIS
    / "t185e_metric_receipt_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T185E_METRIC_RECEIPT_RECOVERY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t185d_metric_readback_recovery.py"


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
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T185E: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T185E preregistration requires clean worktree")
    t185d = load(T185D)
    recovery = load(RECOVERY)
    if (
        canonical_without(t185d, "preregistered_contract_sha256")
        != t185d["preregistered_contract_sha256"]
        or canonical_without(recovery, "result_sha256")
        != recovery["result_sha256"]
        or recovery["status"]
        != "INVALIDATE_T185D_SOURCE_RECEIPT_SCHEMA_BEFORE_EXECUTION"
        or recovery["evidence"][
            "source_preregistered_contract_sha256"
        ]
        != t185d["preregistered_contract_sha256"]
        or any(
            recovery["execution"][key] != 0
            for key in recovery["execution"]
        )
    ):
        raise RuntimeError("T185D recovery identity changed")

    basis = {
        key: value
        for key, value in t185d.items()
        if key
        not in (
            "schema_version",
            "status",
            "sources",
            "recovery_contract",
            "preregistered_contract_sha256",
        )
    }
    basis["schema_version"] = (
        "open_duck.t185e_metric_receipt_recovery_"
        "preregistration.v1"
    )
    basis["status"] = (
        "PREREGISTERED_T185E_METRIC_RECEIPT_RECOVERY"
    )
    sources: dict[str, dict[str, Any]] = {}
    for name, item in t185d["sources"].items():
        if name in ("builder", "runner"):
            continue
        sources[name] = {"kind": "file", **item}
    sources.update(
        {
            "builder": file_receipt(BUILDER),
            "runner": file_receipt(RUNNER),
            "t185d_preregistration": file_receipt(T185D),
            "t185d_source_receipt_schema_recovery": file_receipt(RECOVERY),
        }
    )
    if not all(
        item.get("kind") in ("file", "directory")
        for item in sources.values()
    ):
        raise RuntimeError("T185E source receipt kind remains incomplete")
    basis["sources"] = sources
    basis["recovery_contract"] = {
        "prior_metric_recovery": t185d["recovery_contract"],
        "only_new_change": (
            "add kind=file to complete file receipts and freeze updated "
            "builder and runner receipts"
        ),
        "saved_artifact_contract_unchanged": (
            basis["saved_artifact_contract"]
            == t185d["saved_artifact_contract"]
        ),
        "decision_rule_unchanged": (
            basis["decision_rule"] == t185d["decision_rule"]
        ),
        "authority_unchanged": basis["authority"] == t185d["authority"],
        "all_source_receipts_have_kind": True,
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
        "# T185E metric receipt recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Only new change: complete every file receipt with `kind=file`\n"
        "- Metric rules, event artifact, decision, and authority: unchanged\n"
        "- New simulator / optimizer / inference / behavior / hosted / "
        "robot: `0/0/0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
