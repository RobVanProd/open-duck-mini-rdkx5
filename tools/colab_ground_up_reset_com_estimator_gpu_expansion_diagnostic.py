#!/usr/bin/env python3
"""Capture the frozen hosted expansion report and stop before PPO."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
from typing import Any


HOSTED_SOURCE = Path("/content/colab_ground_up_reset_com_estimator_training.py")
FIXED_REPORT = Path("/content/GROUND_UP_RESET_COM_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC.json")
RESULT_PREFIX = "GROUND_UP_RESET_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_RESULT="


class DiagnosticComplete(Exception):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_hosted_module() -> Any:
    spec = importlib.util.spec_from_file_location("frozen_reset_estimator_hosted", HOSTED_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen hosted source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_diagnostic(module: Any) -> int:
    if FIXED_REPORT.exists():
        raise FileExistsError(FIXED_REPORT)
    original_expand = module.hosted_expand
    marker_count = 0

    def report_then_stop(source: Path, destination: Path, report_path: Path) -> Any:
        nonlocal marker_count
        original_exception = None
        try:
            report = original_expand(source, destination, report_path)
        except RuntimeError as error:
            original_exception = repr(error)
            if not report_path.is_file():
                raise
            report = json.loads(report_path.read_text())
        if not report_path.is_file():
            raise RuntimeError("frozen expansion did not write its report")
        shutil.copy2(report_path, FIXED_REPORT)
        marker = {
            "status": "PASS_DIAGNOSTIC_REPORT_CAPTURED",
            "training_started": False,
            "original_expansion_status": report.get("status"),
            "original_exception": original_exception,
            "report": {
                "path": str(FIXED_REPORT),
                "sha256": sha256(FIXED_REPORT),
                "bytes": FIXED_REPORT.stat().st_size,
            },
        }
        marker_count += 1
        print(RESULT_PREFIX + json.dumps(marker, sort_keys=True), flush=True)
        raise DiagnosticComplete

    module.hosted_expand = report_then_stop
    try:
        module.main()
    except DiagnosticComplete:
        if marker_count != 1:
            raise RuntimeError(f"expected one diagnostic marker, found {marker_count}")
        return 0
    raise RuntimeError("diagnostic reached the training boundary")


def main() -> int:
    return run_diagnostic(load_hosted_module())


if __name__ == "__main__":
    raise SystemExit(main())
