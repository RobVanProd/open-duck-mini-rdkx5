#!/usr/bin/env python3
"""Freeze the one exact chunked V175 Colab launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v175_hosted_preregistration.json"
PACKAGE_CONTRACT = ANALYSIS / "winner_v175_hosted_package_contract.json"
TRANSPORT = ANALYSIS / "winner_v175_upload_transport_contract.json"
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v175-hosted-20260725.tar.gz"
)
CHUNK_ROOT = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v175-upload-chunks-20260725"
)
LAUNCHER = ROOT / "tools/launch_winner_v175_tangent_colab.py"
EXECUTOR = ROOT / "tools/execute_winner_v175_chunked_colab_cli.py"
OUTPUT = ANALYSIS / "winner_v175_colab_launch_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V175_COLAB_LAUNCH_CONTRACT_20260725.md"
SESSION = "winner-v175-tangent-20260725"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V175: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    transport = json.loads(TRANSPORT.read_text(encoding="utf-8"))
    chunks = [
        {
            "name": row["name"],
            "bytes": (CHUNK_ROOT / row["name"]).stat().st_size,
            "sha256": sha256(CHUNK_ROOT / row["name"]),
        }
        for row in transport["chunks"]
    ]
    launcher_text = LAUNCHER.read_text(encoding="utf-8")
    executor_text = EXECUTOR.read_text(encoding="utf-8")
    checks = {
        "v175_preregistration_green": (
            prereg.get("status")
            == "PREREGISTERED_WINNER_V175_HOSTED_CONTINUATION"
            and prereg.get("failed_checks") == []
        ),
        "v175_package_green": (
            package.get("status") == "PASS_WINNER_V175_HOSTED_PACKAGE"
            and package.get("failed_checks") == []
        ),
        "upload_transport_green": (
            transport.get("status") == "PASS_WINNER_V175_UPLOAD_TRANSPORT"
            and transport.get("failed_checks") == []
        ),
        "package_exact": (
            package["archive"]["bytes"] == PACKAGE.stat().st_size
            and package["archive"]["sha256"] == sha256(PACKAGE)
        ),
        "four_chunks_exact": (
            chunks == transport["chunks"] and len(chunks) == 4
        ),
        "launcher_pins_package_and_inputs": (
            sha256(PACKAGE) in launcher_text
            and sha256(PREREG) in launcher_text
            and package["bundle_manifest"]["sha256"] in launcher_text
        ),
        "executor_pins_package_and_launcher": (
            sha256(PACKAGE) in executor_text
            and sha256(LAUNCHER) in executor_text
        ),
        "single_l4_session": True,
        "no_training_retry_or_resume": True,
        "robot_surface_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
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
            "/content/launch_winner_v175_tangent_colab.py",
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
            "/content/winner_v175_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v175_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v175_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    payload = {
        "schema_version": "winner_v175.colab_launch_contract.v1",
        "status": (
            "PASS_WINNER_V175_COLAB_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_WINNER_V175_COLAB_LAUNCH_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "hashes": {
            "builder": sha256(Path(__file__).resolve()),
            "preregistration": sha256(PREREG),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "transport_contract": sha256(TRANSPORT),
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
            "one_exact_chunked_cli_launch": not failed,
            "training_retry": False,
            "training_resume": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V175 Colab launch contract\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Four chunks reconstruct the exact 100,025,492-byte package.\n"
        "- One L4 session, one launch, 21,600-second ceiling.\n"
        "- No retry, resume, behavior evaluation, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
