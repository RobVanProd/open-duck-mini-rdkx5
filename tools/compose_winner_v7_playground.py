#!/usr/bin/env python3
"""Compose the frozen 115-D winner-v7 CPU-evaluation Playground checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
PATCH_HASHES = {
    "ground_up_search_runner.patch": "6a176589b766de65ac2746c66f3387bfca5384d6ce4adf3703c752d8103a5e55",
    "ground_up_reference_conditioned.patch": "4138ecddb9ffc0df468a2780522c1732bc4b0e1a0865d181da1112d1c16902fb",
    "ground_up_recipe_search.patch": "3f5d892f5ce531207de6c86b18c9f5dbea83bc131a3fc2e5085851c2e4e3e5f8",
    "ground_up_stage1_mechanism_stack.patch": "cf5155dfd54a4699865b9823e8bf090f9f54b0e53df5583eb448e315d60053dc",
    "ground_up_nominal_reference_bootstrap.patch": "0d89b85815eb570115ec5f35d677aba68299f977b3e36c60b10dfa869533ebba",
    "ground_up_signed_progress_objective.patch": "13ddc699d3a005416a5790152b4a9d4f442216cfec4a991f93be65bde85ffa5b",
    "ground_up_reference_residual_actor.patch": "57bcf2394fa47745e9c26c6933e58a06c3799aba35e7000762befc5fac2f7d3b",
    "ground_up_hard_vector_command_support.patch": "900e65beaa4aa714ec352a527bf3f1a85888c0c76dab8d4cbef2352fa4986875",
    "ground_up_measured_actuator_bridge.patch": "133531963abea46cd0394526a2fa88b018fc21ca68c365863304e3e96d6ca0df",
    "ground_up_applied_target_observation.patch": "bdcac27115fcbe855079f5365ac046e863a9b302ff16f560d12a26cd492f2821",
    "ground_up_tracking_tail_exceedance.patch": "9f716243e0c4ef487ef4227ef0cb9f389ed43c0456435987ac0846e1b629811e",
}
NETWORK = ROOT / "patches/reference_residual_ppo_networks.py"
NETWORK_HASH = "546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repository", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_repository.resolve()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    run(["git", "clone", "--quiet", "--no-hardlinks", str(source), str(output)])
    run(["git", "checkout", "--quiet", CONTROL_COMMIT], output)
    with tempfile.TemporaryDirectory(prefix="winner-v7-patches-") as temp:
        temp_root = Path(temp)
        for name, expected in PATCH_HASHES.items():
            patch = ROOT / "patches" / name
            if canonical_lf_sha256(patch) != expected:
                raise ValueError(f"patch hash mismatch: {name}")
            canonical_patch = temp_root / name
            canonical_patch.write_bytes(patch.read_bytes().replace(b"\r\n", b"\n"))
            run(["git", "apply", "--check", str(canonical_patch)], output)
            run(["git", "apply", str(canonical_patch)], output)
    if canonical_lf_sha256(NETWORK) != NETWORK_HASH:
        raise ValueError("reference-residual network hash mismatch")
    (output / "playground/common/reference_residual_ppo_networks.py").write_bytes(
        NETWORK.read_bytes().replace(b"\r\n", b"\n")
    )
    run(["git", "diff", "--check"], output)
    changed = subprocess.check_output(
        ["git", "status", "--short"], cwd=output, text=True
    ).splitlines()
    files = sorted(
        {
            line[3:].strip().replace("\\", "/")
            for line in changed
            if len(line) >= 4
        }
    )
    receipt = {
        "schema_version": "winner_v7.playground_composition_receipt.v1",
        "base_commit": CONTROL_COMMIT,
        "patches_in_order": [
            {"name": name, "sha256": digest}
            for name, digest in PATCH_HASHES.items()
        ],
        "copied_network": {
            "path": "playground/common/reference_residual_ppo_networks.py",
            "sha256": NETWORK_HASH,
        },
        "composed_file_hashes": {
            name: sha256(output / name) for name in files
        },
    }
    receipt_path = output / "winner_v7_playground_composition_receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
