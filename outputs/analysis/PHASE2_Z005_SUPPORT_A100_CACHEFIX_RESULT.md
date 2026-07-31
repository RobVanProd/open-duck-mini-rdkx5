# Phase 2 z=0.005 Support A100 Cache-Fix Result

status: `HOLD_LOW_FORWARD_PROGRESS`

## Summary

- workflow: `phase2-z005-support`
- session: `open-duck-a100-phase2`
- hardware: `A100`
- cache_fix_commit: `6b00cbc`
- robot_touched: `false`
- ssh_performed: `false`
- deploy_performed: `false`
- grounded_replay_performed: `false`
- promoted_candidate: `false`

The patched A100 path cleared the previous XLA cache-directory failure and completed the z=0.005 support training/export path.

## Training

- run_dir: `/content/open_duck_training_phase2_z005_support_cli/smoke_20260630T080410Z_gpu`
- local_artifact_bundle: `outputs/analysis/colab_cli/open-duck-a100-phase2-phase2-z005-support-20260630T080315Z/open_duck_colab_cli_phase2-z005-support_20260630T080342Z_artifacts.tar.gz`
- status: `PASS_SMOKE_RUN`
- returncode: `0`
- elapsed_s: `767.6974`
- latest_onnx_step: `122880`
- latest_onnx_sha256: `456f943a339369d2e8a92aa0d8972ca2b496ee04ad4b68497ffb3f518c9a7eb2`
- actionable_stderr_warnings: `0`

## Compact Checkpoint Sweep

This was a 1-second CPU triage sweep at x=0.0 and x=0.08. It is not a promotion gate.

| checkpoint | x=0.0 status | x=0.08 status | x=0.08 track_ratio | x=0.08 mean_vx | x=0.08 max_pitch_vel_p95 | x=0.08 max_tracking_p95 |
|---|---|---|---:|---:|---:|---:|
| `40960` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2158 | 0.0173 | 1.4189 | 0.2110 |
| `81920` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1697 | 0.0136 | 1.4249 | 0.2156 |
| `122880` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1774 | 0.0142 | 1.4290 | 0.2117 |

## Interpretation

- The A100/JAX/MJX training path is usable after creating the XLA cache directories.
- The z=0.005 support/base-height recipe did not produce a useful candidate.
- All checkpoints remained well below the corrected velocity envelope, but x=0.08 forward progress fell below the compact sweep thresholds.
- The next recipe should preserve the Stage A2 walking action/manifold more directly while adding z=0.005 support, rather than adding another scalar support penalty.
