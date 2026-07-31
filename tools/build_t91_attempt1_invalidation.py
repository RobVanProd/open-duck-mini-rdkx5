#!/usr/bin/env python3
"""Record the reporting-only T91 attempt-1 abort without a policy decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t91_com_endpoint_retention_preregistration.json"
MANIFEST = Path(
    "D:/CodexArtifacts/open-duck-policy/t91_com_endpoint_retention_v1/"
    "07_TORSO_COM_X_NEG/T84_ROLLING_HALF/p30/manifest.json"
)
STDERR = Path(
    "D:/CodexArtifacts/open-duck-policy/t91_runner.stderr.log"
)
OUTPUT = ANALYSIS / "t91_com_endpoint_retention_attempt1_invalidation.json"
MARKDOWN = (
    ANALYSIS / "T91_COM_ENDPOINT_RETENTION_ATTEMPT1_INVALIDATION_20260728.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite T91 invalidation: {path}"
            )
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    stderr = STDERR.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = {
        "v1_preregistration_exact": (
            prereg["status"]
            == "PREREGISTERED_T91_COM_ENDPOINT_RETENTION_DIAGNOSTIC"
            and not prereg["failed_checks"]
        ),
        "one_complete_block_only": (
            manifest["block_contract"]["condition"]["id"]
            == "TORSO_COM_X_NEG"
            and manifest["block_contract"]["policy"]["checkpoint_id"]
            == "T84_ROLLING_HALF"
            and manifest["block_contract"]["fit"]["fit_id"] == "p30"
            and len(manifest["traces"]) == 4
        ),
        "reporting_keyerror_exact": (
            'KeyError: \'green_cells\'' in stderr
            and 'block_result["green_cells"]' in stderr
        ),
        "no_formal_result_emitted": not (
            ANALYSIS / "t91_com_endpoint_retention_result.json"
        ).exists(),
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t91_com_endpoint_retention_attempt1_invalidation.v1"
        ),
        "status": (
            "INVALIDATED_T91_ATTEMPT1_REPORTING_ONLY"
            if not failed
            else "HOLD_T91_ATTEMPT1_INVALIDATION"
        ),
        "decision": (
            "EARN_T91_V2_REPORTING_CORRECTION_PREREGISTRATION_ONLY"
            if not failed
            else "STOP_T91_AND_REPAIR_INVALIDATION"
        ),
        "classification": "REPORTING_ONLY_ABORT_AFTER_ONE_COMPLETE_BLOCK",
        "error": "KeyError: green_cells",
        "root_cause": (
            "The evaluator block result contains cells and block_green, "
            "but the wrapper progress print requested a nonexistent "
            "green_cells field after the block had completed."
        ),
        "formal_policy_decision": None,
        "attempt1_block_reuse": False,
        "v2_requirement": (
            "Freeze the one-line reporting correction in a new "
            "preregistration and rerun all 16 cells from a fresh cache root."
        ),
        "receipts": {
            "v1_preregistration": receipt(PREREG),
            "completed_block_manifest": receipt(MANIFEST),
            "stderr": receipt(STDERR),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "completed_behavior_cells_without_decision": 4,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t91_v2_preregistration": not failed,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T91 attempt-1 invalidation",
                "",
                f"- Status: `{value['status']}`",
                "- Classification: reporting-only abort after one block",
                "- Formal policy decision: `NONE`",
                "- Attempt-1 block reuse: `NO`",
                "- Correction: one progress-report field only",
                "- V2 must rerun all 16 cells from a fresh cache root",
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
