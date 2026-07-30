#!/usr/bin/env python3
"""Compose T227's command-atom source from the frozen T215B tree."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "training/t227_command_atom_bank.py"
TARGET_MODULE = "playground/common/t227_command_atom_bank.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"expected one replacement in {path}, found {count}: "
            f"{old[:100]!r}"
        )
    path.write_text(
        text.replace(old, new),
        encoding="utf-8",
        newline="\n",
    )


def file_inventory(root: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(root).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    base = args.base_root.resolve()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse T227 tree: {output}")
    base_manifest = base / "T215B_COMPOSED_SOURCE_MANIFEST.json"
    required = (
        base / "playground/open_duck_mini_v2/joystick.py",
        base / "playground/open_duck_mini_v2/runner.py",
        base / "playground/common/runner.py",
        base / "playground/common/t19_support_trainthrough.py",
        base / "playground/common/t66_endpoint_core_continuation.py",
    )
    if not base_manifest.is_file() or not all(
        path.is_file() for path in required
    ):
        raise FileNotFoundError("T227 frozen T215B base is incomplete")

    shutil.copytree(base, output)
    shutil.copy2(MODULE, output / TARGET_MODULE)

    joystick = output / "playground/open_duck_mini_v2/joystick.py"
    replace_once(
        joystick,
        """        ground_up_hard_vector_command_support=False,
        ground_up_command_support_range=[0.074, 0.080],
""",
        """        ground_up_hard_vector_command_support=False,
        ground_up_command_support_range=[0.074, 0.080],
        winner_t227_command_atom_bank=False,
""",
    )
    replace_once(
        joystick,
        """            forward = jp.where(
                self._config.ground_up_hard_vector_command_support,
                jax.random.uniform(
                    rng1,
                    minval=self._config.ground_up_command_support_range[0],
                    maxval=self._config.ground_up_command_support_range[1],
                ),
                self._config.nominal_reference_command_x,
            )
""",
        """            sampled_forward = jax.random.uniform(
                rng1,
                minval=self._config.ground_up_command_support_range[0],
                maxval=self._config.ground_up_command_support_range[1],
            )
            if self._config.winner_t227_command_atom_bank:
                from playground.common.t227_command_atom_bank import (
                    select_named_axis_forward,
                )

                sampled_forward = select_named_axis_forward(
                    sampled_forward
                )
            forward = jp.where(
                self._config.ground_up_hard_vector_command_support,
                sampled_forward,
                self._config.nominal_reference_command_x,
            )
""",
    )

    duck_runner = output / "playground/open_duck_mini_v2/runner.py"
    replace_once(
        duck_runner,
        """        self.env_config.ground_up_command_support_range = [
            args.ground_up_command_support_min_x,
            args.ground_up_command_support_max_x,
        ]
""",
        """        self.env_config.ground_up_command_support_range = [
            args.ground_up_command_support_min_x,
            args.ground_up_command_support_max_x,
        ]
        self.env_config.winner_t227_command_atom_bank = (
            args.winner_t227_command_atom_bank
        )
""",
    )
    replace_once(
        duck_runner,
        """        self.env_config.winner_v127_constrained_cost = (
            args.winner_v127_constrained_cost
        )
""",
        """        if args.winner_t227_command_atom_bank and not (
            args.winner_t215b_axis_complete_tilt_cost
            and args.winner_v127_constrained_cost
            and args.winner_t98_hidden_expert_continuation
            and args.winner_t19_support_trainthrough
            and args.winner_v3_variable_configuration
            and args.ground_up_hard_vector_command_support
            and args.ppo_num_envs % 32 == 0
        ):
            raise ValueError(
                "T227 requires T216's exact T215B/T98/T19/V3 "
                "continuation and a training population divisible by 32"
            )
        if args.winner_t227_command_atom_bank:
            from playground.common.t227_command_atom_bank import (
                training_readback,
            )

            print(training_readback(args.ppo_num_envs))
        self.env_config.winner_v127_constrained_cost = (
            args.winner_v127_constrained_cost
        )
""",
    )
    replace_once(
        duck_runner,
        """    parser.add_argument("--winner_v127_constrained_cost", action="store_true")
""",
        """    parser.add_argument("--winner_v127_constrained_cost", action="store_true")
    parser.add_argument(
        "--winner_t227_command_atom_bank",
        action="store_true",
    )
""",
    )

    common_runner = output / "playground/common/runner.py"
    replace_once(
        common_runner,
        """        if getattr(self.args, "winner_t19_support_trainthrough", False):
            from playground.common.t19_support_trainthrough import (
                wrap_for_brax_training,
            )

            wrap_env_fn = wrap_for_brax_training

        train_call = functools.partial(
""",
        """        if getattr(self.args, "winner_t19_support_trainthrough", False):
            from playground.common.t19_support_trainthrough import (
                wrap_for_brax_training,
            )

            wrap_env_fn = wrap_for_brax_training
        if getattr(self.args, "winner_t227_command_atom_bank", False):
            from playground.common.t227_command_atom_bank import (
                wrap_for_brax_training,
            )

            wrap_env_fn = wrap_for_brax_training

        train_call = functools.partial(
""",
    )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "py_compile",
            TARGET_MODULE,
            "playground/open_duck_mini_v2/joystick.py",
            "playground/open_duck_mini_v2/runner.py",
            "playground/common/runner.py",
        ],
        cwd=output,
        check=True,
    )
    inventory = file_inventory(output / "playground")
    manifest = {
        "schema_version": "open_duck.t227_composed_source.v1",
        "base": {
            "path": str(base),
            "manifest": str(base_manifest),
            "manifest_sha256": sha256(base_manifest),
            "required_file_sha256": {
                path.relative_to(base).as_posix(): sha256(path)
                for path in required
            },
        },
        "sources": {
            "composer": {
                "path": str(Path(__file__).resolve()),
                "sha256": sha256(Path(__file__).resolve()),
            },
            "command_atom_module": {
                "path": str(MODULE),
                "sha256": sha256(MODULE),
                "installed_as": TARGET_MODULE,
            },
        },
        "mechanism": {
            "configuration_strata": 8,
            "command_strata": [
                "broad_continuous",
                "exact_x_0p074",
                "exact_x_0p077",
                "exact_x_0p080",
            ],
            "cartesian_strata": 32,
            "configuration_randomizer_change": False,
            "command_support_change": True,
            "reward_change": False,
            "cost_change": False,
            "policy_abi_change": False,
            "deployment_graph_change": False,
            "x_zero_training_change": False,
        },
        "playground_inventory": inventory,
    }
    manifest_path = output / "T227_COMPOSED_SOURCE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "manifest": str(manifest_path),
                "manifest_sha256": sha256(manifest_path),
                "python_files": sum(
                    key.endswith(".py") for key in inventory
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
