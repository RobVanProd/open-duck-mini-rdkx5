#!/usr/bin/env python3
"""Reconstruct the exact reviewed Playground/XML/fit CPU environment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
COMPOSED_CRLF = (
    "playground/common/phase_moe_networks.py",
    "playground/common/recurrent_ppo_networks.py",
    "playground/common/rewards.py",
    "playground/common/runner.py",
    "playground/open_duck_mini_v2/custom_rewards.py",
    "playground/open_duck_mini_v2/joystick.py",
    "playground/open_duck_mini_v2/runner.py",
    "playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml",
    "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml",
)
WINDOWS_EVIDENCE = (
    "outputs/analysis/winner_v6b_numeric_hold_attribution.json",
    "outputs/analysis/winner_v8_numeric_hold_attribution.json",
    "outputs/analysis/winner_v9_stored_bound_contract_result.json",
    "outputs/analysis/winner_v9_nominal_behavior_result.json",
    "outputs/analysis/winner_v9_numeric_torque_hold_attribution.json",
    "outputs/analysis/winner_v10_inward_torque_contract_result.json",
    "outputs/analysis/winner_v10_nominal_behavior_result.json",
    "outputs/analysis/winner_v10_r2_condition1_result.json",
    "outputs/analysis/winner_v10_r2_condition2_result.json",
    "outputs/analysis/winner_v10_r2_condition3_result.json",
    "outputs/analysis/winner_v10_r2_condition4_result.json",
    "outputs/analysis/winner_v10_r2_condition5_result.json",
    "outputs/analysis/winner_v10_r2_condition6_result.json",
    "outputs/analysis/ground_up_robustness_r2_matrix_preregistration.json",
    "outputs/analysis/ground_up_robustness_r2_evaluator_contract.json",
    "outputs/analysis/ground_up_robustness_r2_reporting_contract.json",
    "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
    "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
    "tools/evaluate_ground_up_policy.py",
    "tools/closed_loop_sim_eval.py",
    "tools/actuator_bridge_model.py",
    "tools/aggregate_ground_up_robustness_r1.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crlf(path: Path) -> None:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    path.write_bytes(data.replace(b"\n", b"\r\n"))


def run(*command: str, cwd: Path | None = None) -> None:
    subprocess.run(list(command), cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repository", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--fit-output", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output_root, args.work_root, args.fit_output):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite prepared environment: {path}")
    args.work_root.mkdir(parents=True)
    run(
        "python",
        str(ROOT / "tools/compose_winner_v7_playground.py"),
        "--source-repository",
        str(args.source_repository),
        "--output-root",
        str(args.output_root),
    )
    for name in COMPOSED_CRLF:
        crlf(args.output_root / name)
    receipt_path = args.output_root / "winner_v7_playground_composition_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["composed_file_hashes"] = {
        relative: sha256(args.output_root / relative)
        for relative in sorted(receipt["composed_file_hashes"])
    }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    receipt_path.write_bytes(receipt_bytes)
    if sha256(receipt_path) != "628c35fab95e41a2fa82ae2255e0109502d72632c7ad408bf7e1294f5eb1c196":
        raise ValueError("composition receipt reconstruction mismatch")
    for name in WINDOWS_EVIDENCE:
        crlf(ROOT / name)

    v7 = args.work_root / "winner-v7"
    v9 = args.work_root / "winner-v9"
    v10 = args.work_root / "winner-v10"
    run(
        "python",
        str(ROOT / "tools/run_winner_v7_inward_projection_contract.py"),
        "--work-root",
        str(v7),
        "--output",
        str(args.work_root / "winner-v7-contract.json"),
    )
    run(
        "python",
        str(ROOT / "tools/run_winner_v9_stored_bound_contract.py"),
        "--source-half",
        str(v7 / "winner_v7_half_inward_projection.onnx"),
        "--source-final",
        str(v7 / "winner_v7_final_inward_projection.onnx"),
        "--model-xml",
        str(
            args.output_root
            / "playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml"
        ),
        "--scene-xml",
        str(
            args.output_root
            / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
        ),
        "--work-root",
        str(v9),
        "--output",
        str(args.work_root / "winner-v9-contract.json"),
    )
    v9_model = v9 / "xmls/open_duck_mini_v2_backlash.xml"
    crlf(v9_model)
    if sha256(v9_model) != "2132e477d2504faf08af4c5250952bd8b17611fb496ab15f30afc0371f327f9c":
        raise ValueError("winner-v9 XML reconstruction mismatch")
    run(
        "python",
        str(ROOT / "tools/run_winner_v10_inward_torque_contract.py"),
        "--source-half",
        str(v9 / "winner_v9_half_stored_bound.onnx"),
        "--source-final",
        str(v9 / "winner_v9_final_stored_bound.onnx"),
        "--source-model-xml",
        str(v9_model),
        "--source-scene-xml",
        str(v9 / "xmls/scene_flat_terrain_backlash.xml"),
        "--work-root",
        str(v10),
        "--output",
        str(args.work_root / "winner-v10-contract.json"),
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    for relative, expected in receipt["composed_file_hashes"].items():
        if sha256(args.output_root / relative) != expected:
            raise ValueError(f"composed file reconstruction mismatch: {relative}")
    allowed = set(receipt["composed_file_hashes"]) | {
        "winner_v7_playground_composition_receipt.json"
    }
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1"], cwd=args.output_root, text=True
    ).splitlines()
    for line in status:
        relative = line[3:].replace("\\", "/")
        if relative not in allowed:
            run(
                "git",
                "restore",
                "--source=HEAD",
                "--worktree",
                "--",
                relative,
                cwd=args.output_root,
            )
    fit_source = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    args.fit_output.write_bytes(fit_source.read_bytes().replace(b"\r\n", b"\n"))
    if sha256(args.fit_output) != "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b":
        raise ValueError("canonical LF fit reconstruction mismatch")
    destination = args.output_root / "playground/open_duck_mini_v2/xmls"
    shutil.copyfile(v10 / "xmls/open_duck_mini_v2_backlash.xml", destination / "open_duck_mini_v2_backlash.xml")
    shutil.copyfile(v10 / "xmls/scene_flat_terrain_backlash.xml", destination / "scene_flat_terrain_backlash.xml")
    print("PASS_WINNER_V15_CPU_ENVIRONMENT_PREPARATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
