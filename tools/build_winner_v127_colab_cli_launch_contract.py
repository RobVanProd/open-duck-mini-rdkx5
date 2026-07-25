#!/usr/bin/env python3
"""Freeze the one-session V127 Colab CLI launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v127_hosted_preregistration.json"
PACKAGE_CONTRACT = ANALYSIS / "winner_v127_hosted_package_contract.json"
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v127-hosted-20260724.tar.gz"
)
LAUNCHER = ROOT / "tools/launch_winner_v127_constrained_colab.py"
EXECUTOR = ROOT / "tools/execute_winner_v127_colab_cli.py"
OUTPUT = ANALYSIS / "winner_v127_colab_cli_launch_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V127_COLAB_CLI_LAUNCH_CONTRACT_20260724.md"
SESSION = "winner-v127-constrained-20260724"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    package_contract = json.loads(
        PACKAGE_CONTRACT.read_text(encoding="utf-8")
    )
    hashes = {
        "preregistration": sha256(PREREG),
        "package_contract": sha256(PACKAGE_CONTRACT),
        "package": sha256(PACKAGE),
        "launcher": sha256(LAUNCHER),
        "executor": sha256(EXECUTOR),
    }
    checks = {
        "hosted_preregistration_green": prereg.get("status")
        == "PREREGISTERED_WINNER_V127_HOSTED_CONTINUATION",
        "package_contract_green": package_contract.get("status")
        == "PASS_WINNER_V127_HOSTED_PACKAGE",
        "package_hash_exact": package_contract["archive"]["sha256"]
        == hashes["package"],
        "package_bytes_exact": package_contract["archive"]["bytes"]
        == PACKAGE.stat().st_size,
        "l4_exact": '"L4"' in EXECUTOR.read_text(encoding="utf-8"),
        "pinned_software_exact": (
            '"jax[cuda12]==0.7.2"'
            in LAUNCHER.read_text(encoding="utf-8")
        ),
        "no_retry_or_resume": (
            '"retry": False' in LAUNCHER.read_text(encoding="utf-8")
            and '"resume": False' in LAUNCHER.read_text(encoding="utf-8")
        ),
        "robot_surface_absent": True,
        "training_or_behavior_not_run": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    commands = [
        ["colab", "new", "--session", SESSION, "--gpu", "L4"],
        [
            "colab",
            "upload",
            "--session",
            SESSION,
            str(PACKAGE),
            "/content/winner-v127-hosted-20260724.tar.gz",
        ],
        [
            "colab",
            "upload",
            "--session",
            SESSION,
            str(LAUNCHER),
            "/content/launch_winner_v127_constrained_colab.py",
        ],
        [
            "colab",
            "exec",
            "--session",
            SESSION,
            "--file",
            str(EXECUTOR),
            "--timeout",
            "21600",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v127_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v127_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v127_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    payload = {
        "schema_version": "winner_v127.colab_cli_launch_contract.v1",
        "status": (
            "PASS_WINNER_V127_COLAB_CLI_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_WINNER_V127_COLAB_CLI_LAUNCH_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "hashes": hashes,
        "package_bytes": PACKAGE.stat().st_size,
        "session": {
            "name": SESSION,
            "accelerator": "L4",
            "count": 1,
            "max_wall_seconds": 21_600,
        },
        "commands": commands,
        "recovery": {
            "download_result_archive_receipt_before_stop": True,
            "stop_session_after_pass_or_hold": True,
            "retry": False,
            "resume": False,
        },
        "authority": {
            "one_exact_cli_launch": not failed,
            "additional_attempt": False,
            "behavior_evaluation": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V127 Colab CLI launch contract\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Session: `{SESSION}`\n"
        "- Accelerator: one L4\n"
        f"- Package SHA-256: `{hashes['package']}`\n"
        "- Retry/resume: forbidden\n"
        "- Robot, RDK-X5, Gate 5, and behavior authority: absent\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
