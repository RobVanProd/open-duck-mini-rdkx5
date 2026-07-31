#!/usr/bin/env python3
"""Compose the default-off T10 response-conditioned V121 training source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import py_compile
import shutil
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NETWORK_SOURCE = (
    ROOT / "patches" / "t10_response_conditioned_v121_networks.py"
)
WRAPPER_SOURCE = (
    ROOT / "patches" / "t10_command_aware_response_wrapper.py"
)
BASE_MANIFEST = "WINNER_V173_COMPOSED_SOURCE_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def replace_once(
    source: str,
    before: str,
    after: str,
    *,
    label: str,
) -> str:
    count = source.count(before)
    if count != 1:
        raise RuntimeError(
            f"T10 composition {label} expected one match, observed {count}"
        )
    return source.replace(before, after, 1)


def patch_robot_runner(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    replacements = [
        (
            """        if args.policy_architecture in (
            "recurrent",
            "reference_residual_recurrent_adapter",
            "response_conditioned_reference_residual",
        ):
""",
            """        if args.policy_architecture in (
            "recurrent",
            "reference_residual_recurrent_adapter",
            "response_conditioned_reference_residual",
            "response_conditioned_v121",
        ):
""",
            "hidden architecture tuple",
        ),
        (
            """                "reference_residual_recurrent_adapter",
                "response_conditioned_reference_residual",
            ):
""",
            """                "reference_residual_recurrent_adapter",
                "response_conditioned_reference_residual",
                "response_conditioned_v121",
            ):
""",
            "winner-v3 architecture tuple",
        ),
        (
            """        if args.policy_architecture == "response_conditioned_reference_residual":
""",
            """        if args.policy_architecture == "response_conditioned_v121":
            from playground.common.t10_command_aware_response_wrapper import (
                wrap_command_aware_response,
            )

            if not args.winner_v3_variable_configuration:
                raise ValueError(
                    "T10 response conditioning requires variable configuration"
                )
            if not args.winner_v119_train_transition_match:
                raise ValueError(
                    "T10 requires the exact V119/V121 train transition"
                )
            if args.recurrent_hidden_size != 64:
                raise ValueError("T10 hidden/context width must remain 64")
            if args.t10_response_calibrator_path is None:
                raise ValueError("T10 response calibrator path is required")
            self.env = wrap_command_aware_response(
                self.env,
                args.t10_response_calibrator_path,
                calibration_ticks=args.t10_response_calibration_ticks,
                home_return_ticks=args.t10_response_home_return_ticks,
                zero_command_bypass=args.t10_command_aware_zero_bypass,
            )
            self.eval_env = wrap_command_aware_response(
                self.eval_env,
                args.t10_response_calibrator_path,
                calibration_ticks=args.t10_response_calibration_ticks,
                home_return_ticks=args.t10_response_home_return_ticks,
                zero_command_bypass=args.t10_command_aware_zero_bypass,
            )
        if args.policy_architecture == "response_conditioned_reference_residual":
""",
            "T10 environment wrapper",
        ),
        (
            """            "reference_residual_recurrent_adapter",
            "response_conditioned_reference_residual",
        ],
""",
            """            "reference_residual_recurrent_adapter",
            "response_conditioned_reference_residual",
            "response_conditioned_v121",
        ],
""",
            "CLI architecture choice",
        ),
        (
            """    parser.add_argument("--winner_v98_home_return_ticks", type=int, default=250)
""",
            """    parser.add_argument("--winner_v98_home_return_ticks", type=int, default=250)
    parser.add_argument("--t10_response_calibrator_path", default=None)
    parser.add_argument("--t10_response_calibration_ticks", type=int, default=250)
    parser.add_argument("--t10_response_home_return_ticks", type=int, default=0)
    parser.add_argument(
        "--t10_command_aware_zero_bypass",
        action="store_true",
    )
