#!/usr/bin/env python3
"""Run T37's preregistered frozen-normalizer CPU training smoke."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jax
import numpy as np
from orbax import checkpoint as ocp

import run_t31_action_margin_trainthrough_cpu_smoke as t31
import run_t20_support_trainthrough_one_update as t20


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t37_frozen_normalizer_cpu_preregistration.json"
)
RESULT = ANALYSIS / "t37_frozen_normalizer_cpu_result.json"
MARKDOWN = ANALYSIS / "T37_FROZEN_NORMALIZER_CPU_RESULT_20260727.md"
FREEZE_FLAG = "--winner_t37_freeze_observation_normalizer"


def _path_name(path: Any) -> str:
    if hasattr(path, "key"):
        return str(path.key)
    if hasattr(path, "idx"):
        return str(path.idx)
    return str(path)


def normalizer_manifest(normalizer: Any) -> dict[str, Any]:
    """Return a stable, value-sensitive manifest for every normalizer leaf."""
    rows: dict[str, Any] = {}
    for path, leaf in jax.tree_util.tree_flatten_with_path(normalizer)[0]:
        value = np.asarray(leaf)
        name = "/".join(_path_name(item) for item in path)
        rows[name] = {
            "dtype": str(value.dtype),
            "shape": list(value.shape),
            "sha256": hashlib.sha256(value.tobytes()).hexdigest(),
        }
        if value.ndim == 0:
            rows[name]["value"] = value.item()
    payload = json.dumps(
        rows,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return {
        "leaves": rows,
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def uint64_count(manifest: dict[str, Any]) -> int:
    leaves = manifest["leaves"]
    hi = int(leaves["count/hi"]["value"])
    lo = int(leaves["count/lo"]["value"])
    return hi * (2**32) + lo


def checkpoint_normalizer(path: Path) -> Any:
    tree = ocp.PyTreeCheckpointer().restore(str(path))
    return tree[0]


def validate_preregistration(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T37_FROZEN_NORMALIZER_CPU_SMOKE"
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T37 preregistration identity changed")
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
        raise RuntimeError("T37 composed source inventory changed")


def training_command(**kwargs: Any) -> list[str]:
    command = t31_training_command(**kwargs)
    index = command.index("--critic_observation")
    command[index:index] = [FREEZE_FLAG]
    return command


def finalize() -> int:
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    initial_path = Path(value["training"]["initial_checkpoint"]["path"])
    final_path = Path(value["training"]["final_checkpoint"]["path"])
    initial = normalizer_manifest(checkpoint_normalizer(initial_path))
    final = normalizer_manifest(checkpoint_normalizer(final_path))
    expected = prereg["normalizer_contract"]["source_manifest"]
    expected_count = prereg["normalizer_contract"]["source_count"]

    checks = dict(value["checks"])
    checks.update(
        {
            "command_uses_t37_freeze": (
                FREEZE_FLAG in value["training"]["command"]
            ),
            "command_keeps_t31_margin_trainthrough": (
                "--winner_t31_action_margin_trainthrough"
                in value["training"]["command"]
            ),
            "initial_normalizer_exact_source": initial == expected,
            "final_normalizer_bit_exact_initial": final == initial,
            "initial_normalizer_count_exact": (
                uint64_count(initial) == expected_count
            ),
            "final_normalizer_count_exact": (
                uint64_count(final) == expected_count
            ),
            "observation_normalization_remains_enabled": (
                prereg["normalizer_contract"]["normalization_enabled"]
            ),
            "welford_cutoff_not_misused": (
                prereg["normalizer_contract"]["freeze_mechanism"]
                == "temporary_identity_update_context"
            ),
        }
    )
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value["schema_version"] = (
        "open_duck.t37_frozen_normalizer_cpu_result.v1"
    )
    value["status"] = (
        "PASS_T37_FROZEN_NORMALIZER_CPU_SMOKE"
        if not failed
        else "HOLD_T37_FROZEN_NORMALIZER_CPU_SMOKE"
    )
    value["decision"] = (
        "EARN_T38_FROZEN_NORMALIZER_HOSTED_PREREGISTRATION"
        if not failed
        else "KEEP_T37_HOSTED_TRAINING_CLOSED"
    )
    value["checks"] = checks
    value["failed_checks"] = failed
    value["normalizer_contract"] = {
        "expected_source": expected,
        "initial": initial,
        "final": final,
        "expected_count": expected_count,
        "initial_count": uint64_count(initial),
        "final_count": uint64_count(final),
        "all_leaves_bit_exact_after_update": final == initial,
    }
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
                "# T37 frozen-normalizer CPU result",
                "",
                f"status: `{value['status']}`",
                "",
                f"decision: `{value['decision']}`",
                "",
                f"- failed checks: `{failed}`",
                f"- frozen observation count: `{expected_count}`",
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
    print(f"normalizer_sha256={final['sha256']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


t31_training_command = t31.training_command


def main() -> int:
    t31.PREREGISTRATION = PREREGISTRATION
    t31.RESULT = RESULT
    t31.MARKDOWN = MARKDOWN
    t31.validate_preregistration = validate_preregistration
    t31.training_command = training_command
    t31.main()
    return finalize()


if __name__ == "__main__":
    raise SystemExit(main())
