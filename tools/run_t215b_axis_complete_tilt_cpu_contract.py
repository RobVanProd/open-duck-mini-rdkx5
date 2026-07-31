#!/usr/bin/env python3
"""Run T215B's default-off, enabled, and 1,024-step CPU contract."""

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


PREREG = ANALYSIS / "t215b_axis_complete_tilt_cpu_preregistration.json"
RESULT = ANALYSIS / "t215b_axis_complete_tilt_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "T215B_AXIS_COMPLETE_TILT_CPU_RESULT_20260730.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t215b_axis_complete_tilt_cpu_contract_v1"
)


def validate_prereg(value: dict[str, Any]) -> None:
    basis = dict(value)
    basis.pop("preregistered_contract_sha256", None)
    if (
        value.get("status")
        != "PREREGISTERED_T215B_AXIS_COMPLETE_TILT_CPU_CONTRACT"
        or value.get("failed_checks")
        or engine.t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T215B preregistration identity changed")
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
        raise RuntimeError("T215B composed playground changed")


def run_worker(
    *,
    mode: str,
    playground: Path,
    reference: Path,
    source_onnx: Path,
    output: Path,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(TOOLS / "run_t215b_environment_contract_worker.py"),
        "--mode",
        mode,
        "--playground",
        str(playground),
        "--reference",
        str(reference),
        "--output",
        str(output),
    ]
    if mode == "enabled":
        command.extend(
            [
                "--source-onnx",
                str(source_onnx),
                "--ticks",
                "108",
                "--seed",
                "215",
            ]
        )
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
        completed.stdout, encoding="utf-8", newline="\n"
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T215B {mode} worker failed\n{completed.stdout[-20000:]}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def training_command(
    *,
    playground: Path,
    output: Path,
    restore: Path,
    reference: Path,
    gate_asset: Path,
) -> list[str]:
    command = engine.t98.training_command(
        python=Path(sys.executable),
        playground=playground,
        output=output,
        reference=reference,
        restore=restore,
        gate_asset=gate_asset,
    )
    anchor = command.index("--winner_t98_hidden_expert_continuation") + 1
    command[anchor:anchor] = [
        "--winner_v127_constrained_cost",
        "--winner_t215b_axis_complete_tilt_cost",
    ]
    for flag in (
        "--ground_up_peak_torque_exceedance_scale",
        "--ground_up_linear_peak_torque_exceedance_scale",
    ):
        command[command.index(flag) + 1] = "0"
    return command


def finite_metric(
    events: dict[str, list[dict[str, float | int]]],
    tag: str,
) -> bool:
    mapped = {
        "eval/episode_cost/t209_predicted_roll_risk": (
            "eval/episode_cost/t215b_predicted_tilt_box"
        ),
    }.get(tag, tag)
    values = events.get(mapped, [])
    return bool(values) and all(
        math.isfinite(float(row["value"])) for row in values
    )


def transform_result(return_code: int) -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    value.pop("result_sha256", None)
    old_check = value["checks"].pop(
        "roll_cost_and_dual_metrics_finite"
    )
    value["checks"]["tilt_cost_and_dual_metrics_finite"] = old_check
    value["checks"]["exact_t215b_flag_scope"] = (
        value["training"]["command"].count(
            "--winner_t215b_axis_complete_tilt_cost"
        )
        == 1
        and "--winner_t209_dual_roll_cost"
        not in value["training"]["command"]
        and "--winner_t202_predicted_roll_risk"
        not in value["training"]["command"]
    )
    value["checks"]["both_axis_environment_contract_green"] = (
        value["environment_contract"]["checks"][
            "both_synthetic_axes_exceed_box"
        ]
        and value["environment_contract"]["checks"][
            "synthetic_dominant_axis_exact"
        ]
    )
    failed = sorted(
        name for name, passed in value["checks"].items() if not passed
    )
    passed = not failed and return_code == 0
    value["schema_version"] = (
        "open_duck.t215b_axis_complete_tilt_cpu_result.v1"
    )
    value["status"] = (
        "PASS_T215B_AXIS_COMPLETE_TILT_CPU_CONTRACT"
        if passed
        else "HOLD_T215B_AXIS_COMPLETE_TILT_CPU_CONTRACT"
    )
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    value["decision"] = (
        prereg["decision_rule"]["pass"]
        if passed
        else prereg["decision_rule"]["fail"]
    )
    value["failed_checks"] = failed
    value["mechanism"] = prereg["mechanism"]
    value["execution"]["formal_behavior_cells"] = 0
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
        "# T215B axis-complete tilt CPU result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
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
    engine.finite_metric = finite_metric
    return transform_result(engine.main())


if __name__ == "__main__":
    raise SystemExit(main())
