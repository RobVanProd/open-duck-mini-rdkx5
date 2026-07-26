#!/usr/bin/env python3
"""Run T19's preregistered default-off digest correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import run_t19_support_trainthrough_cpu_contract as t19_contract


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t19_default_off_digest_correction_preregistration.json"
)
RESULT = ANALYSIS / "t19_default_off_digest_correction_result.json"
MARKDOWN = (
    ANALYSIS / "T19_DEFAULT_OFF_DIGEST_CORRECTION_RESULT_20260726.md"
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


def verify_receipt(value: dict[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T19 frozen receipt changed: {label}")


def verify_formal_result(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "result_sha256"
    }
    if canonical_sha256(basis) != value["result_sha256"]:
        raise RuntimeError("T19 formal result identity changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T19 correction requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite T19 correction path: {path}"
            )
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    prereg_basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T19_DEFAULT_OFF_DIGEST_CORRECTION"
        or canonical_sha256(prereg_basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T19 correction preregistration identity changed")
    for name, value in prereg["sources"].items():
        verify_receipt(value, name)
    formal_path = Path(prereg["sources"]["formal_result"]["path"])
    formal = json.loads(formal_path.read_text(encoding="utf-8"))
    verify_formal_result(formal)
    enabled = formal["enabled"]
    args.work_root.mkdir(parents=True)
    reference = Path(prereg["contract"]["reference_path"])
    base = Path(prereg["playgrounds"]["base"]["path"])
    composed = Path(prereg["playgrounds"]["composed"]["path"])
    seed = prereg["contract"]["seed"]
    base_value = t19_contract.run_worker(
        "default_off",
        base,
        reference,
        args.work_root / "base_default_off.json",
        env_count=1,
        seed=seed,
    )
    composed_value = t19_contract.run_worker(
        "default_off",
        composed,
        reference,
        args.work_root / "composed_default_off.json",
        env_count=1,
        seed=seed,
    )
    digest_pairs = list(
        zip(
            base_value["trajectory_digests"],
            composed_value["trajectory_digests"],
            strict=True,
        )
    )
    digest_equal = [left == right for left, right in digest_pairs]
    checks = {
        "canonical_default_off_trajectory_bit_exact": (
            len(digest_equal)
            == prereg["contract"]["expected_trajectory_digest_count"]
            and all(digest_equal)
        ),
        "default_off_shapes_exact": (
            base_value["observation_shape"]
            == composed_value["observation_shape"]
            == prereg["contract"]["expected_observation_shape"]
        ),
        "default_off_finite": (
            base_value["finite"] is True
            and composed_value["finite"] is True
        ),
        "default_off_cpu_only": (
            base_value["platforms"]
            == composed_value["platforms"]
            == ["cpu"]
        ),
        "frozen_enabled_evidence_green": (
            formal.get("failed_checks")
            == ["default_off_trajectory_bit_exact"]
            and enabled.get("failed_checks") == []
            and enabled.get("prefix_valid_count") == 64
            and enabled.get("episode_reset_count") == 64
            and all(enabled.get("checks", {}).values())
            and enabled.get("platforms") == ["cpu"]
        ),
        "enabled_worker_not_rerun": True,
        "optimizer_steps_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result_basis = {
        "schema_version": (
            "open_duck.t19_default_off_digest_correction_result.v1"
        ),
        "status": (
            prereg["decision_rule"]["pass_status"]
            if not failed
            else "HOLD_T19_DEFAULT_OFF_DIGEST_CORRECTION"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if not failed
            else prereg["decision_rule"]["failure_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "canonical_digest_equal_by_tick": digest_equal,
        "default_off": {
            "base": base_value,
            "composed": composed_value,
        },
        "reused_enabled_evidence": {
            "formal_result": prereg["sources"]["formal_result"],
            "prefix_valid_count": enabled["prefix_valid_count"],
            "episode_reset_count": enabled["episode_reset_count"],
            "failed_checks": enabled["failed_checks"],
        },
        "execution": {
            "default_off_workers": 2,
            "enabled_workers": 0,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **result_basis,
        "result_sha256": canonical_sha256(result_basis),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T19 default-off digest correction result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Canonical default-off matches: "
                    f"`{sum(digest_equal)}/{len(digest_equal)}`"
                ),
                "- Enabled 64-environment screen: `reused; not rerun`",
                "- Optimizer/hosted/robot execution: `0/0/0`",
                f"- Result SHA-256: `{value['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(
        "canonical_default_off_matches="
        f"{sum(digest_equal)}/{len(digest_equal)}"
    )
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
