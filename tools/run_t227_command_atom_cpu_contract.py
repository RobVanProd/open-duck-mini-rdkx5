#!/usr/bin/env python3
"""Run T227's environment and 1,024-step CPU training contract."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t209_dual_roll_cost_cpu_contract as engine  # noqa: E402
import run_t215b_axis_complete_tilt_cpu_contract as t215b  # noqa: E402


PREREG = ANALYSIS / "t227_command_atom_cpu_preregistration.json"
RESULT = ANALYSIS / "t227_command_atom_cpu_result.json"
MARKDOWN = ANALYSIS / "T227_COMMAND_ATOM_CPU_RESULT_20260730.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227_command_atom_cpu_contract_v1"
)


def validate_prereg(value: dict[str, Any]) -> None:
    basis = dict(value)
    basis.pop("preregistered_contract_sha256", None)
    if (
        value.get("status")
        != "PREREGISTERED_T227_COMMAND_ATOM_CPU_CONTRACT"
        or value.get("failed_checks")
        or engine.t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T227 preregistration identity changed")
    for name, item in value["sources"].items():
        engine.t20.verify_receipt(item, name)
    for name, item in value["assets"].items():
        engine.t20.verify_receipt(item, name)
    playground = Path(value["playground"]["path"])
    inventory = {
        path.relative_to(playground).as_posix(): engine.t20.sha256(path)
        for path in sorted(playground.rglob("*.py"))
    }
    if (
        inventory != value["playground"]["python_inventory"]
        or engine.t20.canonical_sha256(inventory)
        != value["playground"]["python_inventory_sha256"]
    ):
        raise RuntimeError("T227 composed playground changed")


def replace_argument(command: list[str], name: str, value: str) -> None:
    index = command.index(name)
    command[index + 1] = value


def training_command(
    *,
    playground: Path,
    output: Path,
    restore: Path,
    reference: Path,
    gate_asset: Path,
) -> list[str]:
    command = t215b.training_command(
        playground=playground,
        output=output,
        restore=restore,
        reference=reference,
        gate_asset=gate_asset,
    )
    replace_argument(command, "--ppo_num_envs", "32")
    replace_argument(command, "--ppo_batch_size", "32")
    anchor = command.index(
        "--winner_t215b_axis_complete_tilt_cost"
    ) + 1
    command.insert(anchor, "--winner_t227_command_atom_bank")
    return command


def run_worker(
    *,
    mode: str,
    playground: Path,
    reference: Path,
    source_onnx: Path,
    output: Path,
) -> dict[str, Any]:
    if mode == "default_off":
        return t215b.run_worker(
            mode=mode,
            playground=playground,
            reference=reference,
            source_onnx=source_onnx,
            output=output,
        )
    command = [
        sys.executable,
        str(TOOLS / "run_t227_command_atom_environment_worker.py"),
        "--playground",
        str(playground),
        "--reference",
        str(reference),
        "--output",
        str(output),
        "--seed",
        "227",
    ]
    completed = subprocess.run(
        command,
        cwd=playground,
        env=engine.cpu_environment(playground),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )
    output.with_suffix(".log").write_text(
        completed.stdout,
        encoding="utf-8",
        newline="\n",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "T227 environment worker failed\n"
            f"{completed.stdout[-20000:]}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def transform_result(return_code: int) -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    value.pop("result_sha256", None)
    old_head = value["checks"].pop(
        "only_t203_negative_adapter_head_changes"
    )
    value["checks"]["only_t216_negative_adapter_head_changes"] = old_head
    value["checks"]["exact_t227_flag_scope"] = (
        value["training"]["command"].count(
            "--winner_t227_command_atom_bank"
        )
        == 1
        and value["training"]["command"].count(
            "--winner_t215b_axis_complete_tilt_cost"
        )
        == 1
        and value["training"]["command"][
            value["training"]["command"].index("--ppo_num_envs") + 1
        ]
        == "32"
        and value["training"]["command"][
            value["training"]["command"].index("--ppo_batch_size") + 1
        ]
        == "32"
    )
    environment = value["environment_contract"]
    value["checks"]["exact_32_cell_cartesian_reset_green"] = (
        environment["status"]
        == "PASS_T227_COMMAND_ATOM_ENVIRONMENT_CONTRACT"
        and environment["failed_checks"] == []
        and environment["checks"][
            "all_32_cartesian_pairs_present_once"
        ]
        and environment["checks"][
            "exact_command_atoms_survive_t19_reset_and_resample"
        ]
    )
    value["checks"]["t215b_cost_and_dual_metrics_finite"] = (
        value["checks"].pop("roll_cost_and_dual_metrics_finite")
    )
    failed = sorted(
        name for name, passed in value["checks"].items() if not passed
    )
    passed = not failed and return_code == 0
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    value["schema_version"] = "open_duck.t227_command_atom_cpu_result.v1"
    value["status"] = (
        "PASS_T227_COMMAND_ATOM_CPU_CONTRACT"
        if passed
        else "HOLD_T227_COMMAND_ATOM_CPU_CONTRACT"
    )
    value["decision"] = (
        prereg["decision_rule"]["pass"]
        if passed
        else prereg["decision_rule"]["fail"]
    )
    value["failed_checks"] = failed
    value["mechanism"] = prereg["mechanism"]
    value["execution"]["formal_behavior_cells"] = 0
    value["execution"]["hosted_compute_units"] = 0
    value["execution"]["robot_or_rdk_access"] = 0
    value["authority"]["hosted_preregistration"] = passed
    value["authority"]["hosted_training"] = False
    value["authority"]["gate5"] = False
    value["result_sha256"] = engine.t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    final_aux = value["training"]["aux"]["1024"]
    MARKDOWN.write_text(
        "# T227 command-atom CPU result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Cartesian reset: 32/32 configuration-command pairs\n"
        f"- Final dual lambda / eta: "
        f"`{final_aux['lambda']}` / `{final_aux['eta']}`\n"
        "- Optimizer / formal behavior / hosted / robot: "
        "`1024 / 0 / 0 / 0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


def main() -> int:
    engine.PREREG = PREREG
    engine.RESULT = RESULT
    engine.MARKDOWN = MARKDOWN
    engine.WORK = WORK
    engine.validate_prereg = validate_prereg
    engine.run_worker = run_worker
    engine.training_command = training_command
    engine.finite_metric = t215b.finite_metric
    return transform_result(engine.main())


if __name__ == "__main__":
    raise SystemExit(main())
