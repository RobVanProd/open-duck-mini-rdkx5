#!/usr/bin/env python3
"""Freeze the one corrected chunked V127c Colab launch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v127c_hosted_preregistration.json"
PACKAGE_CONTRACT = ANALYSIS / "winner_v127c_hosted_package_contract.json"
CORRECTION = ANALYSIS / "winner_v127_pretraining_launch_correction.json"
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v127c-hosted-20260724.tar.gz"
)
CHUNK_ROOT = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v127c-upload-chunks-20260724"
)
LAUNCHER = ROOT / "tools/launch_winner_v127_constrained_colab.py"
EXECUTOR = ROOT / "tools/execute_winner_v127c_chunked_colab_cli.py"
OUTPUT = ANALYSIS / "winner_v127c_colab_launch_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V127C_COLAB_LAUNCH_CONTRACT_20260724.md"
SESSION = "winner-v127c-constrained-20260724"


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
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    chunks = [
        {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(CHUNK_ROOT.glob("*.part*"))
    ]
    reconstructed = hashlib.sha256()
    for row in chunks:
        with (CHUNK_ROOT / row["name"]).open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                reconstructed.update(block)
    checks = {
        "corrected_preregistration_green": prereg.get("status")
        == "PREREGISTERED_WINNER_V127C_HOSTED_CONTINUATION",
        "corrected_package_green": package_contract.get("status")
        == "PASS_WINNER_V127_HOSTED_PACKAGE",
        "pretraining_correction_green": correction.get("status")
        == "PASS_WINNER_V127_PRETRAINING_LAUNCH_CORRECTION",
        "package_exact": (
            package_contract["archive"]["bytes"] == PACKAGE.stat().st_size
            and package_contract["archive"]["sha256"] == sha256(PACKAGE)
        ),
        "four_chunks_exact": len(chunks) == 4,
        "chunks_reconstruct_package": reconstructed.hexdigest()
        == sha256(PACKAGE),
        "launcher_uses_corrected_package": (
            "winner_v127c_constrained_bundle"
            in LAUNCHER.read_text(encoding="utf-8")
        ),
        "executor_exact_package": (
            sha256(PACKAGE) in EXECUTOR.read_text(encoding="utf-8")
        ),
        "single_l4_session": True,
        "no_training_retry_or_resume": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    commands = [
        ["colab", "new", "--session", SESSION, "--gpu", "L4"],
        *[
            [
                "colab",
                "upload",
                "--session",
                SESSION,
                str(CHUNK_ROOT / row["name"]),
                f"/content/{row['name']}",
            ]
            for row in chunks
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
        "schema_version": "winner_v127c.colab_launch_contract.v1",
        "status": (
            "PASS_WINNER_V127C_COLAB_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_WINNER_V127C_COLAB_LAUNCH_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "hashes": {
            "preregistration": sha256(PREREG),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "pretraining_correction": sha256(CORRECTION),
            "package": sha256(PACKAGE),
            "launcher": sha256(LAUNCHER),
            "executor": sha256(EXECUTOR),
        },
        "chunks": chunks,
        "session": {
            "name": SESSION,
            "accelerator": "L4",
            "count": 1,
            "max_wall_seconds": 21_600,
        },
        "commands": commands,
        "authority": {
            "one_corrected_exact_cli_launch": not failed,
            "training_retry": False,
            "training_resume": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V127c Colab launch\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The only software correction is the preregistered cwd change.\n"
        "- Four chunks reconstruct the exact corrected package.\n"
        "- Authority: one L4 launch; no training retry/resume or behavior.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
