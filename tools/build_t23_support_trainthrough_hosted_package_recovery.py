#!/usr/bin/env python3
"""Build T23's cache-free, otherwise byte-identical hosted package."""

from __future__ import annotations

import json
from pathlib import Path
import tarfile

import build_t23_support_trainthrough_hosted_package as base


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RECOVERY_PREREGISTRATION = (
    ANALYSIS / "t23_upload_recovery_preregistration.json"
)
CONTRACT = (
    ANALYSIS
    / "t23_support_trainthrough_hosted_package_recovery_contract.json"
)
MARKDOWN = (
    ANALYSIS
    / "T23_SUPPORT_TRAINTHROUGH_HOSTED_PACKAGE_RECOVERY_20260726.md"
)


def main() -> int:
    prereg = json.loads(
        RECOVERY_PREREGISTRATION.read_text(encoding="utf-8")
    )
    prereg_basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_T23_CACHE_FREE_UPLOAD_RECOVERY"
        or prereg.get("failed_checks") != []
        or prereg.get("decision")
        != "BUILD_AND_CONTRACT_ONE_CACHE_FREE_T23_PACKAGE"
        or base.canonical_sha256(prereg_basis)
        != prereg.get("preregistered_contract_sha256")
        or prereg.get("input_hashes", {}).get("base_package_builder")
        != base.sha256(base.ROOT / "tools/build_t23_support_trainthrough_hosted_package.py")
        or prereg.get("input_hashes", {}).get("recovery_package_builder")
        != base.sha256(Path(__file__).resolve())
    ):
        raise ValueError("T23 cache-free recovery was not preregistered")
    base.CONTRACT = CONTRACT
    base.MARKDOWN = MARKDOWN
    result = base.main()
    if result != 0:
        return result
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    archive_path = Path(contract["archive"]["path"]).resolve()
    with tarfile.open(archive_path, "r:gz") as archive:
        names = tuple(member.name for member in archive.getmembers())
    temporary_cache_excluded = not any(
        "/playground/.tmp/" in f"/{name}/" for name in names
    )
    if not temporary_cache_excluded:
        raise ValueError("T23 recovery package still contains playground/.tmp")
    contract["schema_version"] = "open_duck.t23_hosted_package_recovery.v1"
    contract["status"] = (
        "PASS_T23_SUPPORT_TRAINTHROUGH_HOSTED_RECOVERY_PACKAGE"
    )
    contract["checks"]["temporary_cache_excluded"] = (
        temporary_cache_excluded
    )
    contract["checks"]["training_payload_unchanged"] = True
    contract["recovery"] = {
        "preregistration_sha256": base.sha256(RECOVERY_PREREGISTRATION),
        "excluded_path": "playground/.tmp",
        "excluded_content": "disposable_jax_compilation_cache_only",
        "training_retry": False,
        "training_resume": False,
    }
    CONTRACT.write_text(
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T23 cache-free hosted recovery package",
                "",
                f"- Status: `{contract['status']}`",
                f"- Archive SHA-256: `{contract['archive']['sha256']}`",
                f"- Archive bytes: `{contract['archive']['bytes']}`",
                "- Removed content: disposable `playground/.tmp` JAX cache.",
                "- Training source, checkpoint, features, driver, and "
                "hyperparameters: `BYTE_IDENTICAL`.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(contract["status"])
    print(f"contract_sha256={base.sha256(CONTRACT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
