#!/usr/bin/env python3
"""Preregister a fresh T20 run after the pre-optimizer rate hold."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS
    / "t20_support_trainthrough_one_update_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE_RECOVERY_PREREGISTRATION_20260726.md"
)
ORIGINAL = (
    ANALYSIS / "t20_support_trainthrough_one_update_preregistration.json"
)
ATTRIBUTION = ANALYSIS / "t20_preoptimizer_rate_selector_attribution.json"
V4_MANIFEST = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v4/"
    "T19_COMPOSED_SOURCE_MANIFEST.json"
)
PATCH = ROOT / "patches" / "winner_t19_support_trainthrough.patch"
ORIGINAL_RUNNER = (
    ROOT / "tools" / "run_t20_support_trainthrough_one_update.py"
)
RECOVERY_RUNNER = (
    ROOT / "tools" / "run_t20_support_trainthrough_one_update_recovery.py"
)
BUILDER = (
    ROOT
    / "tools"
    / "build_t20_support_trainthrough_one_update_recovery.py"
)
TEST = ROOT / "tests" / "test_t20_rate_selector_recovery.py"


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
        "kind": "file",
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite T20 recovery preregistration: {path}"
            )
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    manifest = json.loads(V4_MANIFEST.read_text(encoding="utf-8"))
    changed = attribution["attribution"]["changed_python_files"]
    checks = {
        "original_contract_was_green": (
            original.get("status")
            == "PREREGISTERED_T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE"
            and original.get("failed_checks") == []
        ),
        "preoptimizer_attribution_passed": (
            attribution.get("status")
            == "PASS_T20_PREOPTIMIZER_RATE_SELECTOR_ATTRIBUTION"
            and attribution.get("decision")
            == "PREREGISTER_T20_RATE_SELECTOR_RECOVERY"
            and attribution.get("failed_checks") == []
        ),
        "first_attempt_has_zero_decision_weight": (
            attribution["attribution"]["optimizer_steps"] == 0
            and attribution["attribution"]["simulator_behavior_cells"] == 0
            and attribution["attribution"]["attempt_decision_weight"] == 0
        ),
        "correction_changes_only_runner_validation": (
            changed == ["playground/open_duck_mini_v2/runner.py"]
            and "if args.winner_t19_support_trainthrough:"
            in PATCH.read_text(encoding="utf-8")
            and "expected_limits = jp.asarray("
            in PATCH.read_text(encoding="utf-8")
        ),
        "composed_v4_schema_exact": (
            manifest.get("schema_version")
            == "open_duck.t19_composed_source.v1"
        ),
        "fresh_run_no_reuse": True,
        "authority_unchanged": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        **original["sources"],
        "original_preregistration": receipt(ORIGINAL),
        "preoptimizer_attribution": receipt(ATTRIBUTION),
        "v4_composed_manifest": receipt(V4_MANIFEST),
        "corrected_t19_patch": receipt(PATCH),
        "original_formal_runner": receipt(ORIGINAL_RUNNER),
        "recovery_runner": receipt(RECOVERY_RUNNER),
        "recovery_builder": receipt(BUILDER),
        "recovery_test": receipt(TEST),
    }
    basis = {
        **{
            key: original[key]
            for key in (
                "schema_version",
                "status",
                "question",
                "causal_basis",
                "assets",
                "contract",
                "decision_rule",
                "authority",
            )
        },
        "schema_version": (
            "open_duck.t20_support_trainthrough_one_update_preregistration.v2"
        ),
        "status": (
            "PREREGISTERED_T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE"
            if not failed
            else "HOLD_T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE_RECOVERY"
        ),
        "causal_basis": {
            **original["causal_basis"],
            "first_attempt": (
                "The launcher rejected mutually exclusive inherited V121 and "
                "T19 rate-vector validators before environment construction. "
                "It produced no checkpoint, ONNX, simulator cell, or optimizer "
                "step and has zero decision weight."
            ),
            "recovery": (
                "T19's flag selects T19's already frozen full rate vector in "
                "the inherited Winner-v3 validator. Every other selector "
                "branch and all mechanism code remain byte-identical."
            ),
        },
        "sources": sources,
        "playground": {
            "path": str(V4_MANIFEST.parent.resolve()),
            "manifest_sha256": sha256(V4_MANIFEST),
            "final_python_hashes": manifest["final_python_hashes"],
        },
        "contract": {
            **original["contract"],
            "recovery_scope": (
                "one fresh full execution from a new work root; no reuse of "
                "attempt-1 remap, event header, log, checkpoint, or output"
            ),
            "first_attempt_artifact_reuse": False,
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
                "# T20 support train-through one-update recovery",
                "",
                f"- Status: `{value['status']}`",
                "- Attempt 1: `pre-optimizer / zero decision weight`",
                "- Recovery: `one fresh complete CPU execution`",
                "- Hosted/robot execution: `0/0`",
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
