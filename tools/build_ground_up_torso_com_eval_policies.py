#!/usr/bin/env python3
"""Build the frozen guard/deadband/envelope policies for torso-COM evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import tempfile

import numpy as np
import onnx
from onnx import numpy_helper

from build_ground_up_actual_centered_guard_screen import append_guard, contract_policy
from build_ground_up_command_deadband_repair import contract as deadband_contract
from build_ground_up_command_deadband_repair import wrap as wrap_deadband


SELECTED_STEPS = {
    "U05_DIRECT": (1_003_520, 2_007_040),
    "A05_DIRECT": (1_003_520, 2_007_040),
    "U_CURRICULUM": (512_000, 1_024_000),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def initializer_map(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--guard-preregistration", type=Path, required=True)
    parser.add_argument("--deadband-preregistration", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    guard_spec = json.loads(args.guard_preregistration.read_text())["guard_contract"]
    deadband_spec = json.loads(args.deadband_preregistration.read_text())["transform"]
    obs_indices = np.asarray(guard_spec["measured_joint_offset_indices"], dtype=np.int64)
    pitch_indices = np.asarray(guard_spec["pitch_chain_action_indices"], dtype=np.int64)
    home = np.asarray(guard_spec["home_target_rad"], dtype=np.float32)
    action_scale = float(guard_spec["action_scale_rad"])
    margin = 0.20
    deadband_index = int(deadband_spec["command_x_observation_index"])
    deadband = float(deadband_spec["zero_deadband_absolute_command_x"])
    args.output_root.mkdir(parents=True, exist_ok=True)

    members_by_arm_step = {}
    with tarfile.open(args.archive, "r:gz") as bundle:
        for arm in manifest["arms"]:
            arm_name = arm["name"]
            selected_stage = arm["stages"][-1]
            for entry in selected_stage["onnx"]:
                step = int(Path(entry["name"]).stem.rsplit("_", 1)[1])
                if step not in SELECTED_STEPS[arm_name]:
                    continue
                member_name = (
                    f"ground_up_torso_com_outputs/{arm_name}/stage{selected_stage['stage']}/"
                    f"{entry['name']}"
                )
                stream = bundle.extractfile(member_name)
                if stream is None:
                    raise RuntimeError(f"archive member missing: {member_name}")
                members_by_arm_step[(arm_name, step)] = (
                    member_name, entry["sha256"], stream.read()
                )

    policies = []
    with tempfile.TemporaryDirectory(prefix="torso_com_transform_") as temporary:
        scratch = Path(temporary)
        for arm_name, steps in SELECTED_STEPS.items():
            arm_output = args.output_root / arm_name
            arm_output.mkdir(parents=True, exist_ok=True)
            for step in steps:
                member, expected_hash, source_bytes = members_by_arm_step[(arm_name, step)]
                source_hash = sha256_bytes(source_bytes)
                source_model = onnx.load_model_from_string(source_bytes)
                source_inits = initializer_map(source_model)
                max_delta = source_inits["max_action_delta"].reshape(1, 14)
                source_path = scratch / f"{arm_name}_{step}_source.onnx"
                guarded_path = scratch / f"{arm_name}_{step}_guarded.onnx"
                source_path.write_bytes(source_bytes)
                guarded_model = append_guard(
                    source_model,
                    obs_indices=obs_indices,
                    pitch_indices=pitch_indices,
                    home=home,
                    action_scale=action_scale,
                    margin=margin,
                )
                onnx.save(guarded_model, guarded_path)
                guard_check = contract_policy(
                    source_path,
                    guarded_path,
                    home=home,
                    action_scale=action_scale,
                    obs_indices=obs_indices,
                    pitch_indices=pitch_indices,
                    margin=margin,
                    max_delta=max_delta,
                )
                final_model = wrap_deadband(guarded_model, deadband_index, deadband)
                output_path = arm_output / f"{arm_name}_{step}.onnx"
                onnx.save(final_model, output_path)
                deadband_check = deadband_contract(
                    guarded_path, output_path, deadband_index
                )
                final_inits = initializer_map(final_model)
                changed_source_initializers = [
                    name for name, value in source_inits.items()
                    if name not in final_inits or not np.array_equal(value, final_inits[name])
                ]
                left_ankle_delta = float(final_inits["max_action_delta"][0, 4])
                policies.append({
                    "arm": arm_name,
                    "step": step,
                    "archive_member": member,
                    "source_sha256": source_hash,
                    "expected_source_sha256": expected_hash,
                    "output_path": str(output_path.resolve()),
                    "output_sha256": sha256(output_path),
                    "guard_margin_rad": margin,
                    "deadband_absolute_command_x": deadband,
                    "left_ankle_normalized_delta": left_ankle_delta,
                    "source_initializers_preserved": changed_source_initializers == [],
                    "guard_contract": guard_check,
                    "deadband_contract": deadband_check,
                })

    checks = {
        "exact_six_selected_policies": len(policies) == 6,
        "selected_arm_steps_exact": {
            arm: sorted(item["step"] for item in policies if item["arm"] == arm)
            for arm in SELECTED_STEPS
        } == {arm: list(steps) for arm, steps in SELECTED_STEPS.items()},
        "all_source_hashes_match_manifest": all(
            item["source_sha256"] == item["expected_source_sha256"] for item in policies
        ),
        "all_source_initializers_preserved": all(
            item["source_initializers_preserved"] for item in policies
        ),
        "all_actual_centered_guard_contracts_pass": all(
            item["guard_contract"]["pass"] for item in policies
        ),
        "all_deadband_contracts_pass": all(
            item["deadband_contract"]["pass"] for item in policies
        ),
        "all_left_ankle_envelopes_already_conservative": all(
            item["left_ankle_normalized_delta"] == float(np.float32(0.12))
            for item in policies
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_TORSO_COM_EVAL_POLICY_TRANSFORM_CONTRACT"
        if not failed
        else "FAIL_TORSO_COM_EVAL_POLICY_TRANSFORM_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_eval_policy_transform.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "policies": policies,
        "authority": {
            "run_preregistered_cpu_behavior_matrix": not failed,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Torso-COM Evaluation-Policy Transform Contract",
        "",
        f"status: `{status}`",
        "",
        *(f"- {name}: `{passed}`" for name, passed in checks.items()),
        "",
        "Passing authorizes only the preregistered CPU behavior matrices. It does not select a winner or authorize hardware.",
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
