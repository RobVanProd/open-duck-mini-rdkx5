# Phase 2 z0.0026 Seed-5 Narrow Probe Results

status: `HOLD_NARROW_PROBES_NO_EXPORT`

## Context

The preserved 81920 teacher-continuity checkpoint remains the best known parent:

- full z=0.0026 x=0.08 gate: `7/8` duration complete.
- seed 5 is the lone fall/reverse/support-collapse failure.
- seed 5 trace shows no corrected-envelope velocity excess.

The first support-heavy diagnostic proved the default `phase2-z005-support` direction is too blunt: a tiny 8-env run exported an ONNX, but the resulting policy made seed 5 stable backward/low-progress in a 1-second screen.

## Tooling Added

`tools/run_colab_cli_cuda_workflow.py` now supports:

`--phase2-final-training-args-json`

This appends a JSON list of string arguments to the final Phase 2 training command, so bounded probes can override workflow defaults without adding a new hard-coded workflow.

## Narrow Probe A: z002 Teacher Continuity + Anti-Reverse Overrides

Workflow:

- `phase2-z002-teacher-continuity`
- restore: `outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920`
- terrain z-scale: `0.0026`
- timesteps: `4096`
- PPO envs: `8`
- final overrides:
  - `--forward-wrong-direction-scale -8`
  - `--base-height-scale -0.55`
  - `--forward-pitch-scale -0.36`
  - `--forward-pitch-rate-scale -0.08`
  - `--zero-command-probability 0.0`

Result:

`HOLD_NO_EXPORT`

The remote environment was correct (`jaxlib 0.7.2`, CUDA GPU, policy/sim audit pass). The training log stopped immediately after:

`Enabled restore-policy KL loss: scale=7.5 restore_checkpoint_path=...phase2_z0026_teacher_continuity_81920`

No checkpoint, ONNX, exit sentinel, or Python traceback was produced.

## Narrow Probe B: z005 Executable Path + Gentler Support Overrides

Workflow:

- `phase2-z005-support`
- same restore checkpoint and z-scale.
- timesteps: `4096`
- PPO envs: `8`
- final overrides:
  - `--forward-wrong-direction-scale -8`
  - `--forward-contact-support-scale -0.12`
  - `--forward-contact-support-no-contact-weight 1.0`
  - `--forward-contact-support-asymmetry-weight 0.1`
  - `--forward-single-support-scale 0.05`
  - `--forward-double-support-scale -0.05`
  - `--forward-double-support-dwell-scale -0.05`
  - `--forward-double-support-dwell-grace-steps 24`
  - `--base-height-scale -0.55`
  - `--forward-pitch-scale -0.36`
  - `--forward-pitch-rate-scale -0.08`
  - `--zero-command-probability 0.0`

Result:

`HOLD_NO_EXPORT`

The remote environment was correct, but the training log again stopped immediately after restore-policy KL setup:

`Enabled restore-policy KL loss: scale=4.0 restore_checkpoint_path=...phase2_z0026_teacher_continuity_81920`

No checkpoint, ONNX, exit sentinel, or Python traceback was produced.

## Decision

Do not launch more blind reward-shaping variants from this parent tonight.

Current evidence:

1. The restore checkpoint packages correctly and can be loaded by the remote trainer.
2. The default z005-support tiny run can execute/export, but the exported policy is not useful: it stabilizes seed 5 by reversing in double support.
3. The narrower override probes die before checkpoint/export with no traceback, likely during early JAX/PPO compile or first update.
4. The actual policy problem remains seed-5 support/reverse collapse, but broad support shaping moves into the wrong basin.

Next technical step should be either:

- add stronger runner-side failure capture around the PPO subprocess and XLA compile window, then retry the narrow probe, or
- run a direct minimal local/Colab trainer command outside the high-level wrapper to isolate why these override probes die before checkpoint.

No candidate from this diagnostic is promotable. No robot work is authorized.
