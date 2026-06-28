#!/usr/bin/env python3
"""Audit Phase 2 domain-randomization readiness.

This is an offline-only static audit. It does not train, import JAX, touch the
robot, SSH, deploy, or modify Playground. It answers whether the current local
Open Duck Playground already exposes the randomization hooks needed for the
Phase 2 robustness plan and whether the Phase 1 candidate is available in a
trainable warm-start form.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_POLICY = (
    ROOT
    / "policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx"
)
DEFAULT_POLICY_NPZ = (
    ROOT
    / "outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz"
)
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT / "outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint"
)
DEFAULT_WARMSTART_FIDELITY = (
    ROOT / "outputs/analysis/ppo_bc_command_conditioned_rate175_step0_export_fidelity.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_DOMAIN_RANDOMIZATION_AUDIT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_domain_randomization_audit.json"


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def has_all(text: str, needles: list[str]) -> bool:
    return all(needle in text for needle in needles)


def first_match(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else None


def match_groups(text: str, pattern: str) -> list[str] | None:
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return [group.strip() for group in match.groups()] if match else None


def file_info(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "sha256": sha256(path),
    }


def warmstart_fidelity_status(path: Path) -> dict[str, Any]:
    info = file_info(path)
    info["status"] = "MISSING"
    if not path.exists():
        return info
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        info["status"] = "INVALID_JSON"
        info["error"] = str(exc)
        return info
    info["report_status"] = payload.get("status")
    info["p95_abs_error"] = payload.get("fidelity", {}).get("p95_abs_error")
    info["max_abs_error"] = payload.get("fidelity", {}).get("max_abs_error")
    info["reference_onnx"] = payload.get("reference_onnx")
    info["output_checkpoint"] = payload.get("output_checkpoint")
    info["status"] = (
        "PASS"
        if payload.get("status") == "PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY"
        else "HOLD"
    )
    return info


def audit(args: argparse.Namespace) -> dict[str, Any]:
    playground = Path(args.playground_path)
    common_randomize = playground / "playground/common/randomize.py"
    joystick = playground / "playground/open_duck_mini_v2/joystick.py"
    runner = playground / "playground/open_duck_mini_v2/runner.py"
    common_runner = playground / "playground/common/runner.py"
    constants = playground / "playground/open_duck_mini_v2/constants.py"
    flat_xml = playground / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    rough_xml = playground / "playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml"

    randomize_text = read(common_randomize)
    joystick_text = read(joystick)
    runner_text = read(runner)
    common_runner_text = read(common_runner)
    constants_text = read(constants)
    flat_xml_text = read(flat_xml)
    rough_xml_text = read(rough_xml)

    policy = Path(args.policy)
    candidate_npz = Path(args.candidate_npz)
    restore_checkpoint = Path(args.restore_checkpoint) if args.restore_checkpoint else None
    warmstart_fidelity = Path(args.warmstart_fidelity)
    fidelity = warmstart_fidelity_status(warmstart_fidelity)
    checkpoint_present = restore_checkpoint is not None and restore_checkpoint.exists()
    fidelity_pass = fidelity.get("status") == "PASS"

    hooks: dict[str, dict[str, Any]] = {
        "friction_randomization": {
            "status": "PRESENT" if "geom_friction" in randomize_text else "MISSING",
            "evidence": "playground/common/randomize.py mutates model.geom_friction",
            "current_range": match_groups(
                randomize_text,
                r"geom_friction.*?jax\.random\.uniform\([^)]*?minval=([0-9.]+), maxval=([0-9.]+)",
            ),
        },
        "mass_randomization": {
            "status": "PRESENT" if "body_mass" in randomize_text else "MISSING",
            "evidence": "playground/common/randomize.py mutates model.body_mass",
        },
        "com_randomization": {
            "status": "PRESENT" if "body_ipos" in randomize_text else "MISSING",
            "evidence": "playground/common/randomize.py jitters torso body_ipos",
        },
        "actuator_gain_randomization": {
            "status": (
                "PRESENT"
                if has_all(randomize_text, ["actuator_gainprm", "actuator_biasprm"])
                else "MISSING"
            ),
            "evidence": "playground/common/randomize.py scales actuator gains/bias",
        },
        "frictionloss_armature_randomization": {
            "status": (
                "PRESENT"
                if has_all(randomize_text, ["dof_frictionloss", "dof_armature"])
                else "MISSING"
            ),
            "evidence": "playground/common/randomize.py scales dof frictionloss and armature",
        },
        "observation_noise": {
            "status": (
                "PRESENT"
                if has_all(joystick_text, ["noise_config", "scales", "accelerometer", "gyro"])
                else "MISSING"
            ),
            "evidence": "joystick.py default_config and _get_obs add joint/IMU noise",
        },
        "action_delay": {
            "status": (
                "PRESENT"
                if has_all(joystick_text, ["action_min_delay", "action_max_delay", "action_history"])
                else "MISSING"
            ),
            "evidence": "joystick.py samples delayed action from action_history",
        },
        "imu_delay": {
            "status": (
                "PRESENT"
                if has_all(joystick_text, ["imu_min_delay", "imu_max_delay", "imu_history"])
                else "MISSING"
            ),
            "evidence": "joystick.py samples delayed IMU/gravity history",
        },
        "push_perturbations": {
            "status": (
                "PRESENT"
                if has_all(joystick_text, ["push_config", "push_interval_steps", "push_magnitude"])
                else "MISSING"
            ),
            "evidence": "joystick.py adds random planar velocity impulse to floating base qvel",
        },
        "rough_terrain": {
            "status": (
                "PRESENT"
                if "rough_terrain_backlash" in constants_text and "hfield" in rough_xml_text
                else "MISSING"
            ),
            "evidence": "constants.py maps rough_terrain_backlash and XML contains hfield",
        },
        "actuator_bridge": {
            "status": (
                "PRESENT"
                if has_all(joystick_text, ["actuator_bridge", "_apply_actuator_bridge"])
                and "--enable_actuator_bridge" in runner_text
                else "MISSING"
            ),
            "evidence": "joystick.py bridge model and runner.py bridge CLI flags",
        },
        "domain_randomize_training_hook": {
            "status": (
                "PRESENT"
                if "randomization_fn=self.randomizer" in common_runner_text
                and (
                    "randomize.domain_randomize" in runner_text
                    or "randomize.make_domain_randomizer" in runner_text
                )
                else "MISSING"
            ),
            "evidence": "BaseRunner passes configured randomization_fn into Brax PPO train",
        },
        "leg_geometry_randomization": {
            "status": "PRESENT"
            if has_all(randomize_text, ["leg_geometry_jitter_scale", "body_pos"])
            and "--dr_leg_geometry_jitter_scale" in runner_text
            else "MISSING",
            "evidence": (
                "playground/common/randomize.py supports default-off leg body_pos "
                "scale jitter and runner.py exposes --dr_leg_geometry_jitter_scale"
            ),
        },
        "dr_range_cli": {
            "status": "PRESENT"
            if has_all(
                runner_text,
                [
                    "--dr_friction_min",
                    "--dr_mass_scale_min",
                    "--dr_com_jitter_m",
                    "--push_magnitude_min",
                    "--noise_hip_pos",
                ],
            )
            else "PARTIAL",
            "evidence": (
                "runner.py exposes staged DR range CLI for friction, mass, COM, "
                "push, noise, actuator gain, qpos jitter, and leg geometry"
            ),
        },
    }

    trainable_warmstart = {
        "required_by_phase2": True,
        "policy_onnx": file_info(policy),
        "candidate_mlp_npz": file_info(candidate_npz),
        "restore_checkpoint": file_info(restore_checkpoint) if restore_checkpoint else None,
        "warmstart_fidelity": fidelity,
        "status": "PASS_TRAINABLE_CHECKPOINT_PRESENT"
        if checkpoint_present and fidelity_pass
        else "HOLD_TRAINABLE_WARMSTART_CHECKPOINT_MISSING",
        "reason": (
            "A verified PPO step-0 Orbax checkpoint exists for the Phase 1 rate175 "
            "candidate. The fidelity report proves the exported checkpoint policy "
            "matches the packaged ONNX at action level before PPO updates."
            if checkpoint_present and fidelity_pass
            else "Current Playground PPO warm-start path uses --restore_checkpoint_path "
            "for an Orbax checkpoint. The Phase 1 deployable artifact must be "
            "converted or recovered as a trainable checkpoint before Phase 2."
        ),
    }

    blockers = []
    warnings = []
    if trainable_warmstart["status"].startswith("HOLD"):
        blockers.append(trainable_warmstart["status"])
    if hooks["leg_geometry_randomization"]["status"] == "MISSING":
        warnings.append("WARN_LEG_GEOMETRY_JITTER_NOT_IMPLEMENTED")
    if hooks["dr_range_cli"]["status"] == "PARTIAL":
        warnings.append("WARN_DR_RANGES_NOT_CLI_CONFIGURABLE")

    return {
        "status": "HOLD_PHASE2_NOT_READY" if blockers else "PASS_PHASE2_READY_TO_DRY_RUN",
        "playground_path": str(playground),
        "files": {
            "common_randomize": str(common_randomize),
            "joystick": str(joystick),
            "runner": str(runner),
            "common_runner": str(common_runner),
            "constants": str(constants),
            "flat_xml": str(flat_xml),
            "rough_xml": str(rough_xml),
        },
        "hooks": hooks,
        "trainable_warmstart": trainable_warmstart,
        "blockers": blockers,
        "warnings": warnings,
        "flat_floor_friction_xml": first_match(flat_xml_text, r'name="floor"[^>]*friction="([^"]+)"'),
        "rough_floor_friction_xml": first_match(rough_xml_text, r'name="floor"[^>]*friction="([^"]+)"'),
    }


def write_markdown(result: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Domain Randomization Audit",
        "",
        f"status: `{result['status']}`",
        f"playground_path: `{result['playground_path']}`",
        "",
        "This is an offline static audit. It did not train, SSH, deploy, or move the robot.",
        "",
        "## Existing Hooks",
        "",
        "| hook | status | evidence |",
        "|---|---|---|",
    ]
    for name, item in result["hooks"].items():
        lines.append(f"| `{name}` | `{item['status']}` | {item['evidence']} |")
    lines.extend(
        [
            "",
            "## Warm-Start Gate",
            "",
            f"status: `{result['trainable_warmstart']['status']}`",
            "",
            result["trainable_warmstart"]["reason"],
            "",
            "Artifacts:",
            "",
            f"- ONNX: `{result['trainable_warmstart']['policy_onnx']['path']}`",
            f"- ONNX exists: `{result['trainable_warmstart']['policy_onnx']['exists']}`",
            f"- ONNX sha256: `{result['trainable_warmstart']['policy_onnx']['sha256']}`",
            f"- BC MLP NPZ: `{result['trainable_warmstart']['candidate_mlp_npz']['path']}`",
            f"- BC MLP NPZ exists: `{result['trainable_warmstart']['candidate_mlp_npz']['exists']}`",
            f"- BC MLP NPZ sha256: `{result['trainable_warmstart']['candidate_mlp_npz']['sha256']}`",
            f"- restore checkpoint: `{result['trainable_warmstart']['restore_checkpoint']['path'] if result['trainable_warmstart']['restore_checkpoint'] else None}`",
            f"- restore checkpoint exists: `{result['trainable_warmstart']['restore_checkpoint']['exists'] if result['trainable_warmstart']['restore_checkpoint'] else None}`",
            f"- warm-start fidelity status: `{result['trainable_warmstart']['warmstart_fidelity'].get('report_status')}`",
            f"- warm-start fidelity p95 abs error: `{result['trainable_warmstart']['warmstart_fidelity'].get('p95_abs_error')}`",
            f"- warm-start fidelity max abs error: `{result['trainable_warmstart']['warmstart_fidelity'].get('max_abs_error')}`",
            "",
            "## Terrain / Contact",
            "",
            f"- flat XML floor friction: `{result['flat_floor_friction_xml']}`",
            f"- rough XML floor friction: `{result['rough_floor_friction_xml']}`",
            "",
            "## Blockers",
            "",
        ]
    )
    if result["blockers"]:
        lines.extend(f"- `{blocker}`" for blocker in result["blockers"])
    else:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    if result["warnings"]:
        lines.extend(f"- `{warning}`" for warning in result["warnings"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "Use the verified step-0 PPO checkpoint as the Phase 2 trainable",
            "warm-start. Before the full curriculum, add or configure staged DR",
            "range controls and leg-geometry jitter, then run Stage A and gate it",
            "against the corrected bridge before advancing.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--candidate-npz", default=str(DEFAULT_POLICY_NPZ))
    parser.add_argument("--restore-checkpoint", default=str(DEFAULT_RESTORE_CHECKPOINT))
    parser.add_argument("--warmstart-fidelity", default=str(DEFAULT_WARMSTART_FIDELITY))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    result = audit(args)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    write_markdown(result, output_md)
    print(result["status"])
    for blocker in result["blockers"]:
        print(blocker)
    for warning in result["warnings"]:
        print(warning)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
