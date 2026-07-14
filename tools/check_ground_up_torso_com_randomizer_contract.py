#!/usr/bin/env python3
"""Contract the corrected, targeted torso-COM training randomizer on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    root = args.playground_root.resolve()
    sys.path.insert(0, str(root))
    old_cwd = Path.cwd()
    os.chdir(root)
    try:
        import jax
        from playground.common import randomize
        from playground.open_duck_mini_v2 import joystick

        env = joystick.Joystick(
            task="flat_terrain_backlash",
            config=joystick.default_config(),
            config_overrides={
                "push_config.enable": False,
                "noise_config.level": 0.0,
                "noise_config.action_min_delay": 0,
                "noise_config.action_max_delay": 1,
                "noise_config.imu_min_delay": 0,
                "noise_config.imu_max_delay": 1,
            },
        )
    finally:
        os.chdir(old_cwd)

    model = env.mjx_model
    torso_name = "trunk_assembly"
    torso_id = int(env.mj_model.body(torso_name).id)
    torso_mass = float(env.mj_model.body_mass[torso_id])
    base_name = env.mj_model.body(1).name
    base_mass = float(env.mj_model.body_mass[1])
    sample_count = 4096
    keys = jax.random.split(jax.random.PRNGKey(20260714), sample_count)

    def sample(distribution: str):
        fn = randomize.make_ground_up_torso_com_x_randomizer(
            torso_id, -0.05, 0.05, distribution
        )
        updated, in_axes = fn(model, keys)
        body_ipos = np.asarray(updated.body_ipos)
        baseline = np.asarray(model.body_ipos)
        offsets = body_ipos[:, torso_id, 0] - baseline[torso_id, 0]
        mask = np.ones(body_ipos.shape[1:], dtype=bool)
        mask[torso_id, 0] = False
        other_exact = np.array_equal(
            body_ipos[:, mask], np.broadcast_to(baseline[mask], body_ipos[:, mask].shape)
        )
        return offsets, other_exact, in_axes

    uniform, uniform_other_exact, uniform_in_axes = sample("uniform")
    anchors, anchors_other_exact, anchors_in_axes = sample("anchors")
    anchor_targets = np.asarray([-0.05, 0.0, 0.05], dtype=np.float32)
    anchor_nearest = np.min(np.abs(anchors[:, None] - anchor_targets[None, :]), axis=1)
    anchor_counts = {
        f"{float(value):.2f}": int(np.sum(np.isclose(anchors, value, rtol=0.0, atol=1e-7)))
        for value in anchor_targets
    }

    default_keys = jax.random.split(jax.random.PRNGKey(20260715), 512)
    default_model, _ = randomize.domain_randomize(model, default_keys)
    default_body_ipos = np.asarray(default_model.body_ipos)
    default_body_mass = np.asarray(default_model.body_mass)
    baseline_ipos = np.asarray(model.body_ipos)

    runner_source = (root / "playground/open_duck_mini_v2/runner.py").read_text()
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and os.environ["CUDA_VISIBLE_DEVICES"] == ""
            and os.environ["JAX_PLATFORMS"] == "cpu"
        ),
        "compiled_body_schema_exact": (
            base_name == "base"
            and base_mass == 0.0
            and torso_name == "trunk_assembly"
            and torso_id == 2
            and torso_mass > 0.0
            and randomize.TORSO_BODY_ID == torso_id
        ),
        "runner_resolves_and_checks_named_massive_torso": all(
            token in runner_source
            for token in (
                'torso_body_name = "trunk_assembly"',
                "self.env.mj_model.body(torso_body_name).id",
                "torso_body_mass <= 0.0",
                "make_ground_up_torso_com_x_randomizer",
            )
        ),
        "targeted_randomizer_preserves_nominal_bootstrap_controls": (
            "if args.ground_up_torso_com_randomization:" in runner_source
            and "None if args.nominal_reference_bootstrap else randomize.domain_randomize"
            in runner_source
        ),
        "uniform_exactly_one_field_axis": bool(uniform_other_exact),
        "uniform_range_and_support": (
            uniform.shape == (sample_count,)
            and float(np.min(uniform)) >= -0.05 - 1e-7
            and float(np.max(uniform)) <= 0.05 + 1e-7
            and float(np.min(uniform)) < -0.049
            and float(np.max(uniform)) > 0.049
            and abs(float(np.mean(uniform))) < 0.002
        ),
        "uniform_in_axes_exact": uniform_in_axes.body_ipos == 0,
        "anchors_exactly_one_field_axis": bool(anchors_other_exact),
        "anchors_values_and_coverage_exact": (
            float(np.max(anchor_nearest)) <= 1e-7
            and all(count > 0 for count in anchor_counts.values())
        ),
        "anchors_in_axes_exact": anchors_in_axes.body_ipos == 0,
        "default_randomizer_targets_torso_not_massless_base": (
            np.array_equal(
                default_body_ipos[:, 1],
                np.broadcast_to(baseline_ipos[1], default_body_ipos[:, 1].shape),
            )
            and not np.array_equal(
                default_body_ipos[:, torso_id],
                np.broadcast_to(
                    baseline_ipos[torso_id], default_body_ipos[:, torso_id].shape
                ),
            )
            and np.all(default_body_mass[:, 1] == 0.0)
            and np.any(default_body_mass[:, torso_id] != torso_mass)
        ),
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_GROUND_UP_TORSO_COM_RANDOMIZER_CONTRACT"
        if not failed
        else "FAIL_GROUND_UP_TORSO_COM_RANDOMIZER_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_randomizer_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "compiled_bodies": {
            "outer_base": {"id": 1, "name": base_name, "mass_kg": base_mass},
            "torso": {"id": torso_id, "name": torso_name, "mass_kg": torso_mass},
        },
        "uniform": {
            "samples": sample_count,
            "min_m": float(np.min(uniform)),
            "max_m": float(np.max(uniform)),
            "mean_m": float(np.mean(uniform)),
            "other_body_ipos_entries_exact": bool(uniform_other_exact),
        },
        "anchors": {
            "samples": sample_count,
            "counts": anchor_counts,
            "max_distance_to_declared_anchor_m": float(np.max(anchor_nearest)),
            "other_body_ipos_entries_exact": bool(anchors_other_exact),
        },
        "inputs": {
            "patch": {"path": str(args.patch.resolve()), "sha256": sha256(args.patch)},
            "randomize_py": {
                "path": str(root / "playground/common/randomize.py"),
                "sha256": sha256(root / "playground/common/randomize.py"),
            },
            "runner_py": {
                "path": str(root / "playground/open_duck_mini_v2/runner.py"),
                "sha256": sha256(root / "playground/open_duck_mini_v2/runner.py"),
            },
        },
        "authority": {
            "preregister_torso_com_training_search": not failed,
            "hosted_training_before_preregistration": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Torso-COM Randomizer Contract",
        "",
        f"status: `{status}`",
        "",
        *(f"- {name}: `{passed}`" for name, passed in checks.items()),
        "",
        f"Uniform 4,096-sample support: `{float(np.min(uniform)):.8f}` to "
        f"`{float(np.max(uniform)):.8f} m`, mean `{float(np.mean(uniform)):.8f} m`.",
        f"Anchor counts: `{anchor_counts}`.",
        "",
        "Passing authorizes only preregistration of a targeted torso-COM training search. It does not authorize hosted compute, later robustness stages, local GPU, RDK-X5, or robot access.",
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
