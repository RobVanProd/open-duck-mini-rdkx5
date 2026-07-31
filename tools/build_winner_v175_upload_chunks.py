#!/usr/bin/env python3
"""Split and verify V175's frozen hosted archive for Colab transport."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v175_hosted_package_contract.json"
ARCHIVE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v175-hosted-20260725.tar.gz"
)
CHUNK_ROOT = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v175-upload-chunks-20260725"
)
OUTPUT = ANALYSIS / "winner_v175_upload_transport_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V175_UPLOAD_TRANSPORT_CONTRACT_20260725.md"
CHUNK_BYTES = 25_165_824


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (CHUNK_ROOT, OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V175: {path}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        contract.get("status") != "PASS_WINNER_V175_HOSTED_PACKAGE"
        or contract["archive"]["bytes"] != ARCHIVE.stat().st_size
        or contract["archive"]["sha256"] != sha256(ARCHIVE)
    ):
        raise ValueError("V175 archive contract changed")

    CHUNK_ROOT.mkdir(parents=True)
    chunks = []
    with ARCHIVE.open("rb") as source:
        index = 0
        while True:
            data = source.read(CHUNK_BYTES)
            if not data:
                break
            path = CHUNK_ROOT / f"{ARCHIVE.name}.part{index:03d}"
            path.write_bytes(data)
            chunks.append(
                {
                    "name": path.name,
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
            index += 1
    reconstructed = hashlib.sha256()
    reconstructed_bytes = 0
    for row in chunks:
        path = CHUNK_ROOT / row["name"]
        reconstructed_bytes += path.stat().st_size
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                reconstructed.update(block)
    checks = {
        "package_contract_green": True,
        "four_chunks_exact": len(chunks) == 4,
        "first_three_chunks_full": all(
            row["bytes"] == CHUNK_BYTES for row in chunks[:3]
        ),
        "last_chunk_nonempty_and_bounded": (
            0 < chunks[-1]["bytes"] <= CHUNK_BYTES
        ),
        "reconstructed_bytes_exact": (
            reconstructed_bytes == ARCHIVE.stat().st_size
        ),
        "reconstructed_sha256_exact": (
            reconstructed.hexdigest() == sha256(ARCHIVE)
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v175.upload_transport.v1",
        "status": (
            "PASS_WINNER_V175_UPLOAD_TRANSPORT"
            if not failed
            else "HOLD_WINNER_V175_UPLOAD_TRANSPORT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "builder": sha256(Path(__file__).resolve()),
            "package_contract": sha256(CONTRACT),
            "archive": sha256(ARCHIVE),
        },
        "archive": {
            "path": str(ARCHIVE),
            "bytes": ARCHIVE.stat().st_size,
            "sha256": sha256(ARCHIVE),
        },
        "chunk_root": str(CHUNK_ROOT),
        "chunk_bytes": CHUNK_BYTES,
        "chunks": chunks,
        "authority": {
            "one_exact_chunked_colab_launch_contract": not failed,
            "training_started": False,
            "retry_or_resume": False,
            "robot_or_rdk": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V175 upload transport\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Exact package: `{ARCHIVE.stat().st_size}` bytes, "
        f"`{sha256(ARCHIVE)}`.\n"
        "- Four independently hashed chunks reconstruct the exact package.\n"
        "- Transport only; no training, retry, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
