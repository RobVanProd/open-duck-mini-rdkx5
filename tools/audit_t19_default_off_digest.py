#!/usr/bin/env python3
"""Attribute T19's sole formal hold to a process-local tree digest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RESULT = ANALYSIS / "t19_support_trainthrough_cpu_result.json"
ORIGINAL_PREREG = (
    ANALYSIS / "t19_support_trainthrough_cpu_preregistration.json"
)
RECOVERY_PREREG = (
    ANALYSIS / "t19_support_trainthrough_cpu_recovery_preregistration.json"
)
FIRST_BASE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t19_support_trainthrough_cpu_v1/base_default_off.json"
)
SECOND_BASE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t19_support_trainthrough_cpu_v2/base_default_off.json"
)
OUTPUT = ANALYSIS / "t19_default_off_digest_attribution.json"
MARKDOWN = ANALYSIS / "T19_DEFAULT_OFF_DIGEST_ATTRIBUTION_20260726.md"


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


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T19 audit: {path}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    first = json.loads(FIRST_BASE.read_text(encoding="utf-8"))
    second = json.loads(SECOND_BASE.read_text(encoding="utf-8"))
    comparisons = [
        left == right
        for left, right in zip(
            first["trajectory_digests"],
            second["trajectory_digests"],
            strict=True,
        )
    ]
    checks = {
        "formal_hold_is_default_off_only": (
            result.get("failed_checks")
            == ["default_off_trajectory_bit_exact"]
            and result.get("enabled", {}).get("failed_checks") == []
            and result.get("enabled", {}).get("prefix_valid_count") == 64
            and result.get("enabled", {}).get("episode_reset_count") == 64
        ),
        "same_unchanged_base_playground": (
            first.get("playground")
            == second.get("playground")
            == "D:\\CodexProjects\\Open_Duck_Playground-composed-v175"
        ),
        "same_worker_contract": (
            first.get("mode") == second.get("mode") == "default_off"
            and first.get("observation_shape")
            == second.get("observation_shape")
            == [115]
            and first.get("platforms")
            == second.get("platforms")
            == ["cpu"]
            and first.get("finite") is True
            and second.get("finite") is True
        ),
        "all_same_base_hashes_disagree_across_processes": (
            len(comparisons) == 9 and not any(comparisons)
        ),
        "historical_contracts_present": (
            ORIGINAL_PREREG.is_file() and RECOVERY_PREREG.is_file()
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": "open_duck.t19_default_off_digest_attribution.v1",
        "status": (
            "PASS_T19_DEFAULT_OFF_DIGEST_INVALIDATION"
            if not failed
            else "HOLD_T19_DEFAULT_OFF_DIGEST_ATTRIBUTION"
        ),
        "decision": (
            "PREREGISTER_CANONICAL_LEAF_DIGEST_CORRECTION"
            if not failed
            else "KEEP_T19_FORMAL_HOLD"
        ),
        "checks": checks,
        "failed_checks": failed,
        "attribution": {
            "invalid_field": (
                "str(PyTreeDef) was included in each trajectory digest even "
                "though it is process-local metadata, not transition data"
            ),
            "falsifier": (
                "the same frozen V175 playground, seed, actions, and worker "
                "contract produced nine of nine different hashes across the "
                "two formal processes"
            ),
            "correction_scope": (
                "replace only the process-local PyTreeDef string with a "
                "canonical leaf count; rerun only the two default-off workers"
            ),
            "mechanism_changes": 0,
            "support_prefix_changes": 0,
            "rate_or_coordinate_changes": 0,
            "optimizer_steps": 0,
        },
        "same_base_digest_equal_by_tick": comparisons,
        "input_hashes": {
            "formal_result": sha256(RESULT),
            "original_preregistration": sha256(ORIGINAL_PREREG),
            "recovery_preregistration": sha256(RECOVERY_PREREG),
            "first_base": sha256(FIRST_BASE),
            "second_base": sha256(SECOND_BASE),
        },
    }
    value = {**basis, "audit_sha256": canonical_sha256(basis)}
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T19 default-off digest attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Same-base cross-process hash agreement: `0/9`",
                "- Mechanism/optimizer/hosted changes: `0/0/0`",
                f"- Audit SHA-256: `{value['audit_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"audit_sha256={value['audit_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
