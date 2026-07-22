#!/usr/bin/env python3
"""Apply the frozen ZIP-path correction, then run the strict importer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import stat
from typing import Any
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FROZEN_IMPORTER = ROOT / "tools/import_winner_v24_baseline_anchored_one_update_result.py"
CORRECTION = ROOT / "outputs/analysis/winner_v24_one_update_importer_path_correction.json"
CORRECTION_LF_SHA256 = "85b429510ab386ab6533a6c7962905c78037afe54b7f28cdafb4fd88c07c3815"
FROZEN_IMPORTER_LF_SHA256 = "79808e19be92754118af94c565ef11d0031e30790e370f75aa15d1483e1277f8"
RAW_RESULT_PATH = "winner-v24-baseline-anchored-one-update-result.json"
RAW_RECEIPT_PATH = "winner-v24-baseline-anchored-one-update-result.sha256"
SNAPSHOT_PATH = (
    "winner-v24-baseline-anchored-one-update-work/"
    "winner_v24_baseline_anchored_update_101.npz"
)
GRAPH_PATH = (
    "winner-v24-baseline-anchored-one-update-work/"
    "winner_v24_baseline_anchored_update_101.onnx"
)
EXPECTED_PATHS = {RAW_RESULT_PATH, RAW_RECEIPT_PATH, SNAPSHOT_PATH, GRAPH_PATH}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate_correction() -> dict[str, Any]:
    if lf_sha256(CORRECTION) != CORRECTION_LF_SHA256:
        raise ValueError("Winner-v24 one-update importer correction bytes changed")
    if lf_sha256(FROZEN_IMPORTER) != FROZEN_IMPORTER_LF_SHA256:
        raise ValueError("Winner-v24 one-update frozen importer bytes changed")
    value = json.loads(CORRECTION.read_text(encoding="utf-8"))
    if (
        value.get("schema_version")
        != "winner_v24.one_update_importer_path_correction.v1"
        or value.get("status")
        != "FROZEN_WINNER_V24_ONE_UPDATE_IMPORTER_PATH_CORRECTION"
        or value.get("failed_checks") != []
        or set(value.get("correction", {}).get("actual_members", []))
        != EXPECTED_PATHS
        or value.get("correction", {}).get("one_variable")
        != (
            "replace only the two flattened binary member names with the exact "
            "GitHub-preserved work-directory paths"
        )
        or value.get("correction", {}).get(
            "all_member_safety_size_hash_and_result_validation_unchanged"
        )
        is not True
        or value.get("correction", {}).get("rejected_before_result_read") is not True
        or value.get("authority")
        != {
            "artifact_or_result_rewritten": False,
            "new_workflow_run_authorized": False,
            "optimizer_or_training_authorized": False,
            "pass_authorizes_only": (
                "strict import of the unchanged first-attempt artifact with its "
                "exact GitHub-preserved member paths"
            ),
            "robot_or_rdk_access": False,
        }
    ):
        raise ValueError("Winner-v24 one-update importer correction changed")
    return value


def corrected_read_artifact(path: Path, module: Any) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != EXPECTED_PATHS:
            raise ValueError("Winner-v24 one-update corrected inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v24 one-update artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute()
                or ".." in member.parts
                or "." in member.parts
                or "\\" in info.filename
                or info.flag_bits & 1
                or info.is_dir()
                or file_type == stat.S_IFLNK
                or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v24 one-update artifact has unsafe member")
        return {
            module.RAW_RESULT_NAME: archive.read(RAW_RESULT_PATH),
            module.RAW_RECEIPT_NAME: archive.read(RAW_RECEIPT_PATH),
            module.SNAPSHOT_NAME: archive.read(SNAPSHOT_PATH),
            module.GRAPH_NAME: archive.read(GRAPH_PATH),
        }


def load_corrected_importer():
    validate_correction()
    spec = importlib.util.spec_from_file_location(
        "winner_v24_one_update_frozen_importer", FROZEN_IMPORTER
    )
    if spec is None or spec.loader is None:
        raise ImportError("cannot load Winner-v24 one-update frozen importer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.read_artifact = lambda path: corrected_read_artifact(path, module)
    module.OUTPUT_JSON = (
        ROOT
        / "outputs/analysis/winner_v24_baseline_anchored_one_update_cpu_result_v2.json"
    )
    module.OUTPUT_MD = (
        ROOT
        / "outputs/analysis/WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_RESULT_V2_20260722.md"
    )
    module.__file__ = str(Path(__file__).resolve())
    return module


def main() -> int:
    return load_corrected_importer().main()


if __name__ == "__main__":
    raise SystemExit(main())
