#!/usr/bin/env python3
"""Compose the hash-auditable winner-v3 CPU playground source tree."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONTROL_REPOSITORY = Path("/home/lsd/robots/.ground_up_playground_control")
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
PATCHES = (
    "ground_up_search_runner.patch",
    "ground_up_reference_conditioned.patch",
    "ground_up_recipe_search.patch",
    "ground_up_stage1_mechanism_stack.patch",
    "ground_up_nominal_reference_bootstrap.patch",
    "ground_up_signed_progress_objective.patch",
    "ground_up_reference_residual_actor.patch",
    "ground_up_hard_vector_command_support.patch",
    "ground_up_measured_actuator_bridge.patch",
    "ground_up_applied_target_observation.patch",
    "ground_up_tracking_tail_exceedance.patch",
    "ground_up_torso_com_randomization.patch",
)
BASE_COPIED_SOURCES = {
    "reference_residual_hard_vector_ppo_networks.py": (
        "playground/common/reference_residual_ppo_networks.py"
    ),
    "reference_residual_recurrent_adapter_ppo_networks.py": (
        "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    ),
}
WINNER_V3_COPIED_SOURCES = {
    "winner_v3_variable_configuration.py": (
        "playground/common/winner_v3_variable_configuration.py"
    ),
}
BASE_FINAL_PATCHES = ("ground_up_reference_residual_recurrent_adapter.patch",)
WINNER_V3_FINAL_PATCHES = ("ground_up_winner_v3_variable_configuration.patch",)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command}\n{completed.stdout}"
        )
    return completed.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--stop-before-winner-v3", action="store_true")
    args = parser.parse_args()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse composed tree: {output}")
    if not (CONTROL_REPOSITORY / ".git").exists():
        raise FileNotFoundError(CONTROL_REPOSITORY)
    run(
        ["git", "clone", "--no-hardlinks", str(CONTROL_REPOSITORY), str(output)],
        ROOT,
    )
    run(["git", "checkout", "--detach", CONTROL_COMMIT], output)
    if run(["git", "rev-parse", "HEAD"], output).strip() != CONTROL_COMMIT:
        raise ValueError("control commit mismatch")

    inputs: list[dict[str, str]] = []
    for name in PATCHES:
        path = ROOT / "patches" / name
        inputs.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path)})
        run(["git", "apply", "--check", str(path)], output)
        run(["git", "apply", str(path)], output)
    copied_sources = dict(BASE_COPIED_SOURCES)
    if not args.stop_before_winner_v3:
        copied_sources.update(WINNER_V3_COPIED_SOURCES)
    for source_name, destination_name in copied_sources.items():
        source = ROOT / "patches" / source_name
        destination = output / destination_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        inputs.append(
            {"path": str(source.relative_to(ROOT)), "sha256": sha256(source)}
        )
    final_patches = list(BASE_FINAL_PATCHES)
    if not args.stop_before_winner_v3:
        final_patches.extend(WINNER_V3_FINAL_PATCHES)
    for name in final_patches:
        path = ROOT / "patches" / name
        inputs.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path)})
        run(["git", "apply", "--check", str(path)], output)
        run(["git", "apply", str(path)], output)

    compile_paths = [
        "playground/common/randomize.py",
        "playground/common/runner.py",
        "playground/common/reference_residual_ppo_networks.py",
        "playground/common/reference_residual_recurrent_adapter_ppo_networks.py",
        "playground/open_duck_mini_v2/joystick.py",
        "playground/open_duck_mini_v2/runner.py",
    ]
    if not args.stop_before_winner_v3:
        compile_paths.append(
            "playground/common/winner_v3_variable_configuration.py"
        )
    run(["python3", "-m", "py_compile", *compile_paths], output)
    diff = run(["git", "diff", "--binary", "--", "playground"], output)
    diff_path = output / "WINNER_V3_COMPOSED_SOURCE.diff"
    diff_path.write_text(diff)
    manifest = {
        "schema_version": "winner_v3.composed_playground_source.v1",
        "control_repository": str(CONTROL_REPOSITORY),
        "control_commit": CONTROL_COMMIT,
        "inputs": inputs,
        "composed_diff_sha256": sha256(diff_path),
        "stop_before_winner_v3": args.stop_before_winner_v3,
        "copied_source_destinations": copied_sources,
        "git_status": run(["git", "status", "--short"], output).splitlines(),
    }
    manifest_path = output / "WINNER_V3_COMPOSED_SOURCE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "manifest": str(manifest_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