""",
            "T10 CLI arguments",
        ),
    ]
    for before, after, label in replacements:
        source = replace_once(source, before, after, label=label)
    path.write_text(source, encoding="utf-8", newline="\n")
    return len(replacements)


def patch_common_runner(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    replacements = [
        (
            """        elif self.args.policy_architecture == "response_conditioned_reference_residual":
            from playground.common.winner_v98_response_conditioned_export import (
""",
            """        elif self.args.policy_architecture == "response_conditioned_v121":
            from playground.common.t10_response_conditioned_v121_networks import (
                export_response_conditioned_v121_onnx,
            )

            export_response_conditioned_v121_onnx(
                params,
                self.action_size,
                self.obs_size,
                self.args.recurrent_hidden_size,
                onnx_export_path,
                self.ppo_params.network_factory.policy_hidden_layer_sizes,
                action_velocity_limits_rad_s=(
                    self.env_config.ground_up_action_velocity_limits_rad_s
                ),
                control_dt=float(self.env.dt),
                action_scale=float(self.env_config.action_scale),
            )
        elif self.args.policy_architecture == "response_conditioned_reference_residual":
            from playground.common.winner_v98_response_conditioned_export import (
""",
            "T10 exporter branch",
        ),
        (
            """            elif self.args.policy_architecture == "response_conditioned_reference_residual":
                from playground.common.winner_v98_response_conditioned_ppo_networks import (
""",
            """            elif self.args.policy_architecture == "response_conditioned_v121":
                from playground.common.t10_response_conditioned_v121_networks import (
                    install_response_conditioned_v121_collector_hooks,
                    make_response_conditioned_v121_ppo_networks,
                )

                install_response_conditioned_v121_collector_hooks()
                network_builder = functools.partial(
                    make_response_conditioned_v121_ppo_networks,
                    recurrent_hidden_size=self.args.recurrent_hidden_size,
                )
            elif self.args.policy_architecture == "response_conditioned_reference_residual":
                from playground.common.winner_v98_response_conditioned_ppo_networks import (
""",
            "T10 network branch",
        ),
    ]
    for before, after, label in replacements:
        source = replace_once(source, before, after, label=label)
    path.write_text(source, encoding="utf-8", newline="\n")
    return len(replacements)


def ignore_copy(_path: str, names: list[str]) -> set[str]:
    blocked = {
        ".git",
        ".tmp",
        "__pycache__",
        ".pytest_cache",
        "checkpoints",
    }
    return {name for name in names if name in blocked}


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T10 composition requires --execute")
    base = args.base_root.resolve()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse T10 source: {output}")
    if not (base / BASE_MANIFEST).is_file():
        raise FileNotFoundError(base / BASE_MANIFEST)
    shutil.copytree(base, output, ignore=ignore_copy)

    common = output / "playground" / "common"
    network_target = (
        common / "t10_response_conditioned_v121_networks.py"
    )
    wrapper_target = (
        common / "t10_command_aware_response_wrapper.py"
    )
    shutil.copy2(NETWORK_SOURCE, network_target)
    shutil.copy2(WRAPPER_SOURCE, wrapper_target)
    robot_runner = (
        output / "playground" / "open_duck_mini_v2" / "runner.py"
    )
    common_runner = output / "playground" / "common" / "runner.py"
    patch_count = (
        patch_robot_runner(robot_runner)
        + patch_common_runner(common_runner)
    )
    for path in (
        network_target,
        wrapper_target,
        robot_runner,
        common_runner,
    ):
        py_compile.compile(str(path), doraise=True)

    basis = {
        "schema_version": "open_duck.t10_composed_source.v1",
        "base": {
            "path": str(base),
            "manifest": receipt(base / BASE_MANIFEST),
        },
        "repository_sources": {
            "composer": receipt(Path(__file__)),
            "network": receipt(NETWORK_SOURCE),
            "wrapper": receipt(WRAPPER_SOURCE),
        },
        "composition": {
            "patch_count": patch_count,
            "default_off": (
                "new response_conditioned_v121 architecture and its wrapper "
                "are inactive unless explicitly selected"
            ),
        },
        "final_sources": {
            "network": receipt(network_target),
            "wrapper": receipt(wrapper_target),
            "robot_runner": receipt(robot_runner),
            "common_runner": receipt(common_runner),
        },
        "execution": {
            "optimizer_steps": 0,
            "simulator_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
    }
    manifest = {
        **basis,
        "manifest_sha256": canonical_sha256(basis),
    }
    manifest_path = output / "T10_COMPOSED_SOURCE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(
            manifest,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("PASS_T10_COMPOSED_SOURCE")
    print(f"output={output}")
    print(f"manifest={manifest_path}")
    print(f"manifest_sha256={manifest['manifest_sha256']}")
    print(f"file_sha256={sha256(manifest_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
