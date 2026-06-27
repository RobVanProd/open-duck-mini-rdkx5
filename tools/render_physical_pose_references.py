#!/usr/bin/env python3
"""Render repo-defined Open Duck Mini zero/home pose references.

The soft-offset script asks the operator to place each joint at the "desired
zero position", but the local repo only defines that reference numerically.
This tool renders the MJCF at all-zero joints and at the runtime/sim home
keyframe so the calibration check has concrete reference images.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XML = (
    ROOT.parent
    / "Open_Duck_Playground"
    / "playground"
    / "open_duck_mini_v2"
    / "xmls"
    / "scene_flat_terrain.xml"
)
DEFAULT_OUTPUT = ROOT / "outputs" / "analysis" / "physical_pose_references"

JOINT_ORDER = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]

HOME = np.array(
    [
        0.002,
        0.053,
        -0.630,
        1.368,
        -0.784,
        0.0,
        0.0,
        0.0,
        0.0,
        -0.003,
        -0.065,
        0.635,
        1.379,
        -0.796,
    ],
    dtype=float,
)

VIEWS = {
    "front": (0.0, -20.0),
    "rear": (180.0, -20.0),
    "left": (90.0, -20.0),
    "right": (-90.0, -20.0),
    "oblique": (45.0, -22.0),
}


def set_pose(model: mujoco.MjModel, data: mujoco.MjData, joints: np.ndarray) -> None:
    data.qpos[:] = 0.0
    data.qvel[:] = 0.0
    data.ctrl[:] = joints
    data.qpos[0:7] = np.array([0.0, 0.0, 0.15, 1.0, 0.0, 0.0, 0.0])
    data.qpos[7 : 7 + len(joints)] = joints
    mujoco.mj_forward(model, data)


def render_view(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    pose_name: str,
    view_name: str,
    azimuth: float,
    elevation: float,
    width: int,
    height: int,
) -> Image.Image:
    renderer = mujoco.Renderer(model, width=width, height=height)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = np.array([0.0, 0.0, 0.08])
    cam.distance = 0.62
    cam.azimuth = azimuth
    cam.elevation = elevation
    renderer.update_scene(data, camera=cam)
    image = Image.fromarray(renderer.render())
    renderer.close()

    draw = ImageDraw.Draw(image)
    label = f"{pose_name} - {view_name}"
    draw.rectangle((8, 8, 8 + 8 * len(label), 30), fill=(255, 255, 255))
    draw.text((12, 12), label, fill=(0, 0, 0))
    return image


def write_contact_sheet(images: list[tuple[str, Image.Image]], output: Path) -> None:
    if not images:
        return
    width, height = images[0][1].size
    sheet = Image.new("RGB", (width * 2, height * math.ceil(len(images) / 2)), "white")
    for idx, (_, image) in enumerate(images):
        x = (idx % 2) * width
        y = (idx // 2) * height
        sheet.paste(image.convert("RGB"), (x, y))
    sheet.save(output)


def write_markdown(output_dir: Path, xml_path: Path) -> None:
    lines = [
        "# Physical Pose Reference Renders",
        "",
        f"source_xml: `{xml_path}`",
        "",
        "These images are generated from the repo MJCF, not from a photo or video.",
        "",
        "## Poses",
        "",
        "- `zero`: all 14 actuator joints at `0.0 rad`; this is the reference used by `find_soft_offsets.py`.",
        "- `home`: runtime `HWI.init_pos`; this matches the sim `scene_flat_terrain.xml` `home` keyframe.",
        "",
        "## Joint Order",
        "",
        "| index | joint | zero rad | home rad | home deg |",
        "|---:|---|---:|---:|---:|",
    ]
    for idx, (joint, home) in enumerate(zip(JOINT_ORDER, HOME)):
        lines.append(f"| {idx} | `{joint}` | 0.000 | {home:.3f} | {math.degrees(home):.1f} |")
    lines.extend(
        [
            "",
            "## Images",
            "",
            "| pose | contact sheet |",
            "|---|---|",
            "| zero | `zero_contact_sheet.png` |",
            "| home | `home_contact_sheet.png` |",
            "",
            "Use these references to decide whether the robot's current home pose and",
            "the operator-selected zero pose match the repo coordinate system before",
            "editing `duck_config.json` offsets.",
        ]
    )
    (output_dir / "README.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", type=Path, default=DEFAULT_XML)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model = mujoco.MjModel.from_xml_path(str(args.xml))
    data = mujoco.MjData(model)

    for pose_name, joints in {"zero": np.zeros(14), "home": HOME}.items():
        set_pose(model, data, joints)
        images: list[tuple[str, Image.Image]] = []
        for view_name, (azimuth, elevation) in VIEWS.items():
            image = render_view(
                model,
                data,
                pose_name,
                view_name,
                azimuth,
                elevation,
                args.width,
                args.height,
            )
            path = args.output_dir / f"{pose_name}_{view_name}.png"
            image.save(path)
            images.append((view_name, image))
        write_contact_sheet(images, args.output_dir / f"{pose_name}_contact_sheet.png")

    write_markdown(args.output_dir, args.xml)
    print(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
