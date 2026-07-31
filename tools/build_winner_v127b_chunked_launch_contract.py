#!/usr/bin/env python3
"""Freeze the corrected chunked V127 Colab launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CORRECTION = ANALYSIS / "winner_v127_upload_transport_correction.json"
CHUNK_ROOT = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v127-upload-chunks-20260724"
)
LAUNCHER = ROOT / "tools/launch_winner_v127_constrained_colab.py"
EXECUTOR = ROOT / "tools/execute_winner_v127b_chunked_colab_cli.py"
OUTPUT = ANALYSIS / "winner_v127b_chunked_colab_launch_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V127B_CHUNKED_COLAB_LAUNCH_CONTRACT_20260724.md"
SESSION = "winner-v127b-constrained-20260724"


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
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    chunks = [
        {
            "name": row["name"],
            "bytes": (CHUNK_ROOT / row["name"]).stat().st_size,
            "sha256": sha256(CHUNK_ROOT / row["name"]),
        }
        for row in correction["chunks"]
    ]
    checks = {
        "transport_correction_green": (
            correction.get("status")
            == "PASS_WINNER_V127_UPLOAD_TRANSPORT_CORRECTION"
            and correction.get("failed_checks") == []
            and correction.get("decision")
            == "AUTHORIZE_ONE_V127B_CHUNKED_TRANSPORT_LAUNCH"
        ),
        "all_chunks_exact": chunks == correction["chunks"],
        "launcher_exact": sha256(LAUNCHER)
        == "7947aa8798d415e257a143cdfc3a25addc8b068985e06758727c918edad9cfbf",
        "executor_exact": sha256(EXECUTOR)
        == "7dadda2e6a314f46b4ac7a5058ef2965e19348af1b8b333689ef8eccd922eab8",
        "executor_reconstructs_exact_package": (
            "temporary.replace(PACKAGE)"
            in EXECUTOR.read_text(encoding="utf-8")
        ),
        "l4_exact": '"L4"' in EXECUTOR.read_text(encoding="utf-8"),
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
        "schema_version": "winner_v127b.chunked_launch_contract.v1",
        "status": (
            "PASS_WINNER_V127B_CHUNKED_COLAB_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_WINNER_V127B_CHUNKED_COLAB_LAUNCH_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "hashes": {
            "correction": sha256(CORRECTION),
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
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V127b chunked Colab launch\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Four chunks reconstruct the exact frozen V127 package.\n"
        "- Authority: one L4 launch; no training retry or resume.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
