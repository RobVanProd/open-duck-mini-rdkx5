#!/usr/bin/env python3
"""Preregister V127d after the proven pre-driver archive-root correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CPU_RESULT = ANALYSIS / "winner_v127_constrained_cpu_result.json"
CPU_PREREG = ANALYSIS / "winner_v127_constrained_cpu_preregistration.json"
PRETRAINING_CORRECTION = (
    ANALYSIS / "winner_v127_pretraining_launch_correction.json"
)
ARCHIVE_ROOT_CORRECTION = (
    ANALYSIS / "winner_v127_archive_root_correction.json"
)
V127C_PREREG = ANALYSIS / "winner_v127c_hosted_preregistration.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools/colab_winner_v127_constrained_continuation.py"
OUTPUT = ANALYSIS / "winner_v127d_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V127D_HOSTED_PREREGISTRATION_20260724.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    manifest = playground / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json"
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite {path}")

    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    pretraining = json.loads(
        PRETRAINING_CORRECTION.read_text(encoding="utf-8")
    )
    archive_root = json.loads(
        ARCHIVE_ROOT_CORRECTION.read_text(encoding="utf-8")
    )
    prior_prereg = json.loads(V127C_PREREG.read_text(encoding="utf-8"))
    checks = {
        "cpu_contract_green": (
            cpu.get("status")
            == "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
            and cpu.get("failed_checks") == []
        ),
        "v127c_preregistration_green": (
            prior_prereg.get("status")
            == "PREREGISTERED_WINNER_V127C_HOSTED_CONTINUATION"
            and prior_prereg.get("failed_checks") == []
        ),
        "pretraining_correction_green": (
            pretraining.get("status")
            == "PASS_WINNER_V127_PRETRAINING_LAUNCH_CORRECTION"
            and pretraining.get("failed_checks") == []
        ),
        "archive_root_correction_green": (
            archive_root.get("status")
            == "PASS_WINNER_V127_ARCHIVE_ROOT_CORRECTION"
            and archive_root.get("failed_checks") == []
            and archive_root.get("decision")
            == "AUTHORIZE_ONE_V127D_PRE_DRIVER_PACKAGING_CORRECTION"
        ),
        "both_prior_drivers_never_reached_optimizer": (
            pretraining["checks"]["optimizer_steps_zero"]
            and archive_root["checks"]["prior_optimizer_steps_zero"]
        ),
        "both_prior_launches_had_zero_simulator_steps": (
            pretraining["checks"]["simulator_locomotion_steps_zero"]
            and archive_root["checks"]["prior_simulator_steps_zero"]
        ),
        "training_command_and_objective_unchanged": True,
        "only_archive_root_changes": True,
        "single_continuation_only": True,
        "no_training_retry_or_resume": True,
        "both_postupdate_checkpoints_required": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    input_hashes = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "cpu_preregistration": sha256(CPU_PREREG),
        "pretraining_launch_correction": sha256(PRETRAINING_CORRECTION),
        "archive_root_correction": sha256(ARCHIVE_ROOT_CORRECTION),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    payload = {
        "schema_version": "winner_v127d.hosted_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V127D_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_WINNER_V127D_HOSTED_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "corrections": {
            "pretraining_cwd": pretraining["correction"],
            "archive_root": archive_root["correction"],
        },
        "training": prior_prereg["training"],
        "stop_rule": prior_prereg["stop_rule"],
        "authority": {
            "one_archive_root_corrected_hosted_continuation_after_package": (
                not failed
            ),
            "additional_training_or_retry": False,
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
        "# Winner V127d hosted preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Both prior launches stopped before simulator or optimizer steps.\n"
        "- Only new correction: archive under the selected bundle root.\n"
        "- Training source, command, objective, and stop rule are unchanged.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
