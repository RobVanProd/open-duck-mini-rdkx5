#!/usr/bin/env python3
"""Compose T119 from the frozen T112 Playground with a trainable soft router."""

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
BASE = Path("D:/CodexProjects/Open_Duck_Playground-t112-always-on-expert-v1")
DEFAULT_OUTPUT = Path(
    "D:/CodexProjects/Open_Duck_Playground-t119-joint-soft-router-v1"
)
SOURCE_NETWORK = ROOT / "patches" / "t112_always_on_hidden_expert_ppo_networks.py"
SOURCE_RUNNER = ROOT / "patches" / "t112_open_duck_mini_v2_runner.py"
UPDATE_MASK = ROOT / "patches" / "t119_joint_soft_router_updates.py"


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


def replace_exact(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"T119 {label} replacement count changed: {count}")
    return text.replace(old, new)


def build_network_source() -> str:
    text = SOURCE_NETWORK.read_text(encoding="utf-8")
    text = replace_exact(
        text,
        '"""T98 recurrent adapter with a fixed live-hidden negative-COM expert gate."""',
        '"""T119 recurrent adapter with a jointly trainable soft expert router."""',
        "docstring",
    )
    dense = """        negative_adapter_location = linen.Dense(
            self.action_size,
            kernel_init=jax.nn.initializers.zeros,
            bias_init=jax.nn.initializers.zeros,
            name="negative_adapter_location",
        )(hidden_out)
"""
    expanded_dense = dense + """        soft_router_coefficient_delta = self.param(
            "soft_router_coefficient_delta",
            jax.nn.initializers.zeros,
            (self.recurrent_hidden_size,),
        )
        soft_router_intercept_delta = self.param(
            "soft_router_intercept_delta",
            jax.nn.initializers.zeros,
            (1,),
        )
"""
    text = replace_exact(
        text, dense, expanded_dense, "router parameter insertion"
    )
    old_gate = """        gate_score = jnp.sum(
            (
                (hidden_out - jnp.asarray(self.gate_mean))
                / jnp.asarray(self.gate_scale)
            )
            * jnp.asarray(self.gate_coefficient),
            axis=-1,
            keepdims=True,
        ) + jnp.asarray(self.gate_intercept)
        negative_com_gate = jax.lax.stop_gradient(gate_score >= 0.0)
        # T112 keeps the exact T98 parameter topology but removes routing:
        # every frozen endpoint-bank stratum constrains the same residual.
        conditional_location = negative_adapter_location
"""
    new_gate = """        gate_score = jnp.sum(
            (
                (hidden_out - jnp.asarray(self.gate_mean))
                / jnp.asarray(self.gate_scale)
            )
            * (
                jnp.asarray(self.gate_coefficient)
                + soft_router_coefficient_delta
            ),
            axis=-1,
            keepdims=True,
        ) + jnp.asarray(self.gate_intercept) + soft_router_intercept_delta
        soft_negative_com_weight = jax.nn.sigmoid(gate_score)
        conditional_location = (
            negative_adapter_location * soft_negative_com_weight
        )
"""
    text = replace_exact(text, old_gate, new_gate, "JAX soft router")
    old_initializers = """        numpy_helper.from_array(np.asarray(gate["coefficient"], np.float32).reshape(64, 1), name="hidden_gate_coefficient"),
        numpy_helper.from_array(np.asarray([gate["intercept"]], np.float32), name="hidden_gate_intercept"),
"""
    new_initializers = """        numpy_helper.from_array(
            (
                np.asarray(gate["coefficient"], np.float32)
                + np.asarray(p["soft_router_coefficient_delta"], np.float32)
            ).reshape(64, 1),
            name="hidden_gate_coefficient",
        ),
        numpy_helper.from_array(
            (
                np.asarray([gate["intercept"]], np.float32)
                + np.asarray(p["soft_router_intercept_delta"], np.float32)
            ),
            name="hidden_gate_intercept",
        ),
"""
    text = replace_exact(
        text, old_initializers, new_initializers, "ONNX router initializers"
    )
    old_nodes = """        helper.make_node("GreaterOrEqual", ["hidden_gate_score", "hidden_gate_zero"], ["negative_com_gate"]),
        helper.make_node("Gemm", ["h_out", "negative_adapter_weight", "negative_adapter_bias"], ["negative_adapter_location"]),
        helper.make_node("Identity", ["negative_adapter_location"], ["conditional_adapter_location"]),
"""
    new_nodes = """        helper.make_node("Sigmoid", ["hidden_gate_score"], ["soft_negative_com_weight"]),
        helper.make_node("Gemm", ["h_out", "negative_adapter_weight", "negative_adapter_bias"], ["negative_adapter_location"]),
        helper.make_node("Mul", ["negative_adapter_location", "soft_negative_com_weight"], ["conditional_adapter_location"]),
"""
    text = replace_exact(text, old_nodes, new_nodes, "ONNX soft router")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse T119 Playground: {output}")
    for path in (BASE, SOURCE_NETWORK, SOURCE_RUNNER, UPDATE_MASK):
        if not path.exists():
            raise FileNotFoundError(path)
    shutil.copytree(BASE, output)
    network_path = (
        output / "playground/common/t98_hidden_expert_ppo_networks.py"
    )
    network_path.write_text(
        build_network_source(), encoding="utf-8", newline="\n"
    )
    mask_path = output / "playground/common/t98_hidden_expert_continuation.py"
    shutil.copy2(UPDATE_MASK, mask_path)
    runner_text = SOURCE_RUNNER.read_text(encoding="utf-8")
    runner_text = replace_exact(
        runner_text,
        '"gate=always_on,"\n'
        '                        "actor_updates=negative_adapter_location_only"',
        '"gate=joint_soft,"\n'
        '                        "actor_updates=negative_adapter_location_plus_soft_router"',
        "runner readback",
    )
    runner_path = output / "playground/open_duck_mini_v2/runner.py"
    runner_path.write_text(runner_text, encoding="utf-8", newline="\n")
    compile_paths = [
        network_path,
        mask_path,
        runner_path,
        output / "playground/common/runner.py",
    ]
    subprocess.run(
        [sys.executable, "-m", "py_compile", *map(str, compile_paths)],
        cwd=output,
        check=True,
    )
    inventory = {
        path.relative_to(output).as_posix(): sha256(path)
        for path in sorted(output.rglob("*.py"))
    }
    value = {
        "schema_version": "open_duck.t119_composed_playground.v1",
        "base": str(BASE.resolve()),
        "output": str(output),
        "inputs": {
            "composer": sha256(Path(__file__)),
            "source_network": sha256(SOURCE_NETWORK),
            "source_runner": sha256(SOURCE_RUNNER),
            "update_mask": sha256(UPDATE_MASK),
        },
        "generated": {
            "network": sha256(network_path),
            "runner": sha256(runner_path),
            "update_mask": sha256(mask_path),
        },
        "python_inventory": inventory,
    }
    value["manifest_sha256"] = canonical_sha256(value)
    manifest = output / "T119_COMPOSED_SOURCE_MANIFEST.json"
    manifest.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "manifest": str(manifest),
                "manifest_sha256": value["manifest_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
