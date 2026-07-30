#!/usr/bin/env python3
"""Preregister T185F's runner-path-only recovery."""

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


T185E = ANALYSIS / "t185e_metric_receipt_recovery_preregistration.json"
RECOVERY = ANALYSIS / "t185e_runner_path_contract_recovery_20260730.json"
OUTPUT = (
    ANALYSIS
    / "t185f_metric_runner_path_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T185F_METRIC_RUNNER_PATH_RECOVERY_PREREGISTRATION_20260730.md"
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
            raise FileExistsError(f"refusing to overwrite T185F: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T185F preregistration requires clean worktree")
    t185e = load(T185E)
    recovery = load(RECOVERY)
    if (
        canonical_without(t185e, "preregistered_contract_sha256")
        != t185e["preregistered_contract_sha256"]
        or canonical_without(recovery, "result_sha256")
        != recovery["result_sha256"]
        or recovery["status"]
        != "INVALIDATE_T185E_RUNNER_PATH_CONTRACT_BEFORE_EXECUTION"
        or recovery["evidence"][
            "source_preregistered_contract_sha256"
        ]
        != t185e["preregistered_contract_sha256"]
        or any(value != 0 for value in recovery["execution"].values())
    ):
        raise RuntimeError("T185E path recovery identity changed")

    basis = {
        key: value
        for key, value in t185e.items()
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
        "open_duck.t185f_metric_runner_path_recovery_"
        "preregistration.v1"
    )
    basis["status"] = (
        "PREREGISTERED_T185F_METRIC_RUNNER_PATH_RECOVERY"
    )
    sources = {
        name: item
        for name, item in t185e["sources"].items()
        if name not in ("builder", "runner")
    }
    sources.update(
        {
            "builder": file_receipt(BUILDER),
            "runner": file_receipt(RUNNER),
            "t185e_preregistration": file_receipt(T185E),
            "t185e_runner_path_contract_recovery": file_receipt(RECOVERY),
        }
    )
    if not all(
        item.get("kind") in ("file", "directory")
        for item in sources.values()
    ):
        raise RuntimeError("T185F source receipt kind incomplete")
    basis["sources"] = sources
    basis["recovery_contract"] = {
        "prior_metric_and_receipt_recovery": t185e["recovery_contract"],
        "only_new_change": (
            "runner accepts explicit preregistration, result, and markdown "
            "paths to isolate T185F evidence"
        ),
        "saved_artifact_contract_unchanged": (
            basis["saved_artifact_contract"]
            == t185e["saved_artifact_contract"]
        ),
        "decision_rule_unchanged": (
            basis["decision_rule"] == t185e["decision_rule"]
        ),
        "authority_unchanged": basis["authority"] == t185e["authority"],
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
        "# T185F metric runner-path recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Only new change: isolated explicit runner paths\n"
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
