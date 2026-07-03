#!/usr/bin/env python3
"""Run the Open Duck CUDA workflow through google-colab-cli.

This helper is offline-only. It uploads local repo tarballs to an existing Colab
session, starts a detached remote shell job through ``colab console``, polls for
an artifact bundle, and downloads the results. It does not use GitHub tokens and
does not touch the robot.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tarfile
import textwrap
import time


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_ROOT = ROOT / "outputs" / "analysis" / "colab_cli"
DEFAULT_UPLOAD_ROOT = ROOT.parent / "outputs" / "colab_cli_uploads"
DEFAULT_SESSION = "open-duck-l4"
PINNED_JAX_VERSION = "0.7.2"
MAX_DIRECT_UPLOAD_BYTES = 32 * 1024 * 1024


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def cli_value(value: object) -> str:
    """Return a command-line-safe scalar string for generated remote scripts."""

    if isinstance(value, float):
        # argparse can treat scientific negative strings such as "-5e-05" as
        # option-like tokens. Use fixed decimal form for small negative scales.
        text = f"{value:.12f}".rstrip("0").rstrip(".")
        return text if text not in {"", "-0"} else "0"
    return str(value)


def terrain_label(value: str) -> str:
    """Return a compact artifact label for a terrain z-scale string."""

    text = str(value).strip()
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text.startswith("0."):
        text = "z" + text[2:]
    else:
        text = "z" + text.replace(".", "p")
    return text or "z0"


def seed_count(seed_text: str | None) -> int:
    if not seed_text:
        return 1
    seeds: list[int] = []
    for part in seed_text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            step = 1 if end >= start else -1
            seeds.extend(range(start, end + step, step))
        else:
            seeds.append(int(part))
    return max(1, len(dict.fromkeys(seeds)))


def run(command: list[str], *, check: bool = True, timeout: int | None = None) -> subprocess.CompletedProcess:
    print(">>>", shell_join(command), flush=True)
    completed = subprocess.run(command, text=True, timeout=timeout, check=False)
    print("<<<", completed.returncode, flush=True)
    if check and completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_summary(path: Path) -> dict[str, object]:
    def git(args: list[str]) -> str | None:
        completed = subprocess.run(
            ["git", *args],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return None
        return completed.stdout.strip()

    tracked_status = git(["status", "--porcelain", "--untracked-files=no"]) or ""
    full_status = git(["status", "--porcelain"]) or ""
    untracked = [line for line in full_status.splitlines() if line.startswith("?? ")]
    return {
        "path": str(path.resolve()),
        "branch": git(["branch", "--show-current"]),
        "head": git(["rev-parse", "HEAD"]),
        "upstream": git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]),
        "tracked_dirty": bool(tracked_status.strip()),
        "tracked_status": tracked_status.splitlines(),
        "untracked_count": len(untracked),
    }


def tar_filter(member: tarfile.TarInfo) -> tarfile.TarInfo | None:
    parts = Path(member.name).parts
    blocked = {
        ".git",
        ".tmp",
        "__pycache__",
        ".pytest_cache",
        "cuda_imports",
        "wandb",
    }
    if any(part in blocked for part in parts):
        return None
    if "outputs" in parts:
        allowed_outputs = {
            ("outputs", "analysis", "actuator_response_fit_corrected_knee.json"),
            ("outputs", "analysis", "ACTUATOR_RESPONSE_FIT.md"),
            ("outputs", "analysis", "ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint"),
            ("outputs", "analysis", "reference_motion_x004_override.pkl"),
            ("outputs", "analysis", "reference_motion_override.json"),
            ("outputs", "analysis", "REFERENCE_MOTION_OVERRIDE.md"),
            ("outputs", "analysis", "soft_prior_fragment_config.json"),
            ("outputs", "analysis", "SOFT_PRIOR_FRAGMENT_CONFIG.md"),
            (
                "outputs",
                "analysis",
                "ppo_loc_swish_cmd_pitch_rl_2p25_candidate",
                "candidate_mlp.npz",
            ),
            (
                "outputs",
                "analysis",
                "command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate",
                "candidate.onnx",
            ),
            (
                "outputs",
                "analysis",
                "command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate",
                "candidate_mlp.npz",
            ),
            (
                "outputs",
                "analysis",
                "command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate",
                "candidate_mlp.npz",
            ),
            (
                "outputs",
                "analysis",
                "phase2_rate165_ppo_loc_warmstart_candidate",
                "candidate_mlp.npz",
            ),
            (
                "outputs",
                "analysis",
                "phase2_rate165_ppo_loc_warmstart_candidate",
                "candidate.onnx",
            ),
            (
                "outputs",
                "analysis",
                "phase2_rate165_ppo_loc_warmstart_step0_checkpoint",
            ),
            (
                "outputs",
                "analysis",
                "phase2_limit198_ppo_loc_warmstart_candidate",
                "candidate_mlp.npz",
            ),
            (
                "outputs",
                "analysis",
                "phase2_limit198_ppo_loc_warmstart_candidate",
                "candidate.onnx",
            ),
            (
                "outputs",
                "analysis",
                "phase2_limit198_ppo_loc_warmstart_step0.onnx",
            ),
            (
                "outputs",
                "analysis",
                "phase2_limit198_ppo_loc_warmstart_step0_checkpoint",
            ),
            (
                "outputs",
                "analysis",
                "ppo_bc_command_conditioned_dagger_seed5_x0_step0_checkpoint",
            ),
            (
                "outputs",
                "analysis",
                "ppo_bc_command_conditioned_dagger_seed5_x0_step0.onnx",
            ),
            (
                "outputs",
                "phase2_domain_randomization",
                "stage_a2_preserve_narrow_flat_no_push_gpu",
                "smoke_20260628T031553Z_gpu",
                "2026_06_27_232221_491520",
            ),
            (
                "outputs",
                "phase2_domain_randomization",
                "stage_c0_terrain_z002_preserve_from_a2_gpu",
                "smoke_20260628T103743Z_gpu",
                "2026_06_28_064431_245760",
            ),
            (
                "outputs",
                "phase2_domain_randomization",
                "stage_c2_terrain_z002_targetrate_from_c1_gpu",
                "smoke_20260628T113221Z_gpu",
                "2026_06_28_073829_163840",
            ),
            (
                "outputs",
                "phase2_domain_randomization",
                "stage_z002_tracking_margin_c2_a100",
                "smoke_20260630T102226Z_gpu",
                "2026_06_30_103539_122880",
            ),
            (
                "outputs",
                "phase2_domain_randomization",
                "stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu",
                "smoke_20260629T062042Z_gpu",
                "2026_06_29_022725_245760",
            ),
            ("outputs", "analysis", "PHASE2_CURRICULUM_GATE_LEDGER.md"),
            ("outputs", "analysis", "phase2_curriculum_gate_ledger.json"),
            ("outputs", "analysis", "PHASE2_Z005_SUPPORT_NEXT_RECIPE.md"),
            ("outputs", "analysis", "phase2_z005_support_next_recipe.json"),
            ("outputs", "analysis", "PHASE2_Z002_TRACKING_MARGIN_NEXT_RECIPE.md"),
            ("outputs", "analysis", "phase2_z002_tracking_margin_next_recipe.json"),
            ("outputs", "analysis", "PHASE2_Z002_TEACHER_CONTINUITY_NEXT_RECIPE.md"),
            ("outputs", "analysis", "phase2_z002_teacher_continuity_next_recipe.json"),
            ("outputs", "analysis", "PHASE2_Z0025_BOUNDARY_NEXT_RECIPE.md"),
            ("outputs", "analysis", "phase2_z0025_boundary_next_recipe.json"),
            ("outputs", "analysis", "PHASE2_Z0035_MOTION_FLOOR_NEXT_RECIPE.md"),
            ("outputs", "analysis", "phase2_z0035_motion_floor_next_recipe.json"),
            (
                "outputs",
                "analysis",
                "PHASE2_STAGEA2_GAIN099_TERRAIN_Z0024_BOUNDARY_DECISION.md",
            ),
            (
                "outputs",
                "analysis",
                "phase2_stagea2_gain099_terrain_z0024_boundary_decision.json",
            ),
            (
                "outputs",
                "analysis",
                "PHASE2_SWING_CLEARANCE_DIAGNOSTIC_Z0024.md",
            ),
            (
                "outputs",
                "analysis",
                "phase2_swing_clearance_diagnostic_z0024.json",
            ),
            (
                "outputs",
                "analysis",
                "PHASE2_SWING_PHASE_ADVANCE_NEXT_RECIPE.md",
            ),
            (
                "outputs",
                "analysis",
                "phase2_swing_phase_advance_next_recipe.json",
            ),
            (
                "outputs",
                "analysis",
                "PHASE2_RIGHT_SWING_STRUCTURAL_NEXT_RECIPE.md",
            ),
            (
                "outputs",
                "analysis",
                "phase2_right_swing_structural_next_recipe.json",
            ),
            (
                "outputs",
                "analysis",
                "PHASE2_RIGHT_SWING_PHASE_LIFT_NEXT_RECIPE.md",
            ),
            (
                "outputs",
                "analysis",
                "phase2_right_swing_phase_lift_next_recipe.json",
            ),
            (
                "outputs",
                "analysis",
                "PHASE2_RIGHT_SWING_PHASE_ADVANCE_NEXT_RECIPE.md",
            ),
            (
                "outputs",
                "analysis",
                "phase2_right_swing_phase_advance_next_recipe.json",
            ),
            (
                "outputs",
                "analysis",
                "PHASE2_RIGHT_SWING_PHASE_SINGLE_SUPPORT_NEXT_RECIPE.md",
            ),
            (
                "outputs",
                "analysis",
                "phase2_right_swing_phase_single_support_next_recipe.json",
            ),
            ("outputs", "analysis", "PHASE2_Z005_MOTION_FLOOR_NEXT_RECIPE.md"),
            ("outputs", "analysis", "phase2_z005_motion_floor_next_recipe.json"),
            ("outputs", "analysis", "PHASE2_Z005_MOTION_PRIOR_NEXT_RECIPE.md"),
            ("outputs", "analysis", "phase2_z005_motion_prior_next_recipe.json"),
            ("outputs", "analysis", "PHASE2_NEXT_RUN_PLAN.md"),
            ("outputs", "analysis", "phase2_next_run_plan.json"),
            ("outputs", "analysis", "PHASE2_STAGE_GUARD.md"),
            ("outputs", "analysis", "phase2_stage_guard.json"),
            ("outputs", "analysis", "PHASE2_ARTIFACT_MANIFEST.md"),
            ("outputs", "analysis", "phase2_artifact_manifest.json"),
            ("outputs", "analysis", "phase2_restore_checkpoints"),
        }
        rel_parts = tuple(parts[1:]) if len(parts) > 1 else tuple(parts)
        is_allowed_path = rel_parts in allowed_outputs
        is_allowed_parent = any(path[: len(rel_parts)] == rel_parts for path in allowed_outputs)
        is_allowed_child = any(rel_parts[: len(path)] == path for path in allowed_outputs)
        if not is_allowed_path and not is_allowed_parent and not is_allowed_child:
            return None
    if member.name.endswith((".pyc", ".pyo")):
        return None
    return member


def make_tarball(src: Path, dest: Path, arcname: str) -> None:
    src = src.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(dest, "w:gz") as tf:
        tf.add(src, arcname=arcname, filter=tar_filter)
    print(f"TARBALL {dest} size={dest.stat().st_size}", flush=True)


def would_package_path(relative_path: str) -> bool:
    info = tarfile.TarInfo(f"open-duck-mini-rdkx5/{relative_path}")
    return tar_filter(info) is not None


def required_rdk_package_paths(
    workflow: str, extra_paths: list[str] | None = None
) -> list[str]:
    phase2_terrain_workflows = {
        "phase2-z002-tracking-margin",
        "phase2-z002-teacher-continuity",
        "phase2-z0025-boundary",
        "phase2-z0035-motion-floor",
        "phase2-right-swing-structural",
        "phase2-right-swing-phase-lift",
        "phase2-right-swing-phase-advance",
        "phase2-right-swing-phase-single-support",
        "phase2-z005-support",
        "phase2-z005-motion-floor",
    }
    if workflow not in phase2_terrain_workflows:
        return list(extra_paths or [])
    if workflow == "phase2-z002-tracking-margin":
        recipe_json = "outputs/analysis/phase2_z002_tracking_margin_next_recipe.json"
    elif workflow == "phase2-z002-teacher-continuity":
        recipe_json = "outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json"
    elif workflow == "phase2-z0025-boundary":
        recipe_json = "outputs/analysis/phase2_z0025_boundary_next_recipe.json"
    elif workflow == "phase2-z0035-motion-floor":
        recipe_json = "outputs/analysis/phase2_z0035_motion_floor_next_recipe.json"
    elif workflow == "phase2-right-swing-structural":
        recipe_json = "outputs/analysis/phase2_right_swing_structural_next_recipe.json"
    elif workflow == "phase2-right-swing-phase-lift":
        recipe_json = "outputs/analysis/phase2_right_swing_phase_lift_next_recipe.json"
    elif workflow == "phase2-right-swing-phase-advance":
        recipe_json = "outputs/analysis/phase2_right_swing_phase_advance_next_recipe.json"
    elif workflow == "phase2-right-swing-phase-single-support":
        recipe_json = "outputs/analysis/phase2_right_swing_phase_single_support_next_recipe.json"
    elif workflow == "phase2-z005-motion-floor":
        recipe_json = "outputs/analysis/phase2_z005_motion_floor_next_recipe.json"
    else:
        recipe_json = "outputs/analysis/phase2_z005_support_next_recipe.json"
    paths = [
        "outputs/analysis/actuator_response_fit_corrected_knee.json",
        recipe_json,
        "tools/run_actuator_bridge_training_smoke.py",
        "outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate_mlp.npz",
        "outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate.onnx",
        "outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0.onnx",
        "outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint",
    ]
    if workflow in {"phase2-z002-tracking-margin", "phase2-z002-teacher-continuity"}:
        paths.append("tools/report_phase2_z002_tracking_margin_post_training_gates.py")
        paths.append(
            "outputs/phase2_domain_randomization/"
            "stage_c0_terrain_z002_preserve_from_a2_gpu/"
            "smoke_20260628T103743Z_gpu/2026_06_28_064431_245760"
        )
    else:
        paths.append("tools/report_phase2_z005_post_training_gates.py")
        paths.append(
            "outputs/phase2_domain_randomization/"
            "stage_a2_preserve_narrow_flat_no_push_gpu/"
            "smoke_20260628T031553Z_gpu/2026_06_27_232221_491520"
        )
    if workflow in {"phase2-z002-teacher-continuity", "phase2-z005-motion-floor"}:
        paths.extend(
            [
                (
                    "outputs/analysis/"
                    "command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/"
                    "candidate_mlp.npz"
                ),
            ]
        )
    if workflow == "phase2-z005-motion-floor":
        paths.append("outputs/analysis/phase2_z005_motion_prior_next_recipe.json")
    if extra_paths:
        paths.extend(extra_paths)
    return paths


def validate_rdk_package_inputs(
    workflow: str, rdk_root: Path, extra_paths: list[str] | None = None
) -> None:
    missing: list[str] = []
    excluded: list[str] = []
    for relative_path in required_rdk_package_paths(workflow, extra_paths):
        local_path = rdk_root / relative_path
        if not local_path.exists():
            missing.append(relative_path)
            continue
        if not would_package_path(relative_path):
            excluded.append(relative_path)
    if missing or excluded:
        lines = [f"Required local package inputs are not ready for workflow {workflow!r}."]
        if missing:
            lines.append("Missing:")
            lines.extend(f"  - {item}" for item in missing)
        if excluded:
            lines.append("Excluded by tar filter:")
            lines.extend(f"  - {item}" for item in excluded)
        raise SystemExit("\n".join(lines))


def colab_file_exists(session: str, remote_path: str) -> bool:
    completed = subprocess.run(
        ["colab", "ls", "-s", session, remote_path],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode == 0


def colab_status_text(session: str) -> str:
    completed = subprocess.run(
        ["colab", "status", "-s", session],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.stdout or ""


def colab_status_is_idle(status_text: str) -> bool:
    return "idle" in status_text.lower()


def remote_process_is_running(session: str, remote_pid: str, run_dir: Path) -> bool | None:
    """Return remote PID liveness when a PID file is available.

    `None` means the PID could not be checked. This intentionally probes the
    remote process table instead of trusting only Colab's session status, which
    can report idle while a raw-console shell job is still alive.
    """

    if not colab_file_exists(session, remote_pid):
        return None
    local_pid = run_dir / "remote_workflow.pid"
    try:
        downloaded = subprocess.run(
            ["colab", "download", "-s", session, remote_pid, str(local_pid)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=20,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None
    if downloaded.returncode != 0 or not local_pid.exists():
        return None
    try:
        pid = int(local_pid.read_text().strip())
    except ValueError:
        return None
    probe = run_dir / "remote_pid_probe.py"
    probe.write_text(
        "\n".join(
            [
                "import os",
                f"pid = {pid}",
                "try:",
                "    os.kill(pid, 0)",
                "except ProcessLookupError:",
                "    print('NOT_RUNNING')",
                "except PermissionError:",
                "    print('RUNNING')",
                "else:",
                "    print('RUNNING')",
            ]
        )
        + "\n"
    )
    try:
        checked = subprocess.run(
            ["colab", "exec", "-s", session, "--file", str(probe), "--timeout", "15"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=25,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None
    if checked.returncode != 0:
        return None
    output = checked.stdout or ""
    if "NOT_RUNNING" in output:
        return False
    if "RUNNING" in output:
        return True
    return None


def remote_output_dir_for_bundle(remote_bundle: str) -> str:
    name = Path(remote_bundle).name
    if name.endswith("_artifacts.tar.gz"):
        workflow_name = name[: -len("_artifacts.tar.gz")]
    else:
        workflow_name = Path(remote_bundle).stem
    return f"/content/open-duck-mini-rdkx5/outputs/analysis/{workflow_name}"


def download_partial_output_dir(session: str, remote_bundle: str, run_dir: Path) -> Path | None:
    remote_output_dir = remote_output_dir_for_bundle(remote_bundle)
    if not colab_file_exists(session, remote_output_dir):
        return None
    partial_dir = run_dir / "partial_remote_output"
    partial_dir.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        ["colab", "download", "-s", session, remote_output_dir, str(partial_dir)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    (run_dir / "partial_remote_output_download.log").write_text(
        completed.stdout or ""
    )
    if completed.returncode == 0:
        return partial_dir
    remote_archive = (
        f"/content/{Path(remote_bundle).name.removesuffix('.tar.gz')}"
        "_partial_output.tar.gz"
    )
    console_script = run_dir / "partial_remote_output_tar_console.sh"
    write_console_script(
        console_script,
        f"""
        set -euo pipefail
        test -d {shlex.quote(remote_output_dir)}
        rm -f {shlex.quote(remote_archive)}
        tar -czf {shlex.quote(remote_archive)} -C {shlex.quote(str(Path(remote_output_dir).parent))} {shlex.quote(Path(remote_output_dir).name)}
        ls -l {shlex.quote(remote_archive)}
        """,
    )
    tar_completed = run_console_script(
        session,
        console_script,
        run_dir / "partial_remote_output_tar_console.log",
        timeout_s=300,
    )
    if tar_completed.returncode != 0:
        return None
    archive_dest = run_dir / Path(remote_archive).name
    archive_completed = subprocess.run(
        ["colab", "download", "-s", session, remote_archive, str(archive_dest)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    (run_dir / "partial_remote_output_archive_download.log").write_text(
        archive_completed.stdout or ""
    )
    if archive_completed.returncode != 0 or not archive_dest.exists():
        return None
    with tarfile.open(archive_dest) as tf:
        tf.extractall(partial_dir)
    return partial_dir


def write_console_script(path: Path, remote_script: str) -> None:
    path.write_text(textwrap.dedent(remote_script).strip() + "\nexit\n")


def run_console_script(
    session: str,
    console_script: Path,
    log_path: Path,
    *,
    timeout_s: int = 120,
) -> subprocess.CompletedProcess:
    print(">>>", f"colab console -s {session} < {console_script}", flush=True)
    completed = subprocess.run(
        ["colab", "console", "-s", session],
        input=console_script.read_text(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout_s,
        check=False,
    )
    log_path.write_text(completed.stdout or "")
    print(completed.stdout[-2000:] if completed.stdout else "", flush=True)
    return completed


def initialize_content_api(session: str, run_dir: Path) -> None:
    """Touch /content once so google-colab-cli file upload/download can see it."""

    console_script = run_dir / "initialize_content_api_console.sh"
    write_console_script(
        console_script,
        """
        set -euo pipefail
        mkdir -p /content
        printf 'ready\\n' > /content/open_duck_colab_cli_content_ready.txt
        ls -l /content/open_duck_colab_cli_content_ready.txt
        """,
    )
    completed = run_console_script(
        session,
        console_script,
        run_dir / "console_initialize_content_api.log",
        timeout_s=120,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def upload_with_retries(
    session: str,
    local_path: Path,
    remote_path: str,
    *,
    attempts: int = 3,
) -> None:
    last_returncode = 1
    for attempt in range(1, attempts + 1):
        completed = run(
            ["colab", "upload", "-s", session, str(local_path), remote_path],
            check=False,
        )
        if completed.returncode == 0:
            return
        last_returncode = completed.returncode
        if attempt < attempts:
            time.sleep(2 * attempt)
    raise SystemExit(last_returncode)


def upload_file(
    session: str,
    local_path: Path,
    remote_path: str,
    run_dir: Path,
    *,
    max_direct_bytes: int = MAX_DIRECT_UPLOAD_BYTES,
) -> None:
    """Upload a file, chunking large payloads to avoid Colab content API 500s."""

    local_path = local_path.resolve()
    size = local_path.stat().st_size
    if size <= max_direct_bytes:
        upload_with_retries(session, local_path, remote_path)
        return

    sha256 = file_sha256(local_path)
    chunk_dir = local_path.parent / f"{local_path.name}.chunks"
    if chunk_dir.exists():
        shutil.rmtree(chunk_dir)
    chunk_dir.mkdir(parents=True)
    chunk_paths: list[Path] = []
    with local_path.open("rb") as source:
        index = 0
        while True:
            payload = source.read(max_direct_bytes)
            if not payload:
                break
            chunk_path = chunk_dir / f"{local_path.name}.part{index:05d}"
            chunk_path.write_bytes(payload)
            chunk_paths.append(chunk_path)
            index += 1

    remote_parts_dir = f"{remote_path}.parts"
    console_script = run_dir / f"mkdir_upload_parts_{Path(remote_path).name}.sh"
    write_console_script(
        console_script,
        f"""
        set -euo pipefail
        rm -rf {shlex.quote(remote_parts_dir)}
        mkdir -p {shlex.quote(remote_parts_dir)}
        """,
    )
    completed = run_console_script(
        session,
        console_script,
        run_dir / f"console_mkdir_upload_parts_{Path(remote_path).name}.log",
        timeout_s=120,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)

    for chunk_path in chunk_paths:
        upload_with_retries(
            session,
            chunk_path,
            f"{remote_parts_dir}/{chunk_path.name}",
        )

    manifest = {
        "remote_path": remote_path,
        "sha256": sha256,
        "size_bytes": size,
        "chunk_count": len(chunk_paths),
        "chunk_names": [chunk.name for chunk in chunk_paths],
    }
    manifest_path = run_dir / f"{Path(remote_path).name}.upload_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    chunk_names_literal = repr(manifest["chunk_names"])
    reassemble_script = run_dir / f"reassemble_upload_{Path(remote_path).name}.sh"
    write_console_script(
        reassemble_script,
        f"""
        set -euo pipefail
        python3 - <<'PY'
        from pathlib import Path
        import hashlib
        import sys

        remote_path = Path({remote_path!r})
        remote_parts_dir = Path({remote_parts_dir!r})
        chunk_names = {chunk_names_literal}
        expected_sha256 = {sha256!r}
        expected_size = {size}

        digest = hashlib.sha256()
        with remote_path.open("wb") as out:
            for name in chunk_names:
                chunk = remote_parts_dir / name
                data = chunk.read_bytes()
                digest.update(data)
                out.write(data)

        actual_sha256 = digest.hexdigest()
        actual_size = remote_path.stat().st_size
        print("REASSEMBLED", remote_path, actual_size, actual_sha256)
        if actual_size != expected_size or actual_sha256 != expected_sha256:
            print("UPLOAD_REASSEMBLY_MISMATCH", file=sys.stderr)
            raise SystemExit(1)
        PY
        """,
    )
    completed = run_console_script(
        session,
        reassemble_script,
        run_dir / f"console_reassemble_upload_{Path(remote_path).name}.log",
        timeout_s=300,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def start_remote_job(
    args: argparse.Namespace,
    run_dir: Path,
    rdk_remote_tar: str,
    playground_remote_tar: str,
    candidate_remote_policy: str | None = None,
    candidate_remote_manifest: str | None = None,
) -> None:
    workflow_name = f"open_duck_colab_cli_{args.workflow}_{timestamp()}"
    remote_driver = f"/content/{workflow_name}_driver.py"
    remote_log = f"/content/{workflow_name}.log"
    remote_exit = f"/content/{workflow_name}.exit"
    remote_pid = f"/content/{workflow_name}.pid"
    remote_bundle = f"/content/{workflow_name}_artifacts.tar.gz"
    run_dir.joinpath("REMOTE_PATHS.txt").write_text(
        "\n".join(
            [
                f"workflow_name={workflow_name}",
                f"remote_driver={remote_driver}",
                f"remote_log={remote_log}",
                f"remote_exit={remote_exit}",
                f"remote_pid={remote_pid}",
                f"remote_bundle={remote_bundle}",
            ]
        )
        + "\n"
    )

    driver = build_remote_driver(
        args,
        workflow_name,
        rdk_remote_tar,
        playground_remote_tar,
        remote_bundle,
        candidate_remote_policy=candidate_remote_policy,
        candidate_remote_manifest=candidate_remote_manifest,
    )
    driver_local = run_dir / f"{workflow_name}_driver.py"
    driver_local.write_text(driver)

    if args.exec_remote:
        completed = subprocess.run(
            [
                "colab",
                "exec",
                "-s",
                args.session,
                "-f",
                str(driver_local),
                "--timeout",
                str(args.exec_remote_timeout_s),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        exec_log = run_dir / "exec_remote.log"
        exec_log.write_text(completed.stdout or "")
        print(completed.stdout or "", flush=True)
        print(f"COLAB_EXEC_REMOTE_RETURNCODE {completed.returncode}", flush=True)
        download_remote_results(
            args.session,
            run_dir,
            remote_log,
            remote_exit,
            remote_bundle,
        )
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)
        return

    run(["colab", "upload", "-s", args.session, str(driver_local), remote_driver])

    console_script = run_dir / f"{workflow_name}_start_console.sh"
    if args.foreground_remote:
        write_console_script(
            console_script,
            f"""
            set -uo pipefail
            /usr/bin/python3 {remote_driver} > {remote_log} 2>&1 &
            echo $! > {remote_pid}
            wait $(cat {remote_pid})
            status=$?
            echo $status > {remote_exit}
            echo COLAB_CLI_WORKFLOW_EXIT $status
            """,
        )
        completed = run_console_script(
            args.session,
            console_script,
            run_dir / "console_start.log",
            timeout_s=args.foreground_remote_timeout_s,
        )
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)
        if args.no_poll:
            print(f"Remote foreground job finished. Bundle will be {remote_bundle}", flush=True)
            return
        poll_remote(
            args.session,
            run_dir,
            remote_log,
            remote_exit,
            remote_bundle,
            remote_pid,
            args.poll_interval_s,
            args.timeout_s,
            args.idle_no_sentinel_polls,
        )
        return

    write_console_script(
        console_script,
        f"""
        set -euo pipefail
        setsid bash -lc {shlex.quote(f'/usr/bin/python3 {remote_driver} > {remote_log} 2>&1; echo $? > {remote_exit}')} >/dev/null 2>&1 &
        echo $! > {remote_pid}
        echo COLAB_CLI_WORKFLOW_STARTED $(cat {remote_pid})
        """,
    )
    # colab console reads from stdin, so feed the small start script directly.
    completed = run_console_script(
        args.session,
        console_script,
        run_dir / "console_start.log",
        timeout_s=120,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)

    if args.no_poll:
        print(f"Remote job started. Bundle will be {remote_bundle}", flush=True)
        return
    poll_remote(
        args.session,
        run_dir,
        remote_log,
        remote_exit,
        remote_bundle,
        remote_pid,
        args.poll_interval_s,
        args.timeout_s,
        args.idle_no_sentinel_polls,
    )


def build_remote_driver(
    args: argparse.Namespace,
    workflow_name: str,
    rdk_tar: str,
    playground_tar: str,
    remote_bundle: str,
    *,
    candidate_remote_policy: str | None = None,
    candidate_remote_manifest: str | None = None,
) -> str:
    run_smoke = args.workflow in {"smoke", "training-smoke", "all", "candidate"}
    run_training_smoke_diagnostic = args.workflow == "training-smoke-diagnostic"
    run_candidate_training = args.workflow in {"candidate", "candidate-only", "all"}
    run_phase2_b0d = args.workflow == "phase2-b0d"
    run_phase2_b0e = args.workflow == "phase2-b0e"
    run_phase2_b0f = args.workflow == "phase2-b0f"
    run_phase2_b0g = args.workflow == "phase2-b0g"
    run_phase2_z002_tracking_margin = args.workflow == "phase2-z002-tracking-margin"
    run_phase2_z002_teacher_continuity = args.workflow == "phase2-z002-teacher-continuity"
    run_phase2_z0025_boundary = args.workflow == "phase2-z0025-boundary"
    run_phase2_z0035_motion_floor = args.workflow == "phase2-z0035-motion-floor"
    run_phase2_right_swing_structural = args.workflow == "phase2-right-swing-structural"
    run_phase2_right_swing_phase_lift = args.workflow == "phase2-right-swing-phase-lift"
    run_phase2_right_swing_phase_advance = args.workflow == "phase2-right-swing-phase-advance"
    run_phase2_right_swing_phase_single_support = (
        args.workflow == "phase2-right-swing-phase-single-support"
    )
    run_phase2_z005_support = args.workflow == "phase2-z005-support"
    run_phase2_z005_motion_floor = args.workflow == "phase2-z005-motion-floor"
    run_phase2_z005_like = run_phase2_z005_support or run_phase2_z005_motion_floor
    run_phase2_intermediate_terrain_like = (
        run_phase2_z002_tracking_margin
        or run_phase2_z002_teacher_continuity
        or run_phase2_z0025_boundary
        or run_phase2_z0035_motion_floor
        or run_phase2_right_swing_structural
        or run_phase2_right_swing_phase_lift
        or run_phase2_right_swing_phase_advance
        or run_phase2_right_swing_phase_single_support
    )
    run_phase2_terrain_like = run_phase2_z005_like or run_phase2_intermediate_terrain_like
    run_phase2_motion_floor_like = (
        run_phase2_z005_motion_floor
        or run_phase2_z0035_motion_floor
        or run_phase2_z0025_boundary
        or run_phase2_right_swing_structural
        or run_phase2_right_swing_phase_lift
        or run_phase2_right_swing_phase_advance
        or run_phase2_right_swing_phase_single_support
    )
    run_phase2_cuda_recipe = (
        run_phase2_b0d
        or run_phase2_b0e
        or run_phase2_b0f
        or run_phase2_b0g
        or run_phase2_z002_tracking_margin
        or run_phase2_z002_teacher_continuity
        or run_phase2_z0025_boundary
        or run_phase2_z0035_motion_floor
        or run_phase2_right_swing_structural
        or run_phase2_right_swing_phase_lift
        or run_phase2_right_swing_phase_advance
        or run_phase2_right_swing_phase_single_support
        or run_phase2_z005_support
        or run_phase2_z005_motion_floor
    )
    run_staged_curriculum = args.workflow == "staged-curriculum"
    run_candidate_eval_only = args.workflow == "candidate-eval-only"
    run_checkpoint_sweep = args.workflow == "checkpoint-sweep"
    run_candidate_gates = (
        run_candidate_training or run_staged_curriculum or run_candidate_eval_only
    )
    run_audit = (
        args.workflow
        in {
            "eval",
            "smoke",
            "candidate",
            "candidate-only",
            "candidate-eval-only",
            "checkpoint-sweep",
            "phase2-b0d",
            "phase2-b0e",
            "phase2-b0f",
            "phase2-b0g",
            "phase2-z002-tracking-margin",
            "phase2-z002-teacher-continuity",
            "phase2-z0025-boundary",
            "phase2-z0035-motion-floor",
            "phase2-right-swing-structural",
            "phase2-right-swing-phase-lift",
            "phase2-right-swing-phase-advance",
            "phase2-right-swing-phase-single-support",
            "phase2-z005-support",
            "phase2-z005-motion-floor",
            "all",
        }
        and not args.skip_audit
    )
    run_baseline_eval = args.workflow in {"eval", "smoke", "candidate", "all"}
    install_deps = not args.skip_deps
    smoke_steps = args.smoke_num_timesteps
    smoke_ppo_num_envs = args.smoke_ppo_num_envs
    smoke_ppo_batch_size = args.smoke_ppo_batch_size
    candidate_steps = args.candidate_num_timesteps
    candidate_target_rate_scale = cli_value(args.candidate_target_rate_scale)
    candidate_actuator_tracking_scale = cli_value(args.candidate_actuator_tracking_scale)
    candidate_tracking_lin_vel_scale = cli_value(args.candidate_tracking_lin_vel_scale)
    candidate_tracking_ang_vel_scale = cli_value(args.candidate_tracking_ang_vel_scale)
    candidate_tracking_sigma = cli_value(args.candidate_tracking_sigma)
    candidate_forward_progress_scale = cli_value(args.candidate_forward_progress_scale)
    candidate_forward_progress_deadband = cli_value(args.candidate_forward_progress_deadband)
    candidate_forward_shortfall_scale = cli_value(args.candidate_forward_shortfall_scale)
    candidate_forward_shortfall_required_ratio = cli_value(
        args.candidate_forward_shortfall_required_ratio
    )
    candidate_action_rate_scale = cli_value(args.candidate_action_rate_scale)
    candidate_action_magnitude_scale = cli_value(args.candidate_action_magnitude_scale)
    candidate_stand_still_scale = cli_value(args.candidate_stand_still_scale)
    candidate_alive_scale = cli_value(args.candidate_alive_scale)
    candidate_imitation_scale = cli_value(args.candidate_imitation_scale)
    candidate_lin_vel_x_min = cli_value(args.candidate_lin_vel_x_min)
    candidate_lin_vel_x_max = cli_value(args.candidate_lin_vel_x_max)
    candidate_zero_command_probability = cli_value(args.candidate_zero_command_probability)
    candidate_actuator_bridge_tau_min_s = cli_value(
        args.candidate_actuator_bridge_tau_min_s
    )
    candidate_actuator_bridge_tau_max_s = cli_value(
        args.candidate_actuator_bridge_tau_max_s
    )
    candidate_actuator_bridge_velocity_limit_min_rad_s = cli_value(
        args.candidate_actuator_bridge_velocity_limit_min_rad_s
    )
    candidate_actuator_bridge_velocity_limit_max_rad_s = cli_value(
        args.candidate_actuator_bridge_velocity_limit_max_rad_s
    )
    candidate_actuator_bridge_per_joint_variation = cli_value(
        args.candidate_actuator_bridge_per_joint_variation
    )
    artifact_checkpoint_mode = args.artifact_checkpoint_mode
    staged_initial_restore_checkpoint = args.staged_initial_restore_checkpoint
    if staged_initial_restore_checkpoint and not Path(
        staged_initial_restore_checkpoint
    ).is_absolute():
        staged_initial_restore_checkpoint = (
            f"/content/open-duck-mini-rdkx5/{staged_initial_restore_checkpoint}"
        )
    candidate_restore_checkpoint_path = args.candidate_restore_checkpoint_path
    if candidate_restore_checkpoint_path and not Path(
        candidate_restore_checkpoint_path
    ).is_absolute():
        candidate_restore_checkpoint_path = (
            f"/content/open-duck-mini-rdkx5/{candidate_restore_checkpoint_path}"
        )
    phase2_restore_checkpoint_path = args.phase2_restore_checkpoint_path
    if phase2_restore_checkpoint_path and not Path(
        phase2_restore_checkpoint_path
    ).is_absolute():
        phase2_restore_checkpoint_path = (
            f"/content/open-duck-mini-rdkx5/{phase2_restore_checkpoint_path}"
        )
    candidate_behavior_prior_mlp_npz = args.candidate_behavior_prior_mlp_npz
    if candidate_behavior_prior_mlp_npz and not Path(
        candidate_behavior_prior_mlp_npz
    ).is_absolute():
        candidate_behavior_prior_mlp_npz = (
            f"/content/open-duck-mini-rdkx5/{candidate_behavior_prior_mlp_npz}"
        )
    candidate_behavior_prior_scale = cli_value(args.candidate_behavior_prior_scale)
    candidate_behavior_prior_huber_delta = cli_value(
        args.candidate_behavior_prior_huber_delta
    )
    staged_stop_after_phase_arg = (
        f'"--stop-after-phase", "{args.staged_stop_after_phase}",'
        if args.staged_stop_after_phase is not None
        else ""
    )
    staged_initial_restore_arg = (
        f'"--initial-restore-checkpoint", "{staged_initial_restore_checkpoint}",'
        if staged_initial_restore_checkpoint
        else ""
    )
    staged_phase_gate_command_arg = (
        f'"--phase-gate-command-x", "{cli_value(args.staged_phase_gate_command_x)}",'
        if args.staged_phase_gate_command_x is not None
        else ""
    )
    staged_phase_gate_arg = (
        '"--phase-gate-freeze-check",'
        f"{staged_phase_gate_command_arg}"
        f'"--phase-gate-duration-s", "{cli_value(args.staged_phase_gate_duration_s)}",'
        f'"--phase-gate-bridge-mode", "{args.staged_phase_gate_bridge_mode}",'
        f'"--phase-gate-platform", "{args.staged_phase_gate_platform}",'
        f'"--phase-gate-timeout-s", "{args.staged_phase_gate_timeout_s}",'
        f'"--phase-gate-seeds", "{args.staged_phase_gate_seeds}",'
        f'"--phase-gate-max-fall-fraction", "{cli_value(args.staged_phase_gate_max_fall_fraction)}",'
        f'"--phase-gate-min-track-ratio-mean", "{cli_value(args.staged_phase_gate_min_track_ratio_mean)}",'
        f'"--phase-gate-min-vx-mean", "{cli_value(args.staged_phase_gate_min_vx_mean)}",'
        if args.staged_phase_gate_freeze_check
        else ""
    )
    staged_timeout_multiplier = args.staged_stop_after_phase or 3
    staged_gate_seed_count = seed_count(args.staged_phase_gate_seeds)
    staged_phase_gate_timeout_total = (
        args.staged_phase_gate_timeout_s
        * staged_timeout_multiplier
        * staged_gate_seed_count
        if args.staged_phase_gate_freeze_check
        else 0
    )
    checkpoint_sweep_policies = json.dumps(args.checkpoint_sweep_policies)
    checkpoint_sweep_commands = cli_value(args.checkpoint_sweep_commands)
    checkpoint_sweep_duration = cli_value(args.checkpoint_sweep_duration)
    checkpoint_sweep_bridge_mode = args.checkpoint_sweep_bridge_mode
    checkpoint_sweep_jax_platform = args.checkpoint_sweep_jax_platform
    candidate_checkpoint_sweep_commands = cli_value(args.candidate_checkpoint_sweep_commands)
    candidate_checkpoint_sweep_duration = cli_value(args.candidate_checkpoint_sweep_duration)
    candidate_checkpoint_sweep_jax_platform = args.candidate_checkpoint_sweep_jax_platform
    candidate_disable_bridge_arg = (
        '"--disable-actuator-bridge",' if args.candidate_disable_actuator_bridge else ""
    )
    candidate_behavior_prior_arg = (
        '"--enable-behavior-prior",'
        f' "--behavior-prior-mlp-npz", {candidate_behavior_prior_mlp_npz!r},'
        f' "--behavior-prior-scale", "{candidate_behavior_prior_scale}",'
        f' "--behavior-prior-huber-delta", "{candidate_behavior_prior_huber_delta}",'
        if candidate_behavior_prior_mlp_npz
        else ""
    )
    phase2_default_behavior_prior_mlp = (
        "/content/open-duck-mini-rdkx5/outputs/analysis/"
        "command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/"
        "candidate_mlp.npz"
    )
    if run_phase2_z002_teacher_continuity:
        phase2_recipe_id = "z002_teacher_continuity"
        phase2_default_candidate_name = "phase2_z002_teacher_continuity_cuda"
    elif run_phase2_z002_tracking_margin:
        phase2_recipe_id = "z002_tracking_margin"
        phase2_default_candidate_name = "phase2_z002_tracking_margin_cuda"
    elif run_phase2_z0025_boundary:
        phase2_recipe_id = "z0025_boundary"
        phase2_default_candidate_name = "phase2_z0025_boundary_cuda"
    elif run_phase2_z0035_motion_floor:
        phase2_recipe_id = "z0035_motion_floor"
        phase2_default_candidate_name = "phase2_z0035_motion_floor_cuda"
    elif run_phase2_right_swing_structural:
        phase2_recipe_id = "right_swing_structural"
        phase2_default_candidate_name = "phase2_right_swing_structural_cuda"
    elif run_phase2_right_swing_phase_lift:
        phase2_recipe_id = "right_swing_phase_lift"
        phase2_default_candidate_name = "phase2_right_swing_phase_lift_cuda"
    elif run_phase2_right_swing_phase_advance:
        phase2_recipe_id = "right_swing_phase_advance"
        phase2_default_candidate_name = "phase2_right_swing_phase_advance_cuda"
    elif run_phase2_right_swing_phase_single_support:
        phase2_recipe_id = "right_swing_phase_single_support"
        phase2_default_candidate_name = "phase2_right_swing_phase_single_support_cuda"
    elif run_phase2_z005_motion_floor:
        phase2_recipe_id = "z005_motion_floor"
        phase2_default_candidate_name = "phase2_z005_motion_floor_cuda"
    elif run_phase2_z005_support:
        phase2_recipe_id = "z005_support"
        phase2_default_candidate_name = "phase2_z005_support_stability_cuda"
    elif run_phase2_b0g:
        phase2_recipe_id = "b0g"
        phase2_default_candidate_name = "phase2_b0g_push_recovery_leftknee_cuda"
    elif run_phase2_b0f:
        phase2_recipe_id = "b0f"
        phase2_default_candidate_name = "phase2_b0f_push_local_preserve_cuda"
    elif run_phase2_b0e:
        phase2_recipe_id = "b0e"
        phase2_default_candidate_name = "phase2_b0e_motion_preserving_tracking_cuda"
    else:
        phase2_recipe_id = "b0d"
        phase2_default_candidate_name = "phase2_b0d_tracking_margin_cuda"
    phase2_output_root = f"/content/open_duck_training_phase2_{phase2_recipe_id}_cli"
    phase2_motion_preserve = (
        run_phase2_b0e or run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like
    )
    phase2_num_timesteps = (
        str(args.phase2_num_timesteps)
        if args.phase2_num_timesteps is not None
        else (
            "122880"
            if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity or run_phase2_motion_floor_like)
            else ("81920" if run_phase2_z005_support else ("80000" if (run_phase2_b0f or run_phase2_b0g) else "160000"))
        )
    )
    phase2_ppo_num_envs = (
        str(args.phase2_ppo_num_envs)
        if args.phase2_ppo_num_envs is not None
        else ("64" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "128")
    )
    phase2_ppo_num_evals = (
        str(args.phase2_ppo_num_evals)
        if args.phase2_ppo_num_evals is not None
        else "4"
    )
    phase2_ppo_episode_length = (
        str(args.phase2_episode_length)
        if args.phase2_episode_length is not None
        else "750"
    )
    phase2_ppo_batch_size = (
        str(args.phase2_ppo_batch_size)
        if args.phase2_ppo_batch_size is not None
        else ("512" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "1024")
    )
    phase2_ppo_num_minibatches = (
        str(args.phase2_ppo_num_minibatches)
        if args.phase2_ppo_num_minibatches is not None
        else "4"
    )
    phase2_ppo_num_updates_per_batch = (
        str(args.phase2_ppo_num_updates_per_batch)
        if args.phase2_ppo_num_updates_per_batch is not None
        else "2"
    )
    phase2_lr = "0.000002" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity) else ("0.000004" if run_phase2_motion_floor_like else ("0.000003" if (run_phase2_b0f or run_phase2_b0g or run_phase2_z005_support) else ("0.000012" if run_phase2_b0e else "0.000015")))
    phase2_clip = "0.015" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity) else ("0.025" if run_phase2_motion_floor_like else ("0.02" if (run_phase2_b0f or run_phase2_b0g or run_phase2_z005_support) else ("0.04" if run_phase2_b0e else "0.05")))
    phase2_max_grad_norm = "0.08" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity) else ("0.12" if run_phase2_motion_floor_like else ("0.1" if (run_phase2_b0f or run_phase2_b0g or run_phase2_z005_support) else ("0.2" if run_phase2_b0e else "0.25")))
    if run_phase2_z002_teacher_continuity:
        phase2_restore_kl = "7.5"
    elif run_phase2_z002_tracking_margin:
        phase2_restore_kl = "6.0"
    elif run_phase2_motion_floor_like:
        phase2_restore_kl = "3.0"
    elif run_phase2_z005_support:
        phase2_restore_kl = "4.0"
    elif run_phase2_b0f or run_phase2_b0g:
        phase2_restore_kl = "5.0"
    elif run_phase2_b0e:
        phase2_restore_kl = "1.5"
    else:
        phase2_restore_kl = "1.0"
    phase2_actuator_tracking = (
        "-0.005"
        if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity or run_phase2_motion_floor_like)
        else (
            "-0.01"
            if run_phase2_z005_support
            else (
                "0"
                if run_phase2_b0g
                else ("-0.01" if run_phase2_b0f else ("-0.015" if run_phase2_b0e else "-0.04"))
            )
        )
    )
    if args.phase2_actuator_tracking_scale is not None:
        phase2_actuator_tracking = cli_value(args.phase2_actuator_tracking_scale)
    phase2_forward_progress = "4.5" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity) else ("4.0" if run_phase2_motion_floor_like else ("2.5" if phase2_motion_preserve else "2"))
    phase2_command_progress = "3.5" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity) else ("3.0" if run_phase2_motion_floor_like else ("1.5" if phase2_motion_preserve else "1"))
    phase2_command_shortfall = "-10" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity) else ("-8" if run_phase2_motion_floor_like else ("-4" if phase2_motion_preserve else "-2.5"))
    phase2_command_ratio = "0.55" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity) else ("0.5" if run_phase2_motion_floor_like else ("0.45" if phase2_motion_preserve else "0.4"))
    if args.phase2_forward_progress_scale is not None:
        phase2_forward_progress = cli_value(args.phase2_forward_progress_scale)
    if args.phase2_command_progress_scale is not None:
        phase2_command_progress = cli_value(args.phase2_command_progress_scale)
    if args.phase2_command_progress_shortfall_scale is not None:
        phase2_command_shortfall = cli_value(args.phase2_command_progress_shortfall_scale)
    if args.phase2_command_progress_required_ratio is not None:
        phase2_command_ratio = cli_value(args.phase2_command_progress_required_ratio)
    phase2_extra_args = (
        '"--tracking-lin-vel-scale", "3",'
        '"--tracking-sigma", "0.01",'
        if phase2_motion_preserve
        else ""
    )
    phase2_dr_friction_min = "0.98" if run_phase2_terrain_like else ("0.95" if (run_phase2_b0f or run_phase2_b0g) else "0.8")
    phase2_dr_friction_max = "1.02" if run_phase2_terrain_like else ("1.05" if (run_phase2_b0f or run_phase2_b0g) else "1.1")
    phase2_dr_frictionloss_scale_min = "0.995" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "0.98"
    phase2_dr_frictionloss_scale_max = "1.005" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "1.02"
    phase2_dr_armature_scale_min = "1.0"
    phase2_dr_armature_scale_max = "1.005" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "1.02"
    phase2_dr_com_jitter_m = "0.002" if run_phase2_terrain_like else ("0.003" if (run_phase2_b0f or run_phase2_b0g) else "0.01")
    phase2_dr_mass_scale_min = "0.995" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "0.98"
    phase2_dr_mass_scale_max = "1.005" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "1.02"
    phase2_dr_torso_mass_delta_min = "-0.005" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "-0.02"
    phase2_dr_torso_mass_delta_max = "0.005" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "0.02"
    phase2_dr_qpos_jitter_rad = "0.002" if run_phase2_terrain_like else ("0.003" if (run_phase2_b0f or run_phase2_b0g) else "0.006")
    phase2_dr_actuator_gain_scale_min = "0.995" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "0.98"
    phase2_dr_actuator_gain_scale_max = "1.005" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "1.02"
    phase2_dr_leg_geometry_jitter_scale = "0.001" if (run_phase2_b0f or run_phase2_b0g or run_phase2_terrain_like) else "0.003"
    phase2_push_interval_min_s = "1.0" if (run_phase2_b0f or run_phase2_b0g) else "7"
    phase2_push_interval_max_s = "1.5" if run_phase2_b0g else ("2.0" if run_phase2_b0f else "12")
    phase2_push_magnitude_min = "0.05" if run_phase2_b0g else ("0.03" if run_phase2_b0f else "0.02")
    phase2_push_magnitude_max = "0.1" if run_phase2_b0g else ("0.08" if run_phase2_b0f else "0.1")
    phase2_noise_level = "0.25" if (run_phase2_b0f or run_phase2_b0g) else "0.5"
    phase2_noise_joint_pos = "0.004" if (run_phase2_b0f or run_phase2_b0g) else "0.0075"
    phase2_noise_joint_vel = "0.4" if (run_phase2_b0f or run_phase2_b0g) else "0.75"
    phase2_noise_gravity = "0.02" if (run_phase2_b0f or run_phase2_b0g) else "0.04"
    phase2_noise_gyro = "0.02" if (run_phase2_b0f or run_phase2_b0g) else "0.04"
    phase2_noise_accelerometer = "0.01" if (run_phase2_b0f or run_phase2_b0g) else "0.02"
    phase2_behavior_prior_scale = "-0.18" if run_phase2_z002_teacher_continuity else ("-1.0" if (run_phase2_b0f or run_phase2_b0g) else "-0.35")
    phase2_push_recovery_arg = (
        '"--push-recovery-actuator-tracking-scale", "-0.02",'
        '"--push-recovery-actuator-tracking-huber-delta", "0.03",'
        '"--push-recovery-tracking-window-steps", "25",'
        '"--push-recovery-tracking-joint-indices", "3",'
        if run_phase2_b0g
        else ""
    )
    phase2_restore_checkpoint = (
        "/content/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/"
        "stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/"
        "2026_06_28_064431_245760"
        if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity)
        else
        "/content/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/"
        "stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/"
        "2026_06_27_232221_491520"
        if run_phase2_terrain_like
        else "/content/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/"
        "stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/"
        "smoke_20260629T062042Z_gpu/2026_06_29_022725_245760"
    )
    if phase2_restore_checkpoint_path:
        phase2_restore_checkpoint = phase2_restore_checkpoint_path
    phase2_behavior_prior_arg = (
        (
            '"--enable-behavior-prior",'
            '"--behavior-prior-mlp-npz",'
            f'"{phase2_default_behavior_prior_mlp}",'
            f'"--behavior-prior-scale", "{phase2_behavior_prior_scale}",'
            '"--behavior-prior-huber-delta", "0.08",'
        )
        if run_phase2_z002_teacher_continuity
        else candidate_behavior_prior_arg
        if (run_phase2_terrain_like and candidate_behavior_prior_mlp_npz)
        else (
            ""
            if run_phase2_terrain_like
            else (
                '"--enable-behavior-prior",'
                '"--behavior-prior-mlp-npz",'
                '"/content/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz",'
                f'"--behavior-prior-scale", "{phase2_behavior_prior_scale}",'
                '"--behavior-prior-huber-delta", "0.05",'
            )
        )
    )
    phase2_push_enable_arg = (
        '"--no-push-enable",'
        if run_phase2_terrain_like
        else '"--push-enable",'
    )
    if run_phase2_right_swing_structural:
        phase2_support_stability_arg = (
            '"--forward-wrong-direction-scale", "-6",'
            '"--forward-wrong-direction-allowed-reverse-ratio", "0.01",'
            '"--forward-swing-target-rate-limit-scale", "-0.0025",'
            '"--forward-swing-target-rate-limit-joint-indices", "11,12,13",'
            '"--forward-swing-target-rate-limit-values", "2.25,2.75,2.00",'
            '"--forward-swing-target-rate-limit-huber-delta", "0.05",'
            '"--forward-swing-advance-scale", "-0.001",'
            '"--forward-swing-advance-target-m", "0.004",'
            '"--forward-swing-advance-huber-delta", "0.002",'
            '"--forward-swing-clearance-scale", "-0.00025",'
            '"--forward-swing-clearance-target-m", "0.016",'
            '"--forward-swing-clearance-huber-delta", "0.003",'
        )
    elif run_phase2_right_swing_phase_lift:
        phase2_support_stability_arg = (
            '"--forward-wrong-direction-scale", "-6",'
            '"--forward-wrong-direction-allowed-reverse-ratio", "0.01",'
            '"--forward-swing-target-rate-limit-scale", "-0.0025",'
            '"--forward-swing-target-rate-limit-joint-indices", "11,12,13",'
            '"--forward-swing-target-rate-limit-values", "2.25,2.75,2.00",'
            '"--forward-swing-target-rate-limit-huber-delta", "0.05",'
            '"--forward-phase-swing-lift-scale", "-0.0006",'
            '"--forward-phase-swing-lift-target-m", "0.012",'
            '"--forward-phase-swing-lift-huber-delta", "0.003",'
            '"--forward-swing-advance-scale", "-0.001",'
            '"--forward-swing-advance-target-m", "0.004",'
            '"--forward-swing-advance-huber-delta", "0.002",'
            '"--forward-swing-clearance-scale", "-0.00025",'
            '"--forward-swing-clearance-target-m", "0.016",'
            '"--forward-swing-clearance-huber-delta", "0.003",'
        )
    elif run_phase2_right_swing_phase_advance:
        phase2_support_stability_arg = (
            '"--forward-wrong-direction-scale", "-6",'
            '"--forward-wrong-direction-allowed-reverse-ratio", "0.01",'
            '"--forward-swing-target-rate-limit-scale", "-0.0025",'
            '"--forward-swing-target-rate-limit-joint-indices", "11,12,13",'
            '"--forward-swing-target-rate-limit-values", "2.25,2.75,2.00",'
            '"--forward-swing-target-rate-limit-huber-delta", "0.05",'
            '"--forward-phase-swing-lift-scale", "-0.0006",'
            '"--forward-phase-swing-lift-target-m", "0.012",'
            '"--forward-phase-swing-lift-huber-delta", "0.003",'
            '"--forward-swing-phase-advance-ticks", "3",'
            '"--forward-swing-advance-scale", "-0.001",'
            '"--forward-swing-advance-target-m", "0.004",'
            '"--forward-swing-advance-huber-delta", "0.002",'
            '"--forward-swing-clearance-scale", "-0.00025",'
            '"--forward-swing-clearance-target-m", "0.016",'
            '"--forward-swing-clearance-huber-delta", "0.003",'
        )
    elif run_phase2_right_swing_phase_single_support:
        phase2_support_stability_arg = (
            '"--forward-wrong-direction-scale", "-6",'
            '"--forward-wrong-direction-allowed-reverse-ratio", "0.01",'
            '"--forward-swing-target-rate-limit-scale", "-0.0025",'
            '"--forward-swing-target-rate-limit-joint-indices", "11,12,13",'
            '"--forward-swing-target-rate-limit-values", "2.25,2.75,2.00",'
            '"--forward-swing-target-rate-limit-huber-delta", "0.05",'
            '"--forward-phase-swing-lift-scale", "-0.0006",'
            '"--forward-phase-swing-lift-target-m", "0.012",'
            '"--forward-phase-swing-lift-huber-delta", "0.003",'
            '"--forward-phase-single-support-scale", "-0.004",'
            '"--forward-phase-single-support-swing-contact-weight", "1.0",'
            '"--forward-phase-single-support-stance-no-contact-weight", "2.0",'
            '"--forward-swing-advance-scale", "-0.001",'
            '"--forward-swing-advance-target-m", "0.004",'
            '"--forward-swing-advance-huber-delta", "0.002",'
            '"--forward-swing-clearance-scale", "-0.00025",'
            '"--forward-swing-clearance-target-m", "0.016",'
            '"--forward-swing-clearance-huber-delta", "0.003",'
        )
    elif run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity or run_phase2_motion_floor_like:
        phase2_support_stability_arg = (
            '"--forward-wrong-direction-scale", "-6",'
            '"--forward-wrong-direction-allowed-reverse-ratio", "0.01",'
            '"--forward-contact-support-scale", "-0.12",'
            '"--forward-contact-support-no-contact-weight", "1.0",'
            '"--forward-contact-support-asymmetry-weight", "0.1",'
            '"--forward-single-support-scale", "0.05",'
            '"--forward-double-support-scale", "-0.05",'
            '"--forward-double-support-dwell-scale", "-0.05",'
            '"--forward-double-support-dwell-grace-steps", "24",'
            '"--forward-swing-advance-scale", "-0.001",'
            '"--forward-swing-advance-target-m", "0.004",'
            '"--forward-swing-advance-huber-delta", "0.002",'
            '"--forward-swing-clearance-scale", "-0.00025",'
            '"--forward-swing-clearance-target-m", "0.016",'
            '"--forward-swing-clearance-huber-delta", "0.003",'
        )
    elif run_phase2_z005_support:
        phase2_support_stability_arg = (
        '"--forward-wrong-direction-scale", "-4",'
        '"--forward-wrong-direction-allowed-reverse-ratio", "0.02",'
        '"--forward-contact-support-scale", "-0.35",'
        '"--forward-contact-support-no-contact-weight", "2.0",'
        '"--forward-contact-support-asymmetry-weight", "0.25",'
        '"--forward-single-support-scale", "0.1",'
        '"--forward-double-support-scale", "-0.15",'
        '"--forward-double-support-dwell-scale", "-0.25",'
        '"--forward-double-support-dwell-grace-steps", "16",'
        '"--forward-swing-advance-scale", "-0.002",'
        '"--forward-swing-advance-target-m", "0.004",'
        '"--forward-swing-advance-huber-delta", "0.002",'
        '"--forward-swing-clearance-scale", "-0.0005",'
        '"--forward-swing-clearance-target-m", "0.018",'
        '"--forward-swing-clearance-huber-delta", "0.003",'
        )
    else:
        phase2_support_stability_arg = ""
    phase2_forward_swing_target_rate_limit_arg = ""
    if args.phase2_forward_swing_target_rate_limit_scale is not None:
        missing_rate_limit_args = [
            name
            for name, value in [
                (
                    "--phase2-forward-swing-target-rate-limit-joint-indices",
                    args.phase2_forward_swing_target_rate_limit_joint_indices,
                ),
                (
                    "--phase2-forward-swing-target-rate-limit-values",
                    args.phase2_forward_swing_target_rate_limit_values,
                ),
            ]
            if value is None
        ]
        if missing_rate_limit_args:
            raise SystemExit(
                "Missing required argument(s) for "
                "--phase2-forward-swing-target-rate-limit-scale: "
                + ", ".join(missing_rate_limit_args)
            )
        phase2_forward_swing_target_rate_limit_huber_delta = (
            cli_value(args.phase2_forward_swing_target_rate_limit_huber_delta)
            if args.phase2_forward_swing_target_rate_limit_huber_delta is not None
            else "0.05"
        )
        phase2_forward_swing_target_rate_limit_arg = (
            f'"--forward-swing-target-rate-limit-scale", '
            f'"{cli_value(args.phase2_forward_swing_target_rate_limit_scale)}",'
            f'"--forward-swing-target-rate-limit-joint-indices", '
            f'"{args.phase2_forward_swing_target_rate_limit_joint_indices}",'
            f'"--forward-swing-target-rate-limit-values", '
            f'"{args.phase2_forward_swing_target_rate_limit_values}",'
            f'"--forward-swing-target-rate-limit-huber-delta", '
            f'"{phase2_forward_swing_target_rate_limit_huber_delta}",'
        )
    phase2_support_stability_arg = (
        phase2_support_stability_arg + phase2_forward_swing_target_rate_limit_arg
    )
    phase2_final_training_args = ""
    if args.phase2_final_training_args_json:
        try:
            final_training_args = json.loads(args.phase2_final_training_args_json)
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f"Invalid --phase2-final-training-args-json: {exc}"
            ) from exc
        if not isinstance(final_training_args, list) or not all(
            isinstance(item, str) for item in final_training_args
        ):
            raise SystemExit(
                "--phase2-final-training-args-json must be a JSON list of strings"
            )
        phase2_final_training_args = "".join(f"{item!r}," for item in final_training_args)
    phase2_base_height_scale = "-0.35" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity or run_phase2_motion_floor_like) else "-0.8"
    phase2_forward_pitch_scale = "-0.3" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity or run_phase2_motion_floor_like) else "-0.4"
    phase2_forward_pitch_rate_scale = "-0.06" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity or run_phase2_motion_floor_like) else "-0.08"
    phase2_action_rate_scale = "-0.035" if run_phase2_z002_teacher_continuity else ("-0.04" if run_phase2_z002_tracking_margin else ("-0.055" if run_phase2_motion_floor_like else "-0.08"))
    phase2_action_magnitude_scale = "-0.003" if (run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity or run_phase2_motion_floor_like) else "-0.005"
    phase2_target_rate_scale = "-0.01" if run_phase2_z002_teacher_continuity else ("-0.02" if run_phase2_z002_tracking_margin else "0")
    if args.phase2_target_rate_scale is not None:
        phase2_target_rate_scale = cli_value(args.phase2_target_rate_scale)
    phase2_bridge_delay_max = "3" if run_phase2_terrain_like else "4"
    phase2_bridge_tau_max = "0.14" if run_phase2_terrain_like else "0.1"
    phase2_bridge_per_joint_variation = "0.1" if run_phase2_terrain_like else "0.05"
    phase2_terrain_hfield_z_scale = (
        "0.002"
        if run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity
        else
        "0.0035"
        if run_phase2_z0035_motion_floor
        else "0.0024"
        if run_phase2_right_swing_structural
        or run_phase2_right_swing_phase_lift
        or run_phase2_right_swing_phase_advance
        or run_phase2_right_swing_phase_single_support
        else "0.0025"
        if run_phase2_z0025_boundary
        else ("0.005" if run_phase2_z005_like else "0.002")
    )
    if args.phase2_terrain_hfield_z_scale is not None:
        phase2_terrain_hfield_z_scale = cli_value(args.phase2_terrain_hfield_z_scale)
    phase2_primary_terrain_z = (
        "0.002"
        if run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity
        else (
            "0.0025"
            if run_phase2_z0025_boundary
            else (
                "0.0035"
                if run_phase2_z0035_motion_floor
                else (
                    "0.0024"
                    if (
                        run_phase2_right_swing_structural
                        or run_phase2_right_swing_phase_lift
                        or run_phase2_right_swing_phase_advance
                        or run_phase2_right_swing_phase_single_support
                    )
                    else "0.005"
                )
            )
        )
    )
    if args.phase2_terrain_hfield_z_scale is not None:
        phase2_primary_terrain_z = phase2_terrain_hfield_z_scale
    phase2_primary_terrain_label = (
        "z002"
        if run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity
        else (
            "z0025"
            if run_phase2_z0025_boundary
            else (
                "z0035"
                if run_phase2_z0035_motion_floor
                else (
                    "z0024"
                    if (
                        run_phase2_right_swing_structural
                        or run_phase2_right_swing_phase_lift
                        or run_phase2_right_swing_phase_advance
                        or run_phase2_right_swing_phase_single_support
                    )
                    else "z005"
                )
            )
        )
    )
    if args.phase2_terrain_hfield_z_scale is not None:
        phase2_primary_terrain_label = terrain_label(phase2_terrain_hfield_z_scale)
    phase2_post_training_reporter = (
        "tools/report_phase2_z002_tracking_margin_post_training_gates.py"
        if run_phase2_z002_tracking_margin or run_phase2_z002_teacher_continuity
        else "tools/report_phase2_z005_post_training_gates.py"
    )
    return textwrap.dedent(
        f"""
        import atexit
        import datetime as dt
        import json
        import shutil
        import subprocess
        import sys
        import threading
        import time
        from pathlib import Path
        from importlib import metadata

        PYTHON = "/usr/bin/python3"
        RDK = Path("/content/open-duck-mini-rdkx5")
        PLAYGROUND = Path("/content/Open_Duck_Playground")
        OUT = RDK / "outputs/analysis/{workflow_name}"
        STAGED_ROOT = Path("/content/open_duck_staged_curriculum_cli_{workflow_name}")
        OUT.mkdir(parents=True, exist_ok=True)
        for root in (RDK, PLAYGROUND):
            (root / ".tmp" / "jax_cache" / "xla_gpu_per_fusion_autotune_cache_dir").mkdir(
                parents=True,
                exist_ok=True,
            )
        REMOTE_BUNDLE = Path("{remote_bundle}")
        RUN_STATUS = {{"exit_status": 0}}
        ARTIFACT_CHECKPOINT_MODE = {artifact_checkpoint_mode!r}
        ARTIFACT_BUNDLE_INTERVAL_S = {max(0, int(args.remote_artifact_interval_s))}
        BUNDLE_LOCK = threading.Lock()

        def checkpoint_dirs_for_run(run_dir):
            onnx_stems = {{path.stem for path in run_dir.glob("*.onnx")}}
            candidates = []
            for child in run_dir.iterdir():
                if child.is_dir() and child.name in onnx_stems:
                    candidates.append(child)
            return sorted(candidates, key=lambda path: path.stat().st_mtime)

        def copy_checkpoint_dirs(run_dir, run_dest):
            manifest = {{
                "mode": ARTIFACT_CHECKPOINT_MODE,
                "copied": [],
                "available": [],
            }}
            candidates = checkpoint_dirs_for_run(run_dir)
            manifest["available"] = [path.name for path in candidates]
            if ARTIFACT_CHECKPOINT_MODE == "none":
                selected = []
            elif ARTIFACT_CHECKPOINT_MODE == "all":
                selected = candidates
            else:
                selected = candidates[-1:]
            for item in selected:
                try:
                    dest = run_dest / item.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                    manifest["copied"].append(item.name)
                except Exception as exc:
                    print("copy_checkpoint_warning", item, type(exc).__name__, exc, flush=True)
            try:
                (run_dest / "checkpoint_artifact_manifest.json").write_text(
                    json.dumps(manifest, indent=2) + "\\n"
                )
            except Exception as exc:
                print("checkpoint_manifest_warning", type(exc).__name__, exc, flush=True)

        def copy_training_outputs(src, dest):
            src = Path(src)
            dest = Path(dest)
            if not src.exists():
                return
            dest.mkdir(parents=True, exist_ok=True)
            for run_dir in sorted(src.glob("**/smoke_*_gpu")):
                rel_parent = run_dir.parent.relative_to(src)
                run_dest = dest / rel_parent / run_dir.name
                run_dest.mkdir(parents=True, exist_ok=True)
                for pattern in ["*.onnx", "smoke_manifest*.json", "stdout.txt", "stderr.txt"]:
                    for item in sorted(run_dir.glob(pattern)):
                        try:
                            (run_dest / item.name).write_bytes(item.read_bytes())
                        except Exception as exc:
                            print("copy_training_outputs_warning", item, type(exc).__name__, exc, flush=True)
                copy_checkpoint_dirs(run_dir, run_dest)

        def copy_staged_gate_outputs(src, dest):
            src = Path(src)
            dest = Path(dest)
            if not src.exists():
                return
            gate_dirs = list(src.glob("**/phase_*_freeze_gate_*"))
            gate_dirs.extend(src.glob("**/phase_*_seed_gate_*"))
            for gate_dir in sorted(set(gate_dirs)):
                rel = gate_dir.relative_to(src)
                gate_dest = dest / rel
                gate_dest.mkdir(parents=True, exist_ok=True)
                for item in sorted(gate_dir.rglob("*")):
                    if item.is_dir() or item.suffix not in {{".md", ".json", ".txt"}}:
                        continue
                    try:
                        rel_item = item.relative_to(gate_dir)
                        dest_item = gate_dest / rel_item
                        dest_item.parent.mkdir(parents=True, exist_ok=True)
                        dest_item.write_bytes(item.read_bytes())
                    except Exception as exc:
                        print("copy_staged_gate_warning", item, type(exc).__name__, exc, flush=True)

        def bundle_artifacts():
            if not BUNDLE_LOCK.acquire(blocking=False):
                print("bundle_artifacts_skipped lock_held", flush=True)
                return
            try:
                OUT.mkdir(parents=True, exist_ok=True)
                (OUT / "COLAB_CLI_EXIT_STATUS.txt").write_text(
                    "exit_status=" + str(RUN_STATUS.get("exit_status", 0)) + "\\n"
                )
                (OUT / "COLAB_CLI_HEARTBEAT.json").write_text(
                    json.dumps(
                        {{
                            "generated_at": dt.datetime.now(dt.UTC).isoformat(),
                            "exit_status": RUN_STATUS.get("exit_status", 0),
                            "bundle_interval_s": ARTIFACT_BUNDLE_INTERVAL_S,
                        }},
                        indent=2,
                    )
                    + "\\n"
                )
                copy_training_outputs(
                    "/content/open_duck_training_smokes_cli",
                    OUT / "open_duck_training_smokes_cli",
                )
                copy_training_outputs(
                    "/content/open_duck_training_runs_cli",
                    OUT / "open_duck_training_runs_cli",
                )
                copy_training_outputs(
                    STAGED_ROOT,
                    OUT / "open_duck_staged_curriculum_cli",
                )
                copy_staged_gate_outputs(
                    STAGED_ROOT,
                    OUT / "open_duck_staged_curriculum_cli",
                )
                subprocess.run(
                    ["tar", "-czf", str(REMOTE_BUNDLE), "-C", str(OUT.parent), OUT.name],
                    check=False,
                    text=True,
                )
                print("COLAB_CLI_ARTIFACT", REMOTE_BUNDLE, flush=True)
            except Exception as exc:
                print("bundle_artifacts_warning", type(exc).__name__, exc, flush=True)
            finally:
                BUNDLE_LOCK.release()

        atexit.register(bundle_artifacts)

        def periodic_bundle_artifacts():
            if ARTIFACT_BUNDLE_INTERVAL_S <= 0:
                return
            while True:
                time.sleep(ARTIFACT_BUNDLE_INTERVAL_S)
                print("COLAB_CLI_PERIODIC_ARTIFACT_REFRESH", flush=True)
                bundle_artifacts()

        if ARTIFACT_BUNDLE_INTERVAL_S > 0:
            threading.Thread(
                target=periodic_bundle_artifacts,
                name="colab-artifact-heartbeat",
                daemon=True,
            ).start()

        def run(cmd, cwd=None, timeout=None, env=None, check=True):
            print("\\n>>>", " ".join(str(x) for x in cmd), flush=True)
            completed = subprocess.run(cmd, cwd=cwd, timeout=timeout, env=env, text=True)
            print("<<< returncode", completed.returncode, flush=True)
            if completed.returncode != 0:
                RUN_STATUS["exit_status"] = completed.returncode
                if check:
                    raise SystemExit(completed.returncode)
            return completed

        def run_seed_gate(policy, candidate_name, spec):
            gate_dir = OUT / f"{{candidate_name}}_{{spec['name']}}_seed_gate"
            gate_cmd = [
                PYTHON, "tools/run_candidate_seed_sweep.py",
                "--policies", f"{{candidate_name}}={{policy}}",
                "--fit-json", "outputs/analysis/actuator_response_fit_corrected_knee.json",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--seeds", "0-7",
                "--command-x", str(spec["command_x"]),
                "--task", "rough_terrain_backlash",
                "--duration", "15",
                "--bridge-mode", "fitted",
                "--mode-name", "fitted",
                "--jax-platform", "cpu",
                "--terrain-hfield-z-scale", str(spec["terrain_z"]),
                "--sim-preflight-timeout-s", "600",
                "--closed-loop-timeout-s", "2400",
                "--output-dir", str(gate_dir),
                "--output-md", str(gate_dir / "CANDIDATE_SEED_SWEEP.md"),
                "--output-json", str(gate_dir / "candidate_seed_sweep.json"),
                "--run",
            ]
            if spec.get("push"):
                gate_cmd.extend([
                    "--eval-push-enable",
                    "--eval-push-interval-min-s", "1.0",
                    "--eval-push-interval-max-s", "1.5",
                    "--eval-push-magnitude-min", "0.03",
                    "--eval-push-magnitude-max", "0.08",
                    "--push-recovery-window-s", "0.5",
                    "--push-recovery-max-abs-pitch-rad", "0.8",
                    "--push-recovery-min-base-height-m", "0.08",
                ])
            completed = run(gate_cmd, cwd=RDK, timeout=21600, check=False)
            gate_json = gate_dir / "candidate_seed_sweep.json"
            partial_json = gate_dir / "candidate_seed_sweep.partial.json"
            payload = None
            for candidate_json in (gate_json, partial_json):
                if candidate_json.exists():
                    try:
                        payload = json.loads(candidate_json.read_text())
                        break
                    except Exception as exc:
                        print("seed_gate_json_warning", candidate_json, type(exc).__name__, exc, flush=True)
            aggregate = (payload or {{}}).get("aggregate") or {{}}
            candidate_agg = aggregate.get(candidate_name) or {{}}
            return {{
                "name": spec["name"],
                "command_x": spec["command_x"],
                "terrain_z": spec["terrain_z"],
                "push": bool(spec.get("push")),
                "returncode": completed.returncode,
                "gate_dir": str(gate_dir),
                "result_json": str(gate_json),
                "partial_json": str(partial_json),
                "aggregate": candidate_agg,
            }}

        def run_phase2_z005_post_training_gates(policy, candidate_name):
            primary_label = "{phase2_primary_terrain_label}"
            primary_terrain_z = float("{phase2_primary_terrain_z}")
            gate_specs = [
                {{"name": f"{{primary_label}}_x008_no_push", "command_x": 0.08, "terrain_z": primary_terrain_z, "push": False}},
                {{"name": f"{{primary_label}}_x000_no_push", "command_x": 0.0, "terrain_z": primary_terrain_z, "push": False}},
                {{"name": "z002_x008_no_push_regression", "command_x": 0.08, "terrain_z": 0.002, "push": False}},
                {{"name": "z002_x000_no_push_regression", "command_x": 0.0, "terrain_z": 0.002, "push": False}},
                {{"name": "z002_x008_gentle_push_regression", "command_x": 0.08, "terrain_z": 0.002, "push": True}},
                {{"name": "z002_x000_gentle_push_regression", "command_x": 0.0, "terrain_z": 0.002, "push": True}},
            ]
            results = [run_seed_gate(policy, candidate_name, spec) for spec in gate_specs]
            manifest = {{
                "workflow": {args.workflow!r},
                "policy": str(policy),
                "candidate_name": candidate_name,
                "gate_specs": gate_specs,
                "results": results,
                "note": (
                    "Post-training gates are offline sim only. A gate hold is "
                    "reported as evidence and does not touch robot hardware."
                ),
            }}
            out_json = OUT / f"{{candidate_name}}_post_training_seed_gates.json"
            out_md = OUT / f"{{candidate_name}}_POST_TRAINING_SEED_GATES.md"
            out_json.write_text(json.dumps(manifest, indent=2) + "\\n")
            lines = [
                f"# Phase 2 {{primary_label}} Post-Training Seed Gates",
                "",
                f"candidate: `{{candidate_name}}`",
                f"policy: `{{policy}}`",
                "",
                "| gate | command_x | terrain_z | push | returncode | falls | duration_complete | track_ratio_mean | vx_mean | max_vel_excess_mean | tracking_p95_mean |",
                "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
            for item in results:
                agg = item.get("aggregate") or {{}}
                def stat_mean(name):
                    stats = agg.get(name) or {{}}
                    value = stats.get("mean")
                    return "NA" if value is None else f"{{float(value):.4f}}"
                lines.append(
                    f"| `{{item['name']}}` | {{item['command_x']}} | {{item['terrain_z']}} | "
                    f"`{{item['push']}}` | {{item['returncode']}} | "
                    f"{{agg.get('fall_count', 'NA')}} | "
                    f"{{agg.get('duration_complete_count', 'NA')}} | "
                    f"{{stat_mean('track_ratio')}} | "
                    f"{{stat_mean('mean_local_vx_m_s')}} | "
                    f"{{stat_mean('max_pitch_vel_limit_excess_rad_s')}} | "
                    f"{{stat_mean('max_tracking_p95_rad')}} |"
                )
            lines.extend([
                "",
                "## Interpretation",
                "",
                f"- The {{primary_label}} x=0.08 gate is the immediate terrain-rung target.",
                "- The z=0.002 no-push and gentle-push gates are regression checks for the packaged gain099 candidate behavior.",
                "- Robot validation remains blocked regardless of these results.",
            ])
            out_md.write_text("\\n".join(lines).rstrip() + "\\n")
            print("PHASE2_Z005_POST_TRAINING_GATES", out_json, flush=True)
            return manifest

        run(["rm", "-rf", str(RDK), str(PLAYGROUND)])
        run(["tar", "-xzf", "{rdk_tar}", "-C", "/content"])
        run(["tar", "-xzf", "{playground_tar}", "-C", "/content"])
        OUT.mkdir(parents=True, exist_ok=True)

        if {install_deps!r}:
            run([PYTHON, "-m", "pip", "install", "-U", "pip"], timeout=600)
            run([
                PYTHON, "-m", "pip", "install",
                "jax[cuda12]=={PINNED_JAX_VERSION}",
                "jaxlib=={PINNED_JAX_VERSION}",
                "playground==0.0.5",
                "mujoco==3.9.0",
                "mujoco-mjx==3.9.0",
                "onnxruntime==1.27.0",
                "ml-collections==1.1.0",
                "numpy==2.0.2",
                "matplotlib==3.10.0",
                "mediapy==1.2.6",
                "tensorflow==2.20.0",
                "protobuf==5.29.6",
                "onnx==1.22.0",
            ], timeout=1800)
            run([PYTHON, "-m", "pip", "install", "--no-deps", "tf2onnx==1.17.0"], timeout=600)
            run([PYTHON, "-m", "pip", "install", "--no-deps", "-e", str(PLAYGROUND)], timeout=600)

        print("=== Versions ===", flush=True)
        for name in ["jax", "jaxlib", "brax", "mujoco", "mujoco-mjx", "playground"]:
            try:
                print(name, metadata.version(name), flush=True)
            except Exception as exc:
                print(name, type(exc).__name__, exc, flush=True)
        run([PYTHON, "-c", "import jax; print('backend', jax.default_backend(), jax.devices()); print('has_device_put_replicated', hasattr(jax, 'device_put_replicated'))"])

        if {run_training_smoke_diagnostic!r}:
            run([
                PYTHON, "tools/diagnose_training_smoke_startup.py",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--platform", "gpu",
                "--jax-platforms", "cuda",
                "--output-dir", str(OUT / "training_smoke_startup_diagnostic"),
                "--smoke-num-timesteps", "{smoke_steps}",
                "--export-min-step", "{args.smoke_export_min_step}",
                "--ppo-num-envs", "{smoke_ppo_num_envs}",
                "--ppo-batch-size", "{smoke_ppo_batch_size}",
                "--run-smoke",
            ], cwd=RDK, timeout=1800)
            bundle_artifacts()

        if {run_audit!r}:
            run([
                PYTHON, "tools/audit_policy_sim_contract.py",
                "--policy", "policy/BEST_WALK_ONNX_2.onnx",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--instantiate-timeout-s", "600",
                "--output-md", str(OUT / "POLICY_SIM_CONTRACT_AUDIT_CUDA.md"),
                "--output-json", str(OUT / "policy_sim_contract_audit_cuda.json"),
            ], cwd=RDK, timeout=900)

        if {run_checkpoint_sweep!r}:
            sweep_policies = {checkpoint_sweep_policies}
            sweep_cmd = [
                PYTHON, "tools/sweep_candidate_checkpoints.py",
                "--policies", *sweep_policies,
                "--fit-json", "outputs/analysis/actuator_response_fit_corrected_knee.json",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--commands", "{checkpoint_sweep_commands}",
                "--duration", "{checkpoint_sweep_duration}",
                "--bridge-mode", "{checkpoint_sweep_bridge_mode}",
                "--mode-name", "{checkpoint_sweep_bridge_mode}",
                "--jax-platform", "{checkpoint_sweep_jax_platform}",
                "--sim-preflight-timeout-s", "600",
                "--closed-loop-timeout-s", "1800",
                "--output-dir", str(OUT / "candidate_checkpoint_sweep"),
                "--run",
            ]
            run(sweep_cmd, cwd=RDK, timeout={args.checkpoint_sweep_timeout_s})
            bundle_artifacts()

        if {run_baseline_eval!r}:
            run([
                PYTHON, "tools/eval_policy_with_actuator_bridge.py",
                "--mode", "closed-loop-sim",
                "--policy", "policy/BEST_WALK_ONNX_2.onnx",
                "--fit-json", "outputs/analysis/actuator_response_fit_corrected_knee.json",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--command-x", "0.08",
                "--duration", "15",
                "--bridge-mode", "all",
                "--jax-platform", "gpu",
                "--sim-preflight-timeout-s", "600",
                "--closed-loop-timeout-s", "1800",
                "--output-dir", str(OUT / "baseline_x008"),
            ], cwd=RDK, timeout=2400)

        if {run_smoke!r}:
            run([
                PYTHON, "tools/run_actuator_bridge_training_smoke.py",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--platform", "gpu",
                "--jax-platforms", "cuda",
                "--run",
                "--output-root", "/content/open_duck_training_smokes_cli",
                "--num-timesteps", "{smoke_steps}",
                "--export-min-step", "{args.smoke_export_min_step}",
                "--ppo-num-envs", "{smoke_ppo_num_envs}",
                "--ppo-num-evals", "1",
                "--ppo-episode-length", "50",
                "--ppo-unroll-length", "5",
                "--ppo-batch-size", "{smoke_ppo_batch_size}",
                "--ppo-num-minibatches", "1",
                "--ppo-num-updates-per-batch", "1",
                "--target-rate-scale", "-0.01",
                "--actuator-tracking-scale", "0.0",
                "--timeout-s", "1200",
            ], cwd=RDK, timeout=1500)
            copy_training_outputs(
                "/content/open_duck_training_smokes_cli",
                OUT / "open_duck_training_smokes_cli",
            )

        latest_onnx = None
        candidate_name = None
        training_manifest = None

        if {run_candidate_training!r}:
            candidate_training_cmd = [
                PYTHON, "tools/run_actuator_bridge_training_smoke.py",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--platform", "gpu",
                "--jax-platforms", "cuda",
                "--run",
                "--output-root", "/content/open_duck_training_runs_cli",
                "--num-timesteps", "{candidate_steps}",
                "--ppo-num-envs", "{args.candidate_ppo_num_envs}",
                "--ppo-num-evals", "{args.candidate_ppo_num_evals}",
                "--ppo-episode-length", "{args.candidate_episode_length}",
                "--ppo-unroll-length", "{args.candidate_unroll_length}",
                "--ppo-batch-size", "{args.candidate_ppo_batch_size}",
                "--ppo-num-minibatches", "{args.candidate_ppo_num_minibatches}",
                "--ppo-num-updates-per-batch", "{args.candidate_ppo_num_updates_per_batch}",
                "--target-rate-scale", "{candidate_target_rate_scale}",
                "--actuator-tracking-scale", "{candidate_actuator_tracking_scale}",
                "--tracking-lin-vel-scale", "{candidate_tracking_lin_vel_scale}",
                "--tracking-ang-vel-scale", "{candidate_tracking_ang_vel_scale}",
                "--tracking-sigma", "{candidate_tracking_sigma}",
                "--forward-progress-scale", "{candidate_forward_progress_scale}",
                "--forward-progress-deadband", "{candidate_forward_progress_deadband}",
                "--forward-shortfall-scale", "{candidate_forward_shortfall_scale}",
                "--forward-shortfall-required-ratio", "{candidate_forward_shortfall_required_ratio}",
                "--action-rate-scale", "{candidate_action_rate_scale}",
                "--action-magnitude-scale", "{candidate_action_magnitude_scale}",
                "--stand-still-scale", "{candidate_stand_still_scale}",
                "--alive-scale", "{candidate_alive_scale}",
                "--imitation-scale", "{candidate_imitation_scale}",
                "--lin-vel-x-min", "{candidate_lin_vel_x_min}",
                "--lin-vel-x-max", "{candidate_lin_vel_x_max}",
                "--lin-vel-y-min", "0.0",
                "--lin-vel-y-max", "0.0",
                "--ang-vel-yaw-min", "0.0",
                "--ang-vel-yaw-max", "0.0",
                "--command-resample-steps", "{args.candidate_command_resample_steps}",
                "--zero-command-probability", "{candidate_zero_command_probability}",
                "--head-range-factor", "0.0",
                {candidate_behavior_prior_arg}
                {candidate_disable_bridge_arg}
                "--actuator-bridge-delay-min-ticks", "{args.candidate_actuator_bridge_delay_min_ticks}",
                "--actuator-bridge-delay-max-ticks", "{args.candidate_actuator_bridge_delay_max_ticks}",
                "--actuator-bridge-tau-min-s", "{candidate_actuator_bridge_tau_min_s}",
                "--actuator-bridge-tau-max-s", "{candidate_actuator_bridge_tau_max_s}",
                "--actuator-bridge-velocity-limit-min-rad-s", "{candidate_actuator_bridge_velocity_limit_min_rad_s}",
                "--actuator-bridge-velocity-limit-max-rad-s", "{candidate_actuator_bridge_velocity_limit_max_rad_s}",
                "--actuator-bridge-per-joint-variation", "{candidate_actuator_bridge_per_joint_variation}",
                "--timeout-s", "{args.candidate_timeout_s}",
            ]
            if {candidate_restore_checkpoint_path!r}:
                candidate_training_cmd.extend([
                    "--restore-checkpoint-path",
                    {candidate_restore_checkpoint_path!r},
                ])
            if {args.candidate_ppo_learning_rate is not None!r}:
                candidate_training_cmd.extend([
                    "--ppo-learning-rate",
                    "{cli_value(args.candidate_ppo_learning_rate)}",
                ])
            if {args.candidate_ppo_entropy_cost is not None!r}:
                candidate_training_cmd.extend([
                    "--ppo-entropy-cost",
                    "{cli_value(args.candidate_ppo_entropy_cost)}",
                ])
            if {args.candidate_ppo_clipping_epsilon is not None!r}:
                candidate_training_cmd.extend([
                    "--ppo-clipping-epsilon",
                    "{cli_value(args.candidate_ppo_clipping_epsilon)}",
                ])
            if {args.candidate_ppo_max_grad_norm is not None!r}:
                candidate_training_cmd.extend([
                    "--ppo-max-grad-norm",
                    "{cli_value(args.candidate_ppo_max_grad_norm)}",
                ])
            run(candidate_training_cmd, cwd=RDK, timeout={args.candidate_timeout_s + 300})
            run_dirs = sorted(Path("/content/open_duck_training_runs_cli").glob("smoke_*_gpu"))
            if not run_dirs:
                raise SystemExit("candidate training produced no smoke_*_gpu run directory")
            run_dir = run_dirs[-1]
            onnx_files = sorted(run_dir.glob("*.onnx"))
            if not onnx_files:
                raise SystemExit(f"candidate training produced no ONNX files in {{run_dir}}")
            latest_onnx = onnx_files[-1]
            candidate_name = {args.candidate_name!r} or (
                "open_duck_mini_actuator_bridge_cli_"
                + dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
            )
            training_manifest = run_dir / "smoke_manifest.final.json"
            if not training_manifest.exists():
                training_manifest = run_dir / "smoke_manifest.start.json"
            run([
                PYTHON, "tools/summarize_training_run.py", str(run_dir),
                "--output-md", str(OUT / f"{{candidate_name}}_training_run_summary.md"),
                "--output-json", str(OUT / f"{{candidate_name}}_training_run_summary.json"),
            ], cwd=RDK, timeout=300, check=False)
            copy_training_outputs(
                "/content/open_duck_training_runs_cli",
                OUT / "open_duck_training_runs_cli",
            )

        if {run_phase2_cuda_recipe!r}:
            candidate_name = {args.candidate_name!r} or "{phase2_default_candidate_name}"
            phase2_b0d_cmd = [
                PYTHON, "tools/run_actuator_bridge_training_smoke.py",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--platform", "gpu",
                "--jax-platforms", "cuda",
                "--run",
                "--output-root", "{phase2_output_root}",
                "--task", "rough_terrain_backlash",
                "--num-timesteps", "{phase2_num_timesteps}",
                "--export-min-step", "1",
                "--ppo-num-envs", "{phase2_ppo_num_envs}",
                "--ppo-num-evals", "{phase2_ppo_num_evals}",
                "--ppo-episode-length", "{phase2_ppo_episode_length}",
                "--ppo-unroll-length", "20",
                "--ppo-batch-size", "{phase2_ppo_batch_size}",
                "--ppo-num-minibatches", "{phase2_ppo_num_minibatches}",
                "--ppo-num-updates-per-batch", "{phase2_ppo_num_updates_per_batch}",
                "--restore-checkpoint-path",
                "{phase2_restore_checkpoint}",
                "--ppo-learning-rate", "{phase2_lr}",
                "--ppo-entropy-cost", "0.001",
                "--ppo-clipping-epsilon", "{phase2_clip}",
                "--ppo-max-grad-norm", "{phase2_max_grad_norm}",
                "--restore-policy-kl-scale", "{phase2_restore_kl}",
                "--target-rate-scale", "{phase2_target_rate_scale}",
                "--actuator-tracking-scale", "{phase2_actuator_tracking}",
                {phase2_push_recovery_arg}
                {phase2_extra_args}
                {phase2_support_stability_arg}
                "--forward-progress-scale", "{phase2_forward_progress}",
                "--command-progress-scale", "{phase2_command_progress}",
                "--command-progress-shortfall-scale", "{phase2_command_shortfall}",
                "--command-progress-required-ratio", "{phase2_command_ratio}",
                "--command-progress-warmup-steps", "30",
                "--action-rate-huber-delta", "0.05",
                "--actuator-tracking-huber-delta", "0.03",
                "--action-rate-scale", "{phase2_action_rate_scale}",
                "--action-magnitude-scale", "{phase2_action_magnitude_scale}",
                "--base-height-scale", "{phase2_base_height_scale}",
                "--forward-pitch-scale", "{phase2_forward_pitch_scale}",
                "--forward-pitch-rate-scale", "{phase2_forward_pitch_rate_scale}",
                "--alive-scale", "2",
                "--imitation-scale", "0",
                "--lin-vel-x-min", "0.06",
                "--lin-vel-x-max", "0.1",
                "--lin-vel-y-min", "0",
                "--lin-vel-y-max", "0",
                "--ang-vel-yaw-min", "0",
                "--ang-vel-yaw-max", "0",
                "--command-resample-steps", "600",
                "--zero-command-probability", "0.15",
                "--dr-friction-min", "{phase2_dr_friction_min}",
                "--dr-friction-max", "{phase2_dr_friction_max}",
                "--dr-frictionloss-scale-min", "{phase2_dr_frictionloss_scale_min}",
                "--dr-frictionloss-scale-max", "{phase2_dr_frictionloss_scale_max}",
                "--dr-armature-scale-min", "{phase2_dr_armature_scale_min}",
                "--dr-armature-scale-max", "{phase2_dr_armature_scale_max}",
                "--dr-com-jitter-m", "{phase2_dr_com_jitter_m}",
                "--dr-mass-scale-min", "{phase2_dr_mass_scale_min}",
                "--dr-mass-scale-max", "{phase2_dr_mass_scale_max}",
                "--dr-torso-mass-delta-min", "{phase2_dr_torso_mass_delta_min}",
                "--dr-torso-mass-delta-max", "{phase2_dr_torso_mass_delta_max}",
                "--dr-qpos-jitter-rad", "{phase2_dr_qpos_jitter_rad}",
                "--dr-actuator-gain-scale-min", "{phase2_dr_actuator_gain_scale_min}",
                "--dr-actuator-gain-scale-max", "{phase2_dr_actuator_gain_scale_max}",
                "--dr-leg-geometry-jitter-scale", "{phase2_dr_leg_geometry_jitter_scale}",
                "--push-interval-min-s", "{phase2_push_interval_min_s}",
                "--push-interval-max-s", "{phase2_push_interval_max_s}",
                "--push-magnitude-min", "{phase2_push_magnitude_min}",
                "--push-magnitude-max", "{phase2_push_magnitude_max}",
                "--noise-level", "{phase2_noise_level}",
                "--noise-hip-pos", "{phase2_noise_joint_pos}",
                "--noise-knee-pos", "{phase2_noise_joint_pos}",
                "--noise-ankle-pos", "{phase2_noise_joint_pos}",
                "--noise-joint-vel", "{phase2_noise_joint_vel}",
                "--noise-gravity", "{phase2_noise_gravity}",
                "--noise-gyro", "{phase2_noise_gyro}",
                "--noise-accelerometer", "{phase2_noise_accelerometer}",
                {phase2_push_enable_arg}
                {phase2_behavior_prior_arg}
                "--actuator-bridge-delay-min-ticks", "3",
                "--actuator-bridge-delay-max-ticks", "{phase2_bridge_delay_max}",
                "--actuator-bridge-tau-min-s", "0.06",
                "--actuator-bridge-tau-max-s", "{phase2_bridge_tau_max}",
                "--actuator-bridge-velocity-limit-min-rad-s", "2",
                "--actuator-bridge-velocity-limit-max-rad-s", "3.25",
                "--actuator-bridge-per-joint-variation", "{phase2_bridge_per_joint_variation}",
                "--terrain-hfield-z-scale", "{phase2_terrain_hfield_z_scale}",
                "--timeout-s", "{args.candidate_timeout_s}",
                {phase2_final_training_args}
            ]
            run(phase2_b0d_cmd, cwd=RDK, timeout={args.candidate_timeout_s + 300})
            run_dirs = sorted(Path("{phase2_output_root}").glob("smoke_*_gpu"))
            if not run_dirs:
                raise SystemExit("{args.workflow} training produced no smoke_*_gpu run directory")
            run_dir = run_dirs[-1]
            onnx_files = sorted(run_dir.glob("*.onnx"))
            if not onnx_files:
                raise SystemExit(f"{args.workflow} training produced no ONNX files in {{run_dir}}")
            latest_onnx = onnx_files[-1]
            training_manifest = run_dir / "smoke_manifest.final.json"
            if not training_manifest.exists():
                training_manifest = run_dir / "smoke_manifest.start.json"
            run([
                PYTHON, "tools/summarize_training_run.py", str(run_dir),
                "--output-md", str(OUT / f"{{candidate_name}}_training_run_summary.md"),
                "--output-json", str(OUT / f"{{candidate_name}}_training_run_summary.json"),
            ], cwd=RDK, timeout=300, check=False)
            copy_training_outputs(
                "{phase2_output_root}",
                OUT / "open_duck_training_phase2_{phase2_recipe_id}_cli",
            )
            bundle_artifacts()
            if {args.candidate_checkpoint_sweep!r}:
                sweep_dir = OUT / f"{{candidate_name}}_checkpoint_sweep"
                sweep_cmd = [
                    PYTHON, "tools/sweep_candidate_checkpoints.py",
                    "--policies", *[str(path) for path in onnx_files],
                    "--fit-json", "outputs/analysis/actuator_response_fit_corrected_knee.json",
                    "--playground-path", str(PLAYGROUND),
                    "--env-python", PYTHON,
                    "--commands", "{candidate_checkpoint_sweep_commands}",
                    "--duration", "{candidate_checkpoint_sweep_duration}",
                    "--bridge-mode", "fitted",
                    "--mode-name", "fitted",
                    "--jax-platform", "{candidate_checkpoint_sweep_jax_platform}",
                    "--sim-preflight-timeout-s", "600",
                    "--closed-loop-timeout-s", "1800",
                    "--output-dir", str(sweep_dir),
                    "--run",
                ]
                run(sweep_cmd, cwd=RDK, timeout={args.candidate_checkpoint_sweep_timeout_s})
                sweep_json = sweep_dir / "candidate_checkpoint_sweep.json"
                if sweep_json.exists():
                    sweep_payload = json.loads(sweep_json.read_text())
                    decisions = sweep_payload.get("promotion_decisions") or []
                    promoted = [item for item in decisions if item.get("promote")]
                    selected = promoted[0] if promoted else (decisions[0] if decisions else None)
                    if selected:
                        selected_policy = Path(selected.get("policy") or "")
                        selected_status = selected.get("status")
                        selected_reason = (
                            "promoted_by_checkpoint_sweep"
                            if selected.get("promote")
                            else "best_available_but_not_promoted"
                        )
                        if selected_policy.exists():
                            latest_onnx = selected_policy
                            (OUT / f"{{candidate_name}}_selected_checkpoint.json").write_text(
                                json.dumps(
                                    {{
                                        "selected_policy": str(selected_policy),
                                        "selection_reason": selected_reason,
                                        "selection_status": selected_status,
                                        "promotion_decision": selected,
                                        "sweep_json": str(sweep_json),
                                    }},
                                    indent=2,
                                )
                                + "\\n"
                            )
                            print(
                                "CANDIDATE_SELECTED_CHECKPOINT",
                                selected_reason,
                                selected_status,
                                selected_policy,
                                flush=True,
                            )
                        else:
                            print(
                                "candidate_checkpoint_sweep_selected_missing",
                                selected_policy,
                                flush=True,
                            )
                else:
                    print("candidate_checkpoint_sweep_json_missing", sweep_json, flush=True)
            if {run_phase2_terrain_like and not args.phase2_skip_post_training_gates!r}:
                run_phase2_z005_post_training_gates(latest_onnx, candidate_name)
                post_gate_json = OUT / f"{{candidate_name}}_post_training_seed_gates.json"
                run([
                    PYTHON, "{phase2_post_training_reporter}",
                    str(post_gate_json),
                    "--output-md", str(OUT / f"{{candidate_name}}_POST_TRAINING_GATE_DECISION.md"),
                    "--output-json", str(OUT / f"{{candidate_name}}_post_training_gate_decision.json"),
                ], cwd=RDK, timeout=300, check=False)
            elif {run_phase2_terrain_like and args.phase2_skip_post_training_gates!r}:
                (OUT / f"{{candidate_name}}_post_training_gates_skipped.json").write_text(
                    json.dumps(
                        {{
                            "status": "SKIPPED_POST_TRAINING_GATES",
                            "reason": "phase2_skip_post_training_gates",
                            "selected_policy": str(latest_onnx),
                            "training_manifest": str(training_manifest),
                        }},
                        indent=2,
                    )
                    + "\\n"
                )
                print(
                    "PHASE2_POST_TRAINING_GATES_SKIPPED",
                    latest_onnx,
                    flush=True,
                )
            bundle_artifacts()

        elif {run_staged_curriculum!r}:
            candidate_name = {args.candidate_name!r} or (
                "open_duck_mini_staged_curriculum_cli_"
                + dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
            )
            staged_root = STAGED_ROOT
            run([
                PYTHON, "tools/plan_staged_curriculum_training.py",
                "--run",
                "--recipe", "{args.staged_recipe}",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--platform", "gpu",
                "--jax-platforms", "cuda",
                "--timesteps-scale", "{args.staged_timesteps_scale}",
                {staged_initial_restore_arg}
                {staged_stop_after_phase_arg}
                {staged_phase_gate_arg}
                "--phase-timeout-s", "{args.staged_phase_timeout_s}",
                "--output-root", str(staged_root),
                "--output-md", str(OUT / f"{{candidate_name}}_staged_curriculum_plan.md"),
                "--output-json", str(OUT / f"{{candidate_name}}_staged_curriculum_plan.json"),
                "--ppo-num-envs", "{args.candidate_ppo_num_envs}",
                "--ppo-num-evals", "{args.candidate_ppo_num_evals}",
                "--ppo-episode-length", "{args.candidate_episode_length}",
                "--ppo-unroll-length", "{args.candidate_unroll_length}",
                "--ppo-batch-size", "{args.candidate_ppo_batch_size}",
                "--ppo-num-minibatches", "{args.candidate_ppo_num_minibatches}",
                "--ppo-num-updates-per-batch", "{args.candidate_ppo_num_updates_per_batch}",
            ], cwd=RDK, timeout={args.staged_phase_timeout_s * staged_timeout_multiplier + staged_phase_gate_timeout_total + 900})
            staged_plan = OUT / f"{{candidate_name}}_staged_curriculum_plan.json"
            payload = json.loads(staged_plan.read_text())
            latest_onnx = Path(payload.get("final_candidate_onnx") or "")
            if not latest_onnx.exists():
                raise SystemExit(
                    f"staged curriculum produced no final ONNX: {{latest_onnx}}"
                )
            training_manifest = latest_onnx.parent / "smoke_manifest.final.json"
            if not training_manifest.exists():
                training_manifest = latest_onnx.parent / "smoke_manifest.start.json"
            if not training_manifest.exists():
                training_manifest = None
            copy_training_outputs(
                str(staged_root),
                OUT / "open_duck_staged_curriculum_cli",
            )
            bundle_artifacts()

        elif {run_candidate_eval_only!r}:
            latest_onnx = Path({candidate_remote_policy!r}) if {candidate_remote_policy!r} else None
            if latest_onnx is None or not latest_onnx.exists():
                raise SystemExit(
                    "candidate-eval-only requires --candidate-existing-policy "
                    "and the uploaded ONNX must exist in the Colab runtime"
                )
            candidate_name = {args.candidate_name!r} or (
                "open_duck_mini_actuator_bridge_eval_"
                + latest_onnx.stem
                + "_"
                + dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
            )
            if {candidate_remote_manifest!r}:
                training_manifest = Path({candidate_remote_manifest!r})
                if not training_manifest.exists():
                    print("candidate_eval_only_manifest_missing", training_manifest, flush=True)
                    training_manifest = None
            (OUT / f"{{candidate_name}}_existing_policy_path.txt").write_text(
                str(latest_onnx) + "\\n"
            )
            bundle_artifacts()

        if {run_candidate_gates!r}:
            for command_x, suffix in [("0.0", "x0"), ("0.08", "x008")]:
                gate_dir = OUT / f"{{candidate_name}}_gate_{{suffix}}"
                run([
                    PYTHON, "tools/eval_policy_with_actuator_bridge.py",
                    "--mode", "closed-loop-sim",
                    "--eval-role", "candidate",
                    "--policy", str(latest_onnx),
                    "--fit-json", "outputs/analysis/actuator_response_fit_corrected_knee.json",
                    "--playground-path", str(PLAYGROUND),
                    "--env-python", PYTHON,
                    "--command-x", command_x,
                    "--duration", "15",
                    "--bridge-mode", "all",
                    "--jax-platform", "gpu",
                    "--sim-preflight-timeout-s", "600",
                    "--closed-loop-timeout-s", "1800",
                    "--output-dir", str(gate_dir),
                ], cwd=RDK, timeout=2400)
                run(["cp", str(gate_dir / "CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md"), str(OUT / f"{{candidate_name}}_candidate_gate_{{suffix}}.md")])
                run(["cp", str(gate_dir / "closed_loop_actuator_bridge_eval.json"), str(OUT / f"{{candidate_name}}_candidate_gate_{{suffix}}.json")])
                bundle_artifacts()
            package_cmd = [
                PYTHON, "tools/package_candidate_policy.py", str(latest_onnx),
                "--candidate-name", candidate_name,
                "--contract-audit", str(OUT / "POLICY_SIM_CONTRACT_AUDIT_CUDA.md"),
                "--candidate-gate-x0", str(OUT / f"{{candidate_name}}_candidate_gate_x0.md"),
                "--candidate-gate-x008", str(OUT / f"{{candidate_name}}_candidate_gate_x008.md"),
                "--output-md", str(OUT / f"{{candidate_name}}_policy_package.md"),
                "--output-json", str(OUT / f"{{candidate_name}}_policy_metadata.json"),
            ]
            if training_manifest is not None and training_manifest.exists():
                package_cmd.extend(["--training-manifest", str(training_manifest)])
            else:
                package_cmd.extend([
                    "--allow-missing-evidence",
                    "--non-deployable-reason",
                    (
                        "Eval-only package: training manifest was not provided "
                        "in this Colab run. Sim gates must be reviewed before "
                        "any robot validation."
                    ),
                ])
            run(package_cmd, cwd=RDK, timeout=300, check=False)
            if {run_candidate_training!r}:
                copy_training_outputs(
                    "/content/open_duck_training_runs_cli",
                    OUT / "open_duck_training_runs_cli",
                )

        run([PYTHON, "-m", "pip", "freeze"], cwd=RDK)
        run(["bash", "-lc", f"nvidia-smi > {{OUT / 'nvidia_smi.txt'}} 2>&1 || true"], cwd=RDK)
        run(["bash", "-lc", f"{{PYTHON}} -m pip freeze > {{OUT / 'pip_freeze.txt'}}"], cwd=RDK)
        bundle_artifacts()
        atexit.unregister(bundle_artifacts)
        """
    ).strip() + "\n"


def poll_remote(
    session: str,
    run_dir: Path,
    remote_log: str,
    remote_exit: str,
    remote_bundle: str,
    remote_pid: str,
    interval_s: int,
    timeout_s: int,
    idle_no_sentinel_polls_limit: int,
) -> None:
    deadline = time.time() + timeout_s
    last_log_size: int | None = None
    unchanged_log_polls = 0
    idle_no_exit_polls = 0
    last_status = ""
    log_dest = run_dir / "remote_live.log"
    while time.time() < deadline:
        if colab_file_exists(session, remote_exit):
            break
        if colab_file_exists(session, remote_log):
            subprocess.run(
                ["colab", "download", "-s", session, remote_log, str(log_dest)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if log_dest.exists():
                log_size = log_dest.stat().st_size
                if last_log_size == log_size:
                    unchanged_log_polls += 1
                else:
                    unchanged_log_polls = 0
                    last_log_size = log_size
                lines = log_dest.read_text(errors="replace").splitlines()
                print("\n".join(lines[-12:]), flush=True)
        if colab_file_exists(session, remote_bundle):
            partial_dest = run_dir / (Path(remote_bundle).name + ".partial")
            subprocess.run(
                ["colab", "download", "-s", session, remote_bundle, str(partial_dest)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if partial_dest.exists():
                print(f"PARTIAL_ARTIFACT {partial_dest} size={partial_dest.stat().st_size}", flush=True)
        last_status = colab_status_text(session)
        remote_is_idle = colab_status_is_idle(last_status)
        remote_running = (
            remote_process_is_running(session, remote_pid, run_dir)
            if remote_is_idle and not colab_file_exists(session, remote_exit)
            else None
        )
        if (
            remote_is_idle
            and remote_running is False
            and colab_file_exists(session, remote_bundle)
        ):
            print(
                "REMOTE_IDLE_WITH_BUNDLE_NO_SENTINEL",
                remote_bundle,
                flush=True,
            )
            break
        if remote_is_idle and remote_running:
            idle_no_exit_polls = 0
        elif remote_is_idle and not colab_file_exists(session, remote_exit):
            idle_no_exit_polls += 1
        else:
            idle_no_exit_polls = 0
        if (
            remote_is_idle
            and not colab_file_exists(session, remote_exit)
            and idle_no_exit_polls >= idle_no_sentinel_polls_limit
            and not colab_file_exists(session, remote_bundle)
        ):
            partial_output_dir = download_partial_output_dir(
                session, remote_bundle, run_dir
            )
            evidence = {
                "status": "HOLD_REMOTE_NO_SENTINEL",
                "session": session,
                "remote_log": remote_log,
                "remote_exit": remote_exit,
                "remote_pid": remote_pid,
                "remote_bundle": remote_bundle,
                "remote_output_dir": remote_output_dir_for_bundle(remote_bundle),
                "local_partial_output_dir": str(partial_output_dir)
                if partial_output_dir
                else None,
                "unchanged_log_polls": unchanged_log_polls,
                "idle_no_exit_polls": idle_no_exit_polls,
                "idle_no_sentinel_polls_limit": idle_no_sentinel_polls_limit,
                "remote_process_running": remote_running,
                "poll_interval_s": interval_s,
                "local_live_log": str(log_dest),
                "colab_status": last_status,
                "interpretation": (
                    "The Colab session reported idle while the workflow exit "
                    "sentinel was missing and the remote log stopped growing. "
                    "Treat the run as incomplete and inspect/download any "
                    "partial artifacts manually before reusing checkpoints."
                ),
            }
            (run_dir / "REMOTE_NO_SENTINEL.json").write_text(
                json.dumps(evidence, indent=2, sort_keys=True) + "\n"
            )
            (run_dir / "REMOTE_NO_SENTINEL.md").write_text(
                "\n".join(
                    [
                        "# Remote Colab Workflow Lost Sentinel",
                        "",
                        "status: `HOLD_REMOTE_NO_SENTINEL`",
                        "",
                        f"- session: `{session}`",
                        f"- remote_log: `{remote_log}`",
                        f"- remote_exit: `{remote_exit}`",
                        f"- remote_pid: `{remote_pid}`",
                        f"- remote_bundle: `{remote_bundle}`",
                        f"- remote_output_dir: `{remote_output_dir_for_bundle(remote_bundle)}`",
                        f"- local_partial_output_dir: `{partial_output_dir}`",
                        f"- unchanged_log_polls: `{unchanged_log_polls}`",
                        f"- idle_no_exit_polls: `{idle_no_exit_polls}`",
                        f"- idle_no_sentinel_polls_limit: `{idle_no_sentinel_polls_limit}`",
                        f"- remote_process_running: `{remote_running}`",
                        f"- poll_interval_s: `{interval_s}`",
                        "",
                        "The Colab session reported idle while the workflow "
                        "exit sentinel was missing and the downloaded remote "
                        "log stopped growing. This means the remote job should "
                        "be treated as incomplete, even if partial checkpoints "
                        "or logs exist.",
                        "",
                        "Do not promote partial checkpoints without an "
                        "explicit local gate and evidence summary.",
                        "",
                    ]
                )
            )
            raise SystemExit("HOLD_REMOTE_NO_SENTINEL: Colab workflow disappeared without exit sentinel")
        time.sleep(interval_s)
    else:
        partial_output_dir = download_partial_output_dir(session, remote_bundle, run_dir)
        timeout_evidence = {
            "status": "HOLD_REMOTE_TIMEOUT",
            "session": session,
            "remote_log": remote_log,
            "remote_exit": remote_exit,
            "remote_pid": remote_pid,
            "remote_bundle": remote_bundle,
            "remote_output_dir": remote_output_dir_for_bundle(remote_bundle),
            "local_partial_output_dir": str(partial_output_dir)
            if partial_output_dir
            else None,
            "timeout_s": timeout_s,
            "last_colab_status": last_status,
        }
        (run_dir / "REMOTE_TIMEOUT.json").write_text(
            json.dumps(timeout_evidence, indent=2, sort_keys=True) + "\n"
        )
        raise SystemExit(f"Timed out waiting for {remote_exit}")

    download_remote_results(session, run_dir, remote_log, remote_exit, remote_bundle)


def download_remote_results(
    session: str,
    run_dir: Path,
    remote_log: str,
    remote_exit: str,
    remote_bundle: str,
) -> None:
    if colab_file_exists(session, remote_exit):
        run(["colab", "download", "-s", session, remote_exit, str(run_dir / Path(remote_exit).name)])
    if colab_file_exists(session, remote_log):
        run(["colab", "download", "-s", session, remote_log, str(run_dir / Path(remote_log).name)])
    if colab_file_exists(session, remote_bundle):
        bundle_dest = run_dir / Path(remote_bundle).name
        run(["colab", "download", "-s", session, remote_bundle, str(bundle_dest)])
        extract_dir = run_dir / "artifact"
        extract_dir.mkdir(exist_ok=True)
        with tarfile.open(bundle_dest) as tf:
            tf.extractall(extract_dir)
        print(f"DOWNLOADED_ARTIFACT {bundle_dest}", flush=True)
    else:
        print(f"REMOTE_BUNDLE_MISSING {remote_bundle}", flush=True)


def write_package_only_manifest(
    run_dir: Path,
    workflow: str,
    session: str,
    rdk_tar: Path,
    playground_tar: Path,
    rdk_root: Path,
    playground_root: Path,
    argv: list[str],
    extra_required_paths: list[str] | None = None,
) -> None:
    payload = {
        "status": "PASS_COLAB_PACKAGE_ONLY_READY",
        "workflow": workflow,
        "session": session,
        "source": {
            "rdk": git_summary(rdk_root),
            "playground": git_summary(playground_root),
            "argv": argv,
            "jax_pin": PINNED_JAX_VERSION,
        },
        "archives": {
            "rdk": {
                "path": str(rdk_tar),
                "size_bytes": rdk_tar.stat().st_size,
                "sha256": file_sha256(rdk_tar),
            },
            "playground": {
                "path": str(playground_tar),
                "size_bytes": playground_tar.stat().st_size,
                "sha256": file_sha256(playground_tar),
            },
        },
        "required_rdk_package_paths": required_rdk_package_paths(
            workflow, extra_required_paths
        ),
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
        "uploaded_to_colab": False,
    }
    output_json = run_dir / "PACKAGE_ONLY_MANIFEST.json"
    output_md = run_dir / "PACKAGE_ONLY_MANIFEST.md"
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Colab Package-Only Manifest",
        "",
        f"status: `{payload['status']}`",
        f"workflow: `{workflow}`",
        f"session: `{session}`",
        "",
        "This local check built the upload archives only. It did not upload, train, SSH, deploy, or touch the robot.",
        "",
        "## Archives",
        "",
        "| archive | size bytes | sha256 | path |",
        "|---|---:|---|---|",
    ]
    for name, item in payload["archives"].items():
        lines.append(
            f"| `{name}` | {item['size_bytes']} | `{item['sha256']}` | `{item['path']}` |"
        )
    lines.extend(["", "## Source", ""])
    for name, item in payload["source"].items():
        if isinstance(item, dict):
            lines.append(
                f"- `{name}`: branch `{item.get('branch')}`, head `{item.get('head')}`, "
                f"tracked_dirty `{item.get('tracked_dirty')}`, untracked_count `{item.get('untracked_count')}`"
            )
    lines.append(f"- `jax_pin`: `{payload['source']['jax_pin']}`")
    lines.extend(["", "## Required RDK Package Paths", ""])
    for item in payload["required_rdk_package_paths"]:
        lines.append(f"- `{item}`")
    lines.append("")
    output_md.write_text("\n".join(lines))
    print(f"PACKAGE_ONLY_MANIFEST {output_json}", flush=True)


def repo_relative_existing_path(path_value: str | None, root: Path) -> str | None:
    if not path_value:
        return None
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Open Duck CUDA workflow through google-colab-cli.")
    parser.add_argument("--session", default=DEFAULT_SESSION)
    parser.add_argument("--rdk-root", default=str(ROOT))
    parser.add_argument("--playground-root", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--upload-root", default=str(DEFAULT_UPLOAD_ROOT))
    parser.add_argument(
        "--workflow",
        choices=[
            "eval",
            "smoke",
            "training-smoke",
            "training-smoke-diagnostic",
            "candidate",
            "candidate-only",
            "candidate-eval-only",
            "checkpoint-sweep",
            "phase2-b0d",
            "phase2-b0e",
            "phase2-b0f",
            "phase2-b0g",
            "phase2-z002-tracking-margin",
            "phase2-z002-teacher-continuity",
            "phase2-z0025-boundary",
            "phase2-z0035-motion-floor",
            "phase2-right-swing-structural",
            "phase2-right-swing-phase-lift",
            "phase2-right-swing-phase-advance",
            "phase2-right-swing-phase-single-support",
            "phase2-z005-support",
            "phase2-z005-motion-floor",
            "staged-curriculum",
            "all",
        ],
        default="eval",
    )
    parser.add_argument("--run", action="store_true", help="execute; default is plan-only")
    parser.add_argument(
        "--package-only",
        action="store_true",
        help=(
            "Build local upload tarballs and write a package manifest, then exit "
            "without initializing Colab, uploading, or starting remote work."
        ),
    )
    parser.add_argument("--skip-deps", action="store_true", help="reuse remote dependencies")
    parser.add_argument(
        "--skip-audit",
        action="store_true",
        help=(
            "Skip the repeated policy/sim contract audit in the remote workflow. "
            "Use only after the 101/14 contract has already been verified."
        ),
    )
    parser.add_argument("--no-poll", action="store_true", help="start remote job and return")
    parser.add_argument(
        "--foreground-remote",
        action="store_true",
        help=(
            "Run the remote driver in the foreground inside colab console. "
            "Use this for tiny smoke tests when detached setsid jobs disappear "
            "without writing an exit sentinel."
        ),
    )
    parser.add_argument(
        "--foreground-remote-timeout-s",
        type=int,
        default=1800,
        help="Console timeout for --foreground-remote.",
    )
    parser.add_argument(
        "--exec-remote",
        action="store_true",
        help=(
            "Run the generated remote driver through `colab exec` instead of "
            "raw console. This is intended for sessions where console/detached "
            "jobs disappear before writing an exit sentinel."
        ),
    )
    parser.add_argument(
        "--exec-remote-timeout-s",
        type=int,
        default=14400,
        help="Execution timeout for --exec-remote.",
    )
    parser.add_argument("--poll-interval-s", type=int, default=60)
    parser.add_argument(
        "--idle-no-sentinel-polls",
        type=int,
        default=5,
        help=(
            "Number of consecutive IDLE polls without an exit sentinel before "
            "declaring HOLD_REMOTE_NO_SENTINEL when no artifact bundle exists."
        ),
    )
    parser.add_argument(
        "--remote-artifact-interval-s",
        type=int,
        default=0,
        help=(
            "When >0, the generated remote driver periodically refreshes the "
            "artifact bundle and heartbeat while long training subprocesses "
            "are running. This is intended for Colab sessions that disappear "
            "before the final exit sentinel."
        ),
    )
    parser.add_argument("--timeout-s", type=int, default=7200)
    parser.add_argument("--smoke-num-timesteps", type=int, default=64)
    parser.add_argument("--smoke-ppo-num-envs", type=int, default=8)
    parser.add_argument("--smoke-ppo-batch-size", type=int, default=8)
    parser.add_argument(
        "--smoke-export-min-step",
        type=int,
        default=1,
        help=(
            "Pass --export-min-step to the tiny training-smoke run. The "
            "default skips step-0 ONNX export so the smoke isolates PPO "
            "execution and final-manifest behavior."
        ),
    )
    parser.add_argument("--candidate-num-timesteps", type=int, default=200000)
    parser.add_argument(
        "--phase2-num-timesteps",
        type=int,
        default=None,
        help=(
            "Override the hard-coded Phase 2 workflow training length. "
            "Use for tiny foreground diagnostics only; omit for registered full runs."
        ),
    )
    parser.add_argument(
        "--phase2-ppo-num-envs",
        type=int,
        default=None,
        help="Override Phase 2 PPO env count for bounded diagnostics.",
    )
    parser.add_argument(
        "--phase2-ppo-num-evals",
        type=int,
        default=None,
        help="Override Phase 2 PPO eval count for bounded diagnostics.",
    )
    parser.add_argument(
        "--phase2-episode-length",
        type=int,
        default=None,
        help="Override Phase 2 PPO episode length for bounded diagnostics.",
    )
    parser.add_argument(
        "--phase2-ppo-batch-size",
        type=int,
        default=None,
        help="Override Phase 2 PPO batch size for bounded diagnostics.",
    )
    parser.add_argument(
        "--phase2-ppo-num-minibatches",
        type=int,
        default=None,
        help="Override Phase 2 PPO minibatch count for bounded diagnostics.",
    )
    parser.add_argument(
        "--phase2-ppo-num-updates-per-batch",
        type=int,
        default=None,
        help="Override Phase 2 PPO updates per batch for bounded diagnostics.",
    )
    parser.add_argument(
        "--phase2-restore-checkpoint-path",
        default=None,
        help=(
            "Override the restore checkpoint used by Phase 2 workflows. "
            "Relative paths resolve under /content/open-duck-mini-rdkx5."
        ),
    )
    parser.add_argument(
        "--phase2-terrain-hfield-z-scale",
        type=float,
        default=None,
        help=(
            "Override the terrain hfield z-scale used by Phase 2 terrain "
            "workflows and their post-training primary gate."
        ),
    )
    parser.add_argument(
        "--phase2-target-rate-scale",
        type=float,
        default=None,
        help="Override Phase 2 target-rate penalty scale.",
    )
    parser.add_argument(
        "--phase2-actuator-tracking-scale",
        type=float,
        default=None,
        help="Override Phase 2 actuator-tracking penalty scale.",
    )
    parser.add_argument(
        "--phase2-forward-progress-scale",
        type=float,
        default=None,
        help="Override Phase 2 forward-progress reward scale.",
    )
    parser.add_argument(
        "--phase2-command-progress-scale",
        type=float,
        default=None,
        help="Override Phase 2 command-progress reward scale.",
    )
    parser.add_argument(
        "--phase2-command-progress-shortfall-scale",
        type=float,
        default=None,
        help="Override Phase 2 command-progress shortfall penalty scale.",
    )
    parser.add_argument(
        "--phase2-command-progress-required-ratio",
        type=float,
        default=None,
        help="Override Phase 2 command-progress required ratio.",
    )
    parser.add_argument(
        "--phase2-forward-swing-target-rate-limit-scale",
        type=float,
        default=None,
        help=(
            "Enable the existing Playground phase-swing target-rate-limit "
            "cost for Phase 2 workflows. Use a negative value to penalize "
            "swing target-rate excess."
        ),
    )
    parser.add_argument(
        "--phase2-forward-swing-target-rate-limit-joint-indices",
        default=None,
        help=(
            "Comma-separated actuator indices for "
            "--phase2-forward-swing-target-rate-limit-scale."
        ),
    )
    parser.add_argument(
        "--phase2-forward-swing-target-rate-limit-values",
        default=None,
        help=(
            "Comma-separated rad/s limits matching "
            "--phase2-forward-swing-target-rate-limit-joint-indices."
        ),
    )
    parser.add_argument(
        "--phase2-forward-swing-target-rate-limit-huber-delta",
        type=float,
        default=None,
        help=(
            "Pseudo-Huber delta for the Phase 2 swing target-rate-limit cost. "
            "Defaults to 0.05 when the cost is enabled."
        ),
    )
    parser.add_argument(
        "--phase2-skip-post-training-gates",
        action="store_true",
        help=(
            "For Phase 2 workflows, stop after training artifacts are packaged. "
            "Use this when Colab transport is unstable during the slower CPU gate; "
            "run gates later from the downloaded ONNX."
        ),
    )
    parser.add_argument(
        "--phase2-final-training-args-json",
        default=None,
        help=(
            "JSON list of strings appended to the final Phase 2 training command. "
            "This is for bounded recipe probes where explicit duplicate argparse "
            "options should override workflow defaults."
        ),
    )
    parser.add_argument(
        "--checkpoint-sweep-policies",
        nargs="+",
        default=[
            "policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/candidate.onnx",
            "policy/candidates/movement_bootstrap_v8_overshoot_stabilized_standstill_20260623/candidate.onnx",
            "policy/candidates/movement_bootstrap_v9_progress_balanced_standstill_20260623/candidate.onnx",
        ],
        help=(
            "Policy ONNX paths, relative to the uploaded RDK repo unless "
            "absolute, for --workflow checkpoint-sweep."
        ),
    )
    parser.add_argument("--checkpoint-sweep-commands", default="0.08")
    parser.add_argument("--checkpoint-sweep-duration", type=float, default=5.0)
    parser.add_argument("--checkpoint-sweep-bridge-mode", default="fitted")
    parser.add_argument(
        "--checkpoint-sweep-jax-platform",
        choices=["cpu", "gpu"],
        default="cpu",
        help=(
            "JAX platform for --workflow checkpoint-sweep. CPU is the default "
            "because single-policy MJX eval can be more reliable than GPU "
            "worker preflight on hosted runtimes."
        ),
    )
    parser.add_argument("--checkpoint-sweep-timeout-s", type=int, default=3600)
    parser.add_argument(
        "--staged-timesteps-scale",
        type=float,
        default=1.0,
        help=(
            "Scale the three staged-curriculum phase lengths. The base phases "
            "depend on --staged-recipe."
        ),
    )
    parser.add_argument(
        "--staged-recipe",
        choices=[
            "movement_bootstrap_v24",
            "movement_bootstrap_v23",
            "movement_bootstrap_v22",
            "movement_bootstrap_v20",
            "movement_bootstrap_v21",
            "movement_bootstrap_v19",
            "movement_bootstrap_v18",
            "movement_bootstrap_v17",
            "movement_bootstrap_v16",
            "movement_bootstrap_v15",
            "movement_bootstrap_v14",
            "movement_bootstrap_v13",
            "movement_bootstrap_v12",
            "movement_bootstrap_v11",
            "movement_bootstrap_v10",
            "movement_bootstrap_v9",
            "movement_bootstrap_v8",
            "movement_bootstrap_v7",
            "movement_bootstrap_v6",
            "movement_bootstrap_v5",
            "movement_bootstrap_v4",
            "movement_bootstrap_v3",
            "movement_bootstrap_v2",
            "shortfall_v1",
        ],
        default="movement_bootstrap_v20",
        help=(
            "Recipe passed to tools/plan_staged_curriculum_training.py for "
            "--workflow staged-curriculum. The current default is "
            "movement_bootstrap_v20, a reference/imitation-gait seed experiment "
            "using the synthesized x=0.04 reference override after V19 showed "
            "the raw nearest reference was command-mismatched. "
            "movement_bootstrap_v21 is available as an explicit next recipe: "
            "a weak-soft-prior x=0.04 learner using compact fragment priors, "
            "but it is not the default so future launches do not change "
            "silently. movement_bootstrap_v22 is a stronger step-phased "
            "prior-lock diagnostic after V21 trained but stayed far from the "
            "prior; it is also explicit-only. movement_bootstrap_v23 is the "
            "explicit single-support/contact objective probe after the "
            "target-source branch held; it is also explicit-only. "
            "movement_bootstrap_v24 is the explicit transition/propulsion "
            "follow-up after V23 learned double-support standstill; it is "
            "also explicit-only. "
            "movement_bootstrap_v19 is the preserved raw-reference seed "
            "experiment after V18 showed the immediate reward signal already "
            "prefers forward motion but cold-start PPO still failed at x=0.04. "
            "movement_bootstrap_v18 is the preserved minimal x=0.04 "
            "low-command discovery experiment that held. "
            "movement_bootstrap_v17 is a fresh hard signed-progress structural "
            "break after V16 showed no usable V5-anchor branch point. "
            "movement_bootstrap_v16 returns to the recovered V5 moving "
            "checkpoint and should be run with --staged-initial-restore-checkpoint. "
            "movement_bootstrap_v15 separates no-bridge gait discovery from "
            "mild/fitted actuator transfer after the V14 partial checkpoint "
            "remained low-motion. movement_bootstrap_v14 starts "
            "with a mild bridge for motion discovery before transferring to "
            "the fitted actuator envelope. "
            "movement_bootstrap_v6 explicitly "
            "targets continuity from the in-envelope phase-1 lead. "
            "movement_bootstrap_v7 is intended to be run with "
            "--staged-initial-restore-checkpoint pointing at the recovered "
            "v5 phase-1 checkpoint; movement_bootstrap_v8 is intended to start "
            "from the v7 anchored checkpoint and target the x=0.08 lunge; "
            "movement_bootstrap_v9 starts from v7 again with lighter damping "
            "after v8 stabilized into standstill; movement_bootstrap_v10 "
            "targets the multi-seed V7/V9 failure surfaces; "
            "movement_bootstrap_v11 starts a fresh hard-progress lineage after "
            "V10 failed mostly by freezing; movement_bootstrap_v12 adds "
            "command-progress failure to invalidate V11-style no-motion; "
            "movement_bootstrap_v13 makes that failure carry signed negative "
            "reward."
        ),
    )
    parser.add_argument(
        "--staged-phase-timeout-s",
        type=int,
        default=10800,
        help="Per-phase timeout for --workflow staged-curriculum.",
    )
    parser.add_argument(
        "--staged-stop-after-phase",
        type=int,
        default=None,
        help=(
            "Pass through to the staged planner to stop after this 1-based "
            "phase. Useful for recovering a trainable intermediate checkpoint."
        ),
    )
    parser.add_argument(
        "--staged-initial-restore-checkpoint",
        default=None,
        help=(
            "Checkpoint path visible inside the Colab runtime to use as the "
            "starting point for phase 1 of a staged-curriculum workflow."
        ),
    )
    parser.add_argument(
        "--staged-phase-gate-freeze-check",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Run a short candidate gate after each staged phase and stop on "
            "low forward progress. Enabled by default for staged workflows."
        ),
    )
    parser.add_argument("--staged-phase-gate-command-x", type=float, default=None)
    parser.add_argument("--staged-phase-gate-duration-s", type=float, default=5.0)
    parser.add_argument(
        "--staged-phase-gate-bridge-mode",
        choices=["vanilla", "fitted", "stress", "all"],
        default="fitted",
    )
    parser.add_argument(
        "--staged-phase-gate-platform",
        choices=["cpu", "gpu"],
        default="gpu",
    )
    parser.add_argument("--staged-phase-gate-timeout-s", type=int, default=900)
    parser.add_argument(
        "--staged-phase-gate-seeds",
        default="0-3",
        help=(
            "Seeds for staged multi-seed phase gates. Use an empty string to "
            "fall back to the legacy single-rollout gate."
        ),
    )
    parser.add_argument(
        "--staged-phase-gate-max-fall-fraction",
        type=float,
        default=0.0,
    )
    parser.add_argument(
        "--staged-phase-gate-min-track-ratio-mean",
        type=float,
        default=0.25,
    )
    parser.add_argument(
        "--staged-phase-gate-min-vx-mean",
        type=float,
        default=0.02,
    )
    parser.add_argument("--candidate-ppo-num-envs", type=int, default=256)
    parser.add_argument("--candidate-ppo-num-evals", type=int, default=4)
    parser.add_argument("--candidate-episode-length", type=int, default=600)
    parser.add_argument("--candidate-unroll-length", type=int, default=10)
    parser.add_argument("--candidate-ppo-batch-size", type=int, default=256)
    parser.add_argument("--candidate-ppo-num-minibatches", type=int, default=4)
    parser.add_argument("--candidate-ppo-num-updates-per-batch", type=int, default=4)
    parser.add_argument("--candidate-ppo-learning-rate", type=float, default=None)
    parser.add_argument("--candidate-ppo-entropy-cost", type=float, default=None)
    parser.add_argument("--candidate-ppo-clipping-epsilon", type=float, default=None)
    parser.add_argument("--candidate-ppo-max-grad-norm", type=float, default=None)
    parser.add_argument(
        "--candidate-restore-checkpoint-path",
        default=None,
        help=(
            "Optional checkpoint path visible inside the Colab runtime. Use "
            "this only after uploading or packaging the checkpoint separately."
        ),
    )
    parser.add_argument(
        "--candidate-existing-policy",
        help=(
            "Local ONNX path to upload and evaluate with --workflow "
            "candidate-eval-only. This avoids rerunning training when a prior "
            "Colab job disconnected during gate evaluation."
        ),
    )
    parser.add_argument(
        "--candidate-training-manifest",
        help=(
            "Optional local smoke_manifest JSON to upload with "
            "--workflow candidate-eval-only for candidate packaging."
        ),
    )
    parser.add_argument(
        "--candidate-name",
        help="Optional stable candidate name for training or eval-only packages.",
    )
    parser.add_argument(
        "--artifact-checkpoint-mode",
        choices=["none", "latest", "all"],
        default="latest",
        help=(
            "Checkpoint directories to include in downloaded Colab artifacts. "
            "latest preserves one continuation point per training run without "
            "copying every intermediate checkpoint."
        ),
    )
    parser.add_argument(
        "--candidate-checkpoint-sweep",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "After candidate training, sweep every exported ONNX through a "
            "compact x=0/x=0.08 fitted-bridge gate and use a promoted "
            "checkpoint for final gates when one exists. This prevents "
            "reward-only latest-checkpoint selection."
        ),
    )
    parser.add_argument(
        "--candidate-checkpoint-sweep-commands",
        default="0.0,0.08",
        help="Commands for the post-training compact checkpoint sweep.",
    )
    parser.add_argument(
        "--candidate-checkpoint-sweep-duration",
        type=float,
        default=1.0,
        help=(
            "Duration in seconds for each compact checkpoint-sweep rollout. "
            "Final candidate gates still run the normal longer duration."
        ),
    )
    parser.add_argument(
        "--candidate-checkpoint-sweep-jax-platform",
        choices=["cpu", "gpu"],
        default="cpu",
        help=(
            "JAX platform for the post-training compact checkpoint sweep. "
            "Training still uses GPU; CPU is the default here because the "
            "A100 GPU sweep path can wedge in MJX eval preflight while CPU "
            "completes the same gate."
        ),
    )
    parser.add_argument(
        "--candidate-checkpoint-sweep-timeout-s",
        type=int,
        default=7200,
        help="Remote timeout for the post-training checkpoint sweep.",
    )
    parser.add_argument("--candidate-timeout-s", type=int, default=10800)
    parser.add_argument("--candidate-target-rate-scale", type=float, default=-0.001)
    parser.add_argument("--candidate-actuator-tracking-scale", type=float, default=0.0)
    parser.add_argument("--candidate-tracking-lin-vel-scale", type=float, default=12.0)
    parser.add_argument("--candidate-tracking-ang-vel-scale", type=float, default=0.0)
    parser.add_argument("--candidate-tracking-sigma", type=float, default=0.0025)
    parser.add_argument("--candidate-forward-progress-scale", type=float, default=2.0)
    parser.add_argument("--candidate-forward-progress-deadband", type=float, default=0.02)
    parser.add_argument("--candidate-forward-shortfall-scale", type=float, default=0.0)
    parser.add_argument(
        "--candidate-forward-shortfall-required-ratio",
        type=float,
        default=0.5,
    )
    parser.add_argument("--candidate-action-rate-scale", type=float, default=-0.1)
    parser.add_argument("--candidate-action-magnitude-scale", type=float, default=-0.05)
    parser.add_argument("--candidate-stand-still-scale", type=float, default=-0.2)
    parser.add_argument("--candidate-alive-scale", type=float, default=0.5)
    parser.add_argument("--candidate-imitation-scale", type=float, default=0.25)
    parser.add_argument("--candidate-lin-vel-x-min", type=float, default=0.04)
    parser.add_argument("--candidate-lin-vel-x-max", type=float, default=0.12)
    parser.add_argument("--candidate-command-resample-steps", type=int, default=500)
    parser.add_argument("--candidate-zero-command-probability", type=float, default=0.1)
    parser.add_argument(
        "--candidate-behavior-prior-mlp-npz",
        default=None,
        help=(
            "Optional frozen MLP NPZ to use as a state-conditioned behavior "
            "prior during candidate PPO training. Relative paths are resolved "
            "inside /content/open-duck-mini-rdkx5."
        ),
    )
    parser.add_argument("--candidate-behavior-prior-scale", type=float, default=-0.05)
    parser.add_argument(
        "--candidate-behavior-prior-huber-delta", type=float, default=0.05
    )
    parser.add_argument(
        "--candidate-disable-actuator-bridge",
        action="store_true",
        help=(
            "Disable the default candidate actuator bridge for a locomotion "
            "bootstrap run. This is offline training only; sim gates still "
            "evaluate the exported policy against fitted/stress bridge modes."
        ),
    )
    parser.add_argument("--candidate-actuator-bridge-delay-min-ticks", type=int, default=3)
    parser.add_argument("--candidate-actuator-bridge-delay-max-ticks", type=int, default=8)
    parser.add_argument("--candidate-actuator-bridge-tau-min-s", type=float, default=0.06)
    parser.add_argument("--candidate-actuator-bridge-tau-max-s", type=float, default=0.14)
    parser.add_argument(
        "--candidate-actuator-bridge-velocity-limit-min-rad-s",
        type=float,
        default=2.5,
    )
    parser.add_argument(
        "--candidate-actuator-bridge-velocity-limit-max-rad-s",
        type=float,
        default=4.7,
    )
    parser.add_argument(
        "--candidate-actuator-bridge-per-joint-variation",
        type=float,
        default=0.15,
    )
    args = parser.parse_args()

    rdk_root = Path(args.rdk_root).resolve()
    playground_root = Path(args.playground_root).resolve()
    if not rdk_root.exists():
        raise SystemExit(f"RDK repo missing: {rdk_root}")
    if not playground_root.exists():
        raise SystemExit(f"Playground repo missing: {playground_root}")
    extra_required_paths = [
        item
        for item in [
            repo_relative_existing_path(args.phase2_restore_checkpoint_path, rdk_root),
            repo_relative_existing_path(args.candidate_restore_checkpoint_path, rdk_root),
            repo_relative_existing_path(args.candidate_behavior_prior_mlp_npz, rdk_root),
        ]
        if item
    ]
    validate_rdk_package_inputs(args.workflow, rdk_root, extra_required_paths)
    candidate_existing_policy = (
        Path(args.candidate_existing_policy).expanduser().resolve()
        if args.candidate_existing_policy
        else None
    )
    candidate_training_manifest = (
        Path(args.candidate_training_manifest).expanduser().resolve()
        if args.candidate_training_manifest
        else None
    )
    if args.workflow == "candidate-eval-only" and candidate_existing_policy is None:
        raise SystemExit("--workflow candidate-eval-only requires --candidate-existing-policy")
    if candidate_existing_policy is not None and not candidate_existing_policy.exists():
        raise SystemExit(f"Candidate ONNX missing: {candidate_existing_policy}")
    if (
        candidate_training_manifest is not None
        and not candidate_training_manifest.exists()
    ):
        raise SystemExit(f"Candidate training manifest missing: {candidate_training_manifest}")

    ts = timestamp()
    run_dir = Path(args.output_root).resolve() / f"{args.session}-{args.workflow}-{ts}"
    upload_root = Path(args.upload_root).resolve()
    rdk_tar = upload_root / f"open-duck-mini-rdkx5_cli_{ts}.tar.gz"
    playground_tar = upload_root / f"Open_Duck_Playground_cli_{ts}.tar.gz"

    print(f"COLAB_SESSION {args.session}")
    print(f"WORKFLOW {args.workflow}")
    print(f"RUN_DIR {run_dir}")
    print(f"JAX_PIN {PINNED_JAX_VERSION}")
    if args.package_only:
        run_dir.mkdir(parents=True, exist_ok=True)
        make_tarball(rdk_root, rdk_tar, "open-duck-mini-rdkx5")
        make_tarball(playground_root, playground_tar, "Open_Duck_Playground")
        write_package_only_manifest(
            run_dir,
            args.workflow,
            args.session,
            rdk_tar,
            playground_tar,
            rdk_root,
            playground_root,
            sys.argv,
            extra_required_paths,
        )
        print("PACKAGE_ONLY no Colab upload or remote work started")
        return 0
    if not args.run:
        run_dir.mkdir(parents=True, exist_ok=True)
        workflow_name = f"open_duck_colab_cli_{args.workflow}_{ts}"
        remote_bundle = f"/content/{workflow_name}_artifacts.tar.gz"
        candidate_remote_policy = (
            "/content/open_duck_candidate_existing_policy.onnx"
            if candidate_existing_policy is not None
            else None
        )
        candidate_remote_manifest = (
            "/content/open_duck_candidate_training_manifest.json"
            if candidate_training_manifest is not None
            else None
        )
        driver = build_remote_driver(
            args,
            workflow_name,
            "/content/open-duck-mini-rdkx5_cli.tar.gz",
            "/content/Open_Duck_Playground_cli.tar.gz",
            remote_bundle,
            candidate_remote_policy=candidate_remote_policy,
            candidate_remote_manifest=candidate_remote_manifest,
        )
        driver_path = run_dir / f"{workflow_name}_driver.py"
        driver_path.write_text(driver)
        run_dir.joinpath("PLAN_ONLY_REMOTE_PATHS.txt").write_text(
            "\n".join(
                [
                    f"workflow_name={workflow_name}",
                    f"remote_bundle={remote_bundle}",
                    f"driver={driver_path}",
                ]
            )
            + "\n"
        )
        print("PLAN_ONLY pass --run to upload/start remote work")
        print(f"PLAN_DRIVER {driver_path}")
        return 0

    run_dir.mkdir(parents=True, exist_ok=True)
    initialize_content_api(args.session, run_dir)
    make_tarball(rdk_root, rdk_tar, "open-duck-mini-rdkx5")
    make_tarball(playground_root, playground_tar, "Open_Duck_Playground")
    rdk_remote = "/content/open-duck-mini-rdkx5_cli.tar.gz"
    playground_remote = "/content/Open_Duck_Playground_cli.tar.gz"
    upload_file(args.session, rdk_tar, rdk_remote, run_dir)
    upload_file(args.session, playground_tar, playground_remote, run_dir)
    candidate_remote_policy = None
    candidate_remote_manifest = None
    if candidate_existing_policy is not None:
        candidate_remote_policy = "/content/open_duck_candidate_existing_policy.onnx"
        upload_file(
            args.session,
            candidate_existing_policy,
            candidate_remote_policy,
            run_dir,
        )
    if candidate_training_manifest is not None:
        candidate_remote_manifest = "/content/open_duck_candidate_training_manifest.json"
        upload_file(
            args.session,
            candidate_training_manifest,
            candidate_remote_manifest,
            run_dir,
        )
    start_remote_job(
        args,
        run_dir,
        rdk_remote,
        playground_remote,
        candidate_remote_policy=candidate_remote_policy,
        candidate_remote_manifest=candidate_remote_manifest,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
