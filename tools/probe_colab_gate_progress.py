#!/usr/bin/env python3
"""Read-only Colab probe for active checkpoint-gate progress."""

from pathlib import Path

lines = []
roots = sorted(Path("/content/open-duck-mini-rdkx5/outputs/analysis").glob("open_duck_colab_cli_*/phase2_stage_a_narrow_rate175_cuda_checkpoint_sweep"))
for root in roots:
    lines.append(f"ROOT {root}")
    for path in sorted(root.rglob("closed_loop_actuator_bridge_eval.json")):
        lines.append(f"COMPLETE {path.relative_to(root)} size={path.stat().st_size}")
for proc in sorted(Path("/proc").glob("[0-9]*")):
    try:
        command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        continue
    if "sweep_candidate_checkpoints" in command or "eval_policy_with_actuator_bridge" in command:
        lines.append(f"PROCESS {proc.name} {command[:1000]}")
text = "\n".join(lines) + "\n"
Path("/content/codex_gate_progress.txt").write_text(text)
print(text, end="")
