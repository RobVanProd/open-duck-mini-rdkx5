#!/usr/bin/env python3
"""Audit Open Duck Playground reset support/contact distribution.

This is an offline sim diagnostic. It does not train, touch the robot, SSH, or
deploy anything. Imports for JAX/MuJoCo/Playground stay inside runtime code so
normal py_compile and --help do not require the training environment.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Iterable, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"


@contextlib.contextmanager
def temporary_cwd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def parse_seeds(raw: str) -> list[int]:
    seeds: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            seeds.extend(range(int(start), int(end) + 1))
        else:
            seeds.append(int(part))
    return sorted(dict.fromkeys(seeds))


def percentile(values: Sequence[float], pct: float) -> float | None:
    data = sorted(
        float(value)
        for value in values
        if value is not None and not (math.isnan(float(value)) or math.isinf(float(value)))
    )
    if not data:
        return None
    if len(data) == 1:
        return data[0]
    k = (len(data) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return data[lo]
    return data[lo] * (hi - k) + data[hi] * (k - lo)


def stats(values: Iterable[float]) -> dict[str, float | None]:
    data = [
        float(value)
        for value in values
        if value is not None and not (math.isnan(float(value)) or math.isinf(float(value)))
    ]
    if not data:
        return {"count": 0, "mean": None, "min": None, "p50": None, "p95": None, "max": None}
    arr = np.asarray(data, dtype=float)
    return {
        "count": int(arr.size),
        "mean": float(np.mean(arr)),
        "min": float(np.min(arr)),
        "p50": percentile(data, 50),
        "p95": percentile(data, 95),
        "max": float(np.max(arr)),
    }


def write_scaled_hfield_scene(source_xml: Path, z_scale: float) -> Path:
    text = source_xml.read_text()
    pattern = re.compile(r'(<hfield\b[^>]*\bsize=")([^"]+)(")')
    match = pattern.search(text)
    if not match:
        raise ValueError(f"no hfield size attribute found in {source_xml}")
    values = match.group(2).split()
    if len(values) != 4:
        raise ValueError(f"expected four hfield size values in {source_xml}: {values}")
    values[2] = f"{float(z_scale):.8g}"
    scaled_text = text[: match.start(2)] + " ".join(values) + text[match.end(2) :]
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=f"_hfield_z{float(z_scale):.8g}.xml",
        prefix=".codex_reset_audit_",
        dir=source_xml.parent,
        delete=False,
    )
    with tmp:
        tmp.write(scaled_text)
    return Path(tmp.name)


def support_label(contact: Sequence[bool]) -> str:
    left, right = bool(contact[0]), bool(contact[1])
    if left and right:
        return "double"
    if left:
        return "left"
    if right:
        return "right"
    return "none"


def audit_resets(args: argparse.Namespace) -> dict[str, Any]:
    os.environ.setdefault("JAX_PLATFORM_NAME", args.jax_platform)
    sys.path.insert(0, str(args.playground_path))

    import jax  # noqa: PLC0415
    import jax.numpy as jp  # noqa: PLC0415
    from mujoco_playground._src.collision import geoms_colliding  # noqa: PLC0415
    from playground.open_duck_mini_v2 import constants as duck_constants  # noqa: PLC0415
    from playground.open_duck_mini_v2 import joystick  # noqa: PLC0415

    seeds = parse_seeds(args.seeds)
    temp_scene_xml: Path | None = None
    original_task_to_xml = duck_constants.task_to_xml
    rows: list[dict[str, Any]] = []
    try:
        with temporary_cwd(args.playground_path):
            cfg = joystick.default_config()
            overrides = {
                "push_config.enable": False,
                "noise_config.level": 0.0,
                "noise_config.action_min_delay": 0,
                "noise_config.action_max_delay": 1,
                "noise_config.imu_min_delay": 0,
                "noise_config.imu_max_delay": 1,
                "lin_vel_x": [args.command_x, args.command_x],
                "lin_vel_y": [0.0, 0.0],
                "ang_vel_yaw": [0.0, 0.0],
                "neck_pitch_range": [0.0, 0.0],
                "head_pitch_range": [0.0, 0.0],
                "head_yaw_range": [0.0, 0.0],
                "head_roll_range": [0.0, 0.0],
            }
            terrain_override = {
                "enabled": False,
                "hfield_z_scale": None,
                "source_xml": None,
                "temp_xml": None,
            }
            if args.terrain_hfield_z_scale is not None:
                source_xml = Path(original_task_to_xml(args.task))
                temp_scene_xml = write_scaled_hfield_scene(
                    source_xml, float(args.terrain_hfield_z_scale)
                )
                terrain_override = {
                    "enabled": True,
                    "hfield_z_scale": float(args.terrain_hfield_z_scale),
                    "source_xml": str(source_xml),
                    "temp_xml": str(temp_scene_xml),
                }

                def task_to_xml_override(task_name: str):
                    if task_name == args.task:
                        return temp_scene_xml
                    return original_task_to_xml(task_name)

                duck_constants.task_to_xml = task_to_xml_override

            env = joystick.Joystick(task=args.task, config=cfg, config_overrides=overrides)
            home_qpos = np.asarray(jax.device_get(env._init_q), dtype=float)
            home_actuator = np.asarray(
                jax.device_get(env.get_actuator_joints_qpos(env._init_q)), dtype=float
            )
            joint_names = [
                env._mj_model.actuator(index).name for index in range(int(env.action_size))
            ]
            if len(joint_names) != int(env.action_size) or any(
                not name for name in joint_names
            ):
                joint_names = [f"joint_{index}" for index in range(int(env.action_size))]

            for seed in seeds:
                state = env.reset(jax.random.PRNGKey(seed))
                state = jax.device_get(state)
                data = state.data
                contact = [
                    bool(geoms_colliding(data, geom_id, env._floor_geom_id))
                    for geom_id in env._feet_geom_id
                ]
                qpos = np.asarray(data.qpos, dtype=float)
                qvel = np.asarray(data.qvel, dtype=float)
                actuator_qpos = np.asarray(
                    jax.device_get(env.get_actuator_joints_qpos(data.qpos)), dtype=float
                )
                foot_pos = np.asarray(data.site_xpos[env._feet_site_id], dtype=float)
                actuator_delta = actuator_qpos - home_actuator
                base_addr = int(env._floating_base_qpos_addr)
                qvel_addr = int(env._floating_base_qvel_addr)
                rows.append(
                    {
                        "seed": int(seed),
                        "support": support_label(contact),
                        "contact": [bool(item) for item in contact],
                        "base_x_m": float(qpos[base_addr]),
                        "base_y_m": float(qpos[base_addr + 1]),
                        "base_height_m": float(qpos[base_addr + 2]),
                        "base_qvel_norm": float(np.linalg.norm(qvel[qvel_addr : qvel_addr + 6])),
                        "foot_z_m": foot_pos[:, 2].astype(float).tolist(),
                        "foot_z_min_m": float(np.min(foot_pos[:, 2])),
                        "foot_z_max_m": float(np.max(foot_pos[:, 2])),
                        "foot_z_delta_m": float(abs(foot_pos[0, 2] - foot_pos[1, 2])),
                        "actuator_delta_l2_rad": float(np.linalg.norm(actuator_delta)),
                        "actuator_delta_max_abs_rad": float(np.max(np.abs(actuator_delta))),
                        "actuator_delta_rad": {
                            name: float(value) for name, value in zip(joint_names, actuator_delta)
                        },
                    }
                )
    finally:
        duck_constants.task_to_xml = original_task_to_xml
        if temp_scene_xml is not None:
            with contextlib.suppress(OSError):
                temp_scene_xml.unlink()

    support_counts: dict[str, int] = {"none": 0, "left": 0, "right": 0, "double": 0}
    for row in rows:
        support_counts[row["support"]] += 1

    status = "PASS_RESET_DISTRIBUTION_AUDIT"
    if support_counts["none"] > 0:
        status = "HOLD_RESET_DISTRIBUTION_CONTAINS_NO_CONTACT_STARTS"
    elif support_counts["left"] + support_counts["right"] > 0:
        status = "WARN_RESET_DISTRIBUTION_CONTAINS_SINGLE_CONTACT_STARTS"

    seed5 = next((row for row in rows if row["seed"] == 5), None)
    payload: dict[str, Any] = {
        "status": status,
        "playground_path": str(args.playground_path),
        "task": args.task,
        "terrain_hfield_z_scale": args.terrain_hfield_z_scale,
        "command_x": args.command_x,
        "jax_backend": jax.default_backend(),
        "jax_devices": [str(device) for device in jax.devices()],
        "seeds": seeds,
        "support_counts": support_counts,
        "support_percent": {
            key: (100.0 * value / len(rows) if rows else 0.0)
            for key, value in support_counts.items()
        },
        "base_height_stats_m": stats(row["base_height_m"] for row in rows),
        "base_qvel_norm_stats": stats(row["base_qvel_norm"] for row in rows),
        "foot_z_min_stats_m": stats(row["foot_z_min_m"] for row in rows),
        "foot_z_max_stats_m": stats(row["foot_z_max_m"] for row in rows),
        "foot_z_delta_stats_m": stats(row["foot_z_delta_m"] for row in rows),
        "actuator_delta_l2_stats_rad": stats(row["actuator_delta_l2_rad"] for row in rows),
        "actuator_delta_max_abs_stats_rad": stats(
            row["actuator_delta_max_abs_rad"] for row in rows
        ),
        "seed5": seed5,
        "rows": rows,
        "reset_implementation": {
            "base_xy_uniform_m": [-0.05, 0.05],
            "yaw_uniform_rad": [-3.14, 3.14],
            "actuator_qpos_multiplier": [0.5, 1.5],
            "base_qvel_uniform": [-0.05, 0.05],
            "ctrl_initialized_to_actuator_qpos": True,
            "source": "Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py reset()",
        },
        "interpretation": (
            "No-contact reset starts are outside the standing support manifold and should "
            "be treated as a reset-distribution issue unless the real robot start protocol "
            "can produce the same unsupported state."
        ),
    }
    return payload


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return "NA"
        return f"{value:.{digits}f}"
    return str(value)


def write_markdown(payload: dict[str, Any], output: Path) -> None:
    lines = [
        "# Playground Reset Distribution Audit",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline reset/support diagnostic. It does not SSH, deploy,",
        "train, run robot tests, or change runtime behavior.",
        "",
        "## Config",
        "",
        f"- playground_path: `{payload['playground_path']}`",
        f"- task: `{payload['task']}`",
        f"- terrain_hfield_z_scale: `{payload['terrain_hfield_z_scale']}`",
        f"- command_x: `{payload['command_x']}`",
        f"- seeds: `{payload['seeds']}`",
        f"- jax_backend: `{payload['jax_backend']}`",
        f"- jax_devices: `{payload['jax_devices']}`",
        "",
        "## Reset Implementation",
        "",
    ]
    for key, value in payload["reset_implementation"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Support Counts",
            "",
            "| support | count | percent |",
            "|---|---:|---:|",
        ]
    )
    for key in ("none", "left", "right", "double"):
        lines.append(
            f"| `{key}` | {payload['support_counts'][key]} | "
            f"{fmt(payload['support_percent'][key])} |"
        )
    lines.extend(
        [
            "",
            "## Distribution Stats",
            "",
            "| metric | mean | min | p50 | p95 | max |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for label, key in [
        ("base_height_m", "base_height_stats_m"),
        ("base_qvel_norm", "base_qvel_norm_stats"),
        ("foot_z_min_m", "foot_z_min_stats_m"),
        ("foot_z_max_m", "foot_z_max_stats_m"),
        ("foot_z_delta_m", "foot_z_delta_stats_m"),
        ("actuator_delta_l2_rad", "actuator_delta_l2_stats_rad"),
        ("actuator_delta_max_abs_rad", "actuator_delta_max_abs_stats_rad"),
    ]:
        item = payload[key]
        lines.append(
            f"| `{label}` | {fmt(item.get('mean'))} | {fmt(item.get('min'))} | "
            f"{fmt(item.get('p50'))} | {fmt(item.get('p95'))} | {fmt(item.get('max'))} |"
        )
    lines.extend(
        [
            "",
            "## Per-Seed Reset State",
            "",
            "| seed | support | contact | base_h | foot_z | foot_z_delta | qpos_l2 | qpos_max_abs |",
            "|---:|---|---|---:|---|---:|---:|---:|",
        ]
    )
    for row in payload["rows"]:
        lines.append(
            f"| {row['seed']} | `{row['support']}` | `{row['contact']}` | "
            f"{fmt(row['base_height_m'])} | `{[round(x, 4) for x in row['foot_z_m']]}` | "
            f"{fmt(row['foot_z_delta_m'])} | {fmt(row['actuator_delta_l2_rad'])} | "
            f"{fmt(row['actuator_delta_max_abs_rad'])} |"
        )
    if payload.get("seed5") is not None:
        row = payload["seed5"]
        lines.extend(
            [
                "",
                "## Seed 5 Detail",
                "",
                f"- support: `{row['support']}`",
                f"- contact: `{row['contact']}`",
                f"- base_height_m: `{fmt(row['base_height_m'])}`",
                f"- foot_z_m: `{[round(x, 4) for x in row['foot_z_m']]}`",
                f"- actuator_delta_l2_rad: `{fmt(row['actuator_delta_l2_rad'])}`",
                f"- actuator_delta_max_abs_rad: `{fmt(row['actuator_delta_max_abs_rad'])}`",
                "",
                "Largest actuator deltas from home:",
                "",
                "| joint | delta_rad |",
                "|---|---:|",
            ]
        )
        deltas = sorted(
            row["actuator_delta_rad"].items(), key=lambda item: abs(float(item[1])), reverse=True
        )
        for name, value in deltas[:8]:
            lines.append(f"| `{name}` | {fmt(value)} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            payload["interpretation"],
            "",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", type=Path, default=DEFAULT_PLAYGROUND)
    parser.add_argument("--task", default="rough_terrain_backlash")
    parser.add_argument("--terrain-hfield-z-scale", type=float, default=None)
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--seeds", default="0-31")
    parser.add_argument("--jax-platform", choices=["cpu", "gpu"], default="cpu")
    parser.add_argument(
        "--output-md",
        type=Path,
        default=ROOT / "outputs/analysis/PLAYGROUND_RESET_DISTRIBUTION_AUDIT.md",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=ROOT / "outputs/analysis/playground_reset_distribution_audit.json",
    )
    args = parser.parse_args()
    args.playground_path = args.playground_path.expanduser().resolve()

    payload = audit_resets(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, args.output_md)
    print(f"status={payload['status']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
