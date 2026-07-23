#!/usr/bin/env python3
"""Compose the hash-auditable Winner-v98 response-conditioned Playground."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
DEFAULT_CONTROL_REPOSITORY = Path(
    os.environ.get(
        "WINNER_V98_CONTROL_REPOSITORY", "/home/lsd/robots/.ground_up_playground_control"
    )
)
BASE_PATCHES = (
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
    "reference_residual_hard_vector_ppo_networks.py": "playground/common/reference_residual_ppo_networks.py",
    "reference_residual_recurrent_adapter_ppo_networks.py": "playground/common/reference_residual_recurrent_adapter_ppo_networks.py",
    "winner_v3_variable_configuration.py": "playground/common/winner_v3_variable_configuration.py",
}
BASE_FINAL_PATCHES = (
    "ground_up_reference_residual_recurrent_adapter.patch",
    "ground_up_winner_v3_variable_configuration.patch",
)
V98_COPIED_SOURCES = {
    "winner_v98_response_conditioned_ppo_networks.py": "playground/common/winner_v98_response_conditioned_ppo_networks.py",
    "winner_v98_response_calibration_wrapper.py": "playground/common/winner_v98_response_calibration_wrapper.py",
    "winner_v98_response_conditioned_export.py": "playground/common/winner_v98_response_conditioned_export.py",
}
V98_FINAL_PATCHES = ("ground_up_response_conditioned_locomotion.patch",)
HUNK = re.compile(r"^@@ -(?:\d+)(?:,(\d+))? \+(?:\d+)(?:,(\d+))? @@")


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


def normalized_patch(path: Path) -> bytes:
    """Restore omitted prefixes on blank unified-diff context lines."""

    lines = path.read_bytes().replace(b"\r\n", b"\n").splitlines()
    output: list[bytes] = []
    old_remaining = 0
    new_remaining = 0
    in_hunk = False
    for raw in lines:
        if not in_hunk:
            output.append(raw)
            match = HUNK.match(raw.decode("utf-8"))
            if match:
                old_remaining = int(match.group(1) or 1)
                new_remaining = int(match.group(2) or 1)
                in_hunk = True
            continue
        line = raw if raw else b" "
        prefix = line[:1]
        if prefix == b" ":
            old_remaining -= 1
            new_remaining -= 1
        elif prefix == b"-":
            old_remaining -= 1
        elif prefix == b"+":
            new_remaining -= 1
        elif prefix != b"\\":
            raise ValueError(f"malformed hunk line in {path}: {raw!r}")
        output.append(line)
        if old_remaining == 0 and new_remaining == 0:
            in_hunk = False
        elif old_remaining < 0 or new_remaining < 0:
            raise ValueError(f"hunk count underflow in {path}")
    if in_hunk:
        raise ValueError(f"truncated hunk in {path}")
    return b"\n".join(output) + b"\n"


def apply_patch(path: Path, destination: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="winner-v98-patch-") as directory:
        normalized = Path(directory) / path.name
        normalized.write_bytes(normalized_patch(path))
        run(["git", "apply", "--check", str(normalized)], destination)
        run(["git", "apply", str(normalized)], destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--control-repository", type=Path, default=DEFAULT_CONTROL_REPOSITORY
    )
    parser.add_argument("--stop-before-winner-v98", action="store_true")
    args = parser.parse_args()
    output = args.output_root.resolve()
    control = args.control_repository.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse composed tree: {output}")
    if not (control / ".git").exists():
        raise FileNotFoundError(control)
    # Disable Windows checkout conversion before files are materialized.  Setting
    # core.autocrlf after clone is too late: every LF source then appears dirty and
    # the byte-frozen patches cannot match their control-commit context.
    run(
        [
            "git",
            "-c",
            "core.autocrlf=false",
            "clone",
            "--no-hardlinks",
            str(control),
            str(output),
        ],
        ROOT,
    )
    run(["git", "config", "core.autocrlf", "false"], output)
    run(["git", "checkout", "--detach", CONTROL_COMMIT], output)
    if run(["git", "rev-parse", "HEAD"], output).strip() != CONTROL_COMMIT:
        raise ValueError("control commit mismatch")

    inputs: list[dict[str, str]] = []
    for name in BASE_PATCHES:
        path = ROOT / "patches" / name
        inputs.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)})
        apply_patch(path, output)
    copied = dict(BASE_COPIED_SOURCES)
    if not args.stop_before_winner_v98:
        copied.update(V98_COPIED_SOURCES)
    for source_name, destination_name in copied.items():
        source = ROOT / "patches" / source_name
        destination = output / destination_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        inputs.append(
            {"path": source.relative_to(ROOT).as_posix(), "sha256": sha256(source)}
        )
    final_patches = list(BASE_FINAL_PATCHES)
    if not args.stop_before_winner_v98:
        final_patches.extend(V98_FINAL_PATCHES)
    for name in final_patches:
        path = ROOT / "patches" / name
        inputs.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)})
        apply_patch(path, output)

    compile_paths = [
        "playground/common/randomize.py",
        "playground/common/runner.py",
        "playground/common/reference_residual_ppo_networks.py",
        "playground/common/reference_residual_recurrent_adapter_ppo_networks.py",
        "playground/common/winner_v3_variable_configuration.py",
        "playground/open_duck_mini_v2/joystick.py",
        "playground/open_duck_mini_v2/runner.py",
    ]
    if not args.stop_before_winner_v98:
        compile_paths.extend(V98_COPIED_SOURCES.values())
    run([sys.executable, "-m", "py_compile", *compile_paths], output)
    diff = run(["git", "diff", "--binary", "--", "playground"], output)
    diff_path = output / "WINNER_V98_COMPOSED_SOURCE.diff"
    diff_path.write_text(diff, encoding="utf-8")
    manifest = {
        "schema_version": "winner_v98.composed_playground_source.v1",
        "control_repository": str(control),
        "control_commit": CONTROL_COMMIT,
        "inputs": inputs,
        "composed_diff_sha256": sha256(diff_path),
        "stop_before_winner_v98": args.stop_before_winner_v98,
        "copied_source_destinations": copied,
        "git_status": run(["git", "status", "--short"], output).splitlines(),
    }
    manifest_path = output / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output": str(output), "manifest": str(manifest_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
