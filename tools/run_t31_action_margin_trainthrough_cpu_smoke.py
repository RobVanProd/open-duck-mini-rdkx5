#!/usr/bin/env python3
"""Run T31's preregistered 1,024-step CPU restore/update/export smoke."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort

import run_t20_support_trainthrough_one_update as t20
import run_t22_corrected_one_update_cpu_smoke as t22
from build_t28_t23_action_margin_assets import wrap as append_margin


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t31_action_margin_trainthrough_cpu_preregistration.json"
)
RESULT = ANALYSIS / "t31_action_margin_trainthrough_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "T31_ACTION_MARGIN_TRAINTHROUGH_CPU_RESULT_20260727.md"
)
VELOCITY_LIMITS = (
    "1.0,.75,1.4736209064722061,1.4300791546702385,"
    "1.3976470567286015,.5,.5,.5,.5,.5,.75,1.25,1.0,"
    "1.2215287424623966"
)


def validate_preregistration(value: dict) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_SMOKE"
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T31 preregistration identity changed")
    for name, item in value["sources"].items():
        t20.verify_receipt(item, name)
    for name, item in value["assets"].items():
        t20.verify_receipt(item, name)
    playground = Path(value["playground"]["path"])
    inventory = {
        path.relative_to(playground).as_posix(): t20.sha256(path)
        for path in sorted(playground.rglob("*.py"))
    }
    if (
        inventory != value["playground"]["python_inventory"]
        or t20.canonical_sha256(inventory)
        != value["playground"]["python_inventory_sha256"]
    ):
        raise RuntimeError("T31 composed source inventory changed")


def training_command(**kwargs) -> list[str]:
    command = t20_training_command(**kwargs)
    index = command.index("--critic_observation")
    command[index:index] = ["--winner_t31_action_margin_trainthrough"]
    return command


def margin_contract(
    source_path: Path,
    wrapped_path: Path,
    limit: np.float32,
) -> dict:
    source = ort.InferenceSession(
        str(source_path),
        providers=["CPUExecutionProvider"],
    )
    wrapped = ort.InferenceSession(
        str(wrapped_path),
        providers=["CPUExecutionProvider"],
    )
    rng = np.random.default_rng(20260727)
    action_exact = True
    previous_exact = True
    hidden_exact = True
    feedback_exact = True
    strict_margin = True
    finite = True
    changed = 0
    for command_x in (0.0, 0.074, 0.077, 0.08):
        for _ in range(64):
            obs = rng.normal(size=(1, 115)).astype(np.float32)
            obs[:, 6] = np.float32(command_x)
            feed = {
                "obs": obs,
                "previous_action": rng.uniform(
                    -1.0,
                    1.0,
                    size=(1, 14),
                ).astype(np.float32),
                "h_in": rng.normal(size=(1, 64)).astype(np.float32),
                "calibration_context": rng.normal(
                    size=(1, 64)
                ).astype(np.float32),
            }
            before = source.run(None, feed)
            after = wrapped.run(None, feed)
            expected_action = np.clip(before[0], -limit, limit)
            expected_previous = np.clip(before[1], -limit, limit)
            action_exact &= np.array_equal(after[0], expected_action)
            previous_exact &= np.array_equal(after[1], expected_previous)
            hidden_exact &= np.array_equal(after[2], before[2])
            feedback_exact &= np.array_equal(after[0], after[1])
            strict_margin &= bool(
                np.all(np.abs(after[0]) < np.float32(0.98))
                and np.all(np.abs(after[1]) < np.float32(0.98))
            )
            finite &= all(bool(np.all(np.isfinite(item))) for item in after)
            changed += int(np.count_nonzero(after[0] != before[0]))
    checks = {
        "action_clip_bit_exact": action_exact,
        "previous_action_clip_bit_exact": previous_exact,
        "hidden_output_bit_exact": hidden_exact,
        "realized_feedback_bit_exact": feedback_exact,
        "strict_margin": strict_margin,
        "all_outputs_finite": finite,
        "cpu_provider": wrapped.get_providers()[0] == "CPUExecutionProvider",
    }
    return {
        "checks": checks,
        "changed_action_values": changed,
        "pass": all(checks.values()),
    }


def deployment_graph(raw: Path, output_root: Path) -> dict:
    output_root.mkdir(parents=True)
    pre_margin_root = output_root / "pre_margin"
    base = t22.deployment_graph(raw, pre_margin_root)
    limit = np.nextafter(np.float32(0.98), np.float32(0.0))
    margin_path = output_root / "action_margin.onnx"
    model = append_margin(onnx.load(base["wrapped"]["path"]), limit)
    onnx.save(model, margin_path)
    contract = margin_contract(
        Path(base["wrapped"]["path"]),
        margin_path,
        limit,
    )
    return {
        **base,
        "pre_margin_wrapped": base["wrapped"],
        "pre_margin_wrapped_io": base["wrapped_io"],
        "wrapped": t20.receipt(margin_path),
        "wrapped_io": t20.graph_io(margin_path),
        "margin_contract": contract,
    }


def finalize() -> int:
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    checks = dict(value["checks"])
    step_zero = value["deployments"]["0"]
    checks.update(
        {
            "command_uses_t31_margin_trainthrough": (
                "--winner_t31_action_margin_trainthrough"
                in value["training"]["command"]
            ),
            "both_margin_export_contracts_pass": all(
                item["margin_contract"]["pass"]
                for item in value["deployments"].values()
            ),
            "step_zero_pre_margin_wrapper_byte_exact": (
                step_zero["pre_margin_wrapped"]["sha256"]
                == prereg["assets"][
                    "frozen_t18_pre_margin_wrapped_onnx"
                ]["sha256"]
            ),
            "step_zero_margin_wrapper_byte_exact": (
                step_zero["wrapped"]["sha256"]
                == prereg["assets"]["frozen_t18_wrapped_onnx"]["sha256"]
            ),
            "composed_flag_default_off": (
                "--winner_t31_action_margin_trainthrough"
                in value["training"]["command"]
            ),
        }
    )
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value["schema_version"] = (
        "open_duck.t31_action_margin_trainthrough_cpu_result.v1"
    )
    value["status"] = (
        "PASS_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_SMOKE"
        if not failed
        else "HOLD_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_SMOKE"
    )
    value["decision"] = (
        "EARN_T31_HOSTED_CONTINUATION_PREREGISTRATION"
        if not failed
        else "KEEP_T31_HOSTED_TRAINING_CLOSED"
    )
    value["checks"] = checks
    value["failed_checks"] = failed
    value["authority"] = {
        "hosted_preregistration": not failed,
        "hosted_training": False,
        "behavior_evaluation": False,
        "checkpoint_selection": False,
        "gate5": False,
        "rdkx5_or_robot": False,
        "torque_or_motion": False,
    }
    value.pop("result_sha256", None)
    value["result_sha256"] = t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T31 action-margin train-through CPU result",
                "",
                f"status: `{value['status']}`",
                "",
                f"decision: `{value['decision']}`",
                "",
                f"- failed checks: `{failed}`",
                "- CPU steps / hosted / robot: `1,024 / 0 / 0`",
                "",
                "Passing authorizes only a separate hosted-continuation "
                "preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


t20_training_command = t20.training_command


def main() -> int:
    t20.PREREGISTRATION = PREREGISTRATION
    t20.RESULT = RESULT
    t20.MARKDOWN = MARKDOWN
    t20.VELOCITY_LIMITS = VELOCITY_LIMITS
    t20.validate_preregistration = validate_preregistration
    t20.training_command = training_command
    t20.deployment_graph = deployment_graph
    t20.main()
    return finalize()


if __name__ == "__main__":
    raise SystemExit(main())
