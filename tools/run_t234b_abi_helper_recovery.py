#!/usr/bin/env python3
"""Execute the exact T234 ABI-helper recovery."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess

import onnx

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    abi as model_abi,
    canonical_sha256,
    receipt,
    verify,
)


PREREG = ANALYSIS / "t234b_abi_helper_recovery_preregistration.json"
OUTPUT = ANALYSIS / "t234b_abi_helper_recovery_result.json"
MARKDOWN = ANALYSIS / "T234B_ABI_HELPER_RECOVERY_RESULT_20260730.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t234b_abi_helper_recovery_v1"
)


def adapted_abi(value):
    model = onnx.load(value) if isinstance(value, Path) else value
    return model_abi(model)


def load_original(path: Path):
    spec = importlib.util.spec_from_file_location("t234_original", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load original T234 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T234B: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to overwrite T234B work: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T234B execution requires a clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        name: value
        for name, value in prereg.items()
        if name != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T234B_ABI_HELPER_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T234B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)

    original_path = Path(
        prereg["frozen_inputs"]["original_runner"]["path"]
    )
    module = load_original(original_path)
    WORK.mkdir(parents=True)
    module.abi = adapted_abi
    module.WORK = WORK / "graphs"
    module.OUTPUT = WORK / "inner_t234_result.json"
    module.MARKDOWN = WORK / "inner_t234_result.md"
    return_code = int(module.main())
    inner_path = module.OUTPUT
    if return_code != 0 or not inner_path.is_file():
        raise RuntimeError(
            f"T234B inner T234 failed: return_code={return_code}"
        )
    inner = json.loads(inner_path.read_text(encoding="utf-8"))
    checks = {
        "inner_t234_passed": (
            inner["status"] == "PASS_T234_EXACT_LOW_COMMAND_HEAD_ROUTE"
            and inner["decision"]
            == (
                "EARN_T235_EXACT_LOW_COMMAND_NOMINAL_MATRIX_"
                "PREREGISTRATION_ONLY"
            )
            and not inner["failed_checks"]
        ),
        "inner_original_contract_sha_exact": (
            inner["preregistered_contract_sha256"]
            == json.loads(
                Path(
                    prereg["frozen_inputs"]["original_preregistration"][
                        "path"
                    ]
                ).read_text(encoding="utf-8")
            )["preregistered_contract_sha256"]
        ),
        "adapter_only_recovery": True,
        "original_partial_still_exact": (
            receipt(
                Path(
                    prereg["frozen_inputs"]["partial_transform"]["path"]
                )
            )
            == prereg["frozen_inputs"]["partial_transform"]
        ),
        "no_behavior_training_hosted_robot": (
            inner["execution"]["behavior_cells"] == 0
            and inner["execution"]["optimizer_steps"] == 0
            and inner["execution"]["hosted_sessions"] == 0
            and inner["execution"]["robot_or_rdk_access"] == 0
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    passed = not failed
    result_basis = {
        "schema_version": "open_duck.t234b_abi_helper_recovery_result.v1",
        "status": (
            "PASS_T234B_ABI_HELPER_RECOVERY"
            if passed
            else "HOLD_T234B_ABI_HELPER_RECOVERY"
        ),
        "decision": (
            prereg["decision_rule"]["inner_t234_passes_exactly"]
            if passed
            else prereg["decision_rule"]["otherwise"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "inner_t234_result": receipt(inner_path),
        "inner_t234_result_sha256": inner["result_sha256"],
        "graphs": inner["graphs"],
        "recovery_kind": "Path_to_ModelProto_ABI_adapter_only",
        "execution": inner["execution"],
        "authority": {
            "nominal_behavior_preregistration": passed,
            "training": False,
            "hosted": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    result = {
        **result_basis,
        "result_sha256": canonical_sha256(result_basis),
    }
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T234B ABI-helper recovery result\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        "- Recovery: exact Path-to-ModelProto API adapter\n"
        f"- Random inference rows: "
        f"`{inner['execution']['random_inference_rows']}`\n"
        f"- Frozen trace rows: "
        f"`{inner['execution']['trace_inference_rows']}`\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
