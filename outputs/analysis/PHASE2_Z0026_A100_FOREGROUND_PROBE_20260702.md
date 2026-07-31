# Phase 2 Z0026 A100 Foreground Probe

generated_at: `2026-07-02T04:40:00Z`

## Executive Summary

- `PASS_A100_FOREGROUND_TRANSPORT`: the Colab A100 workflow completed when run with the foreground remote path.
- `PASS_SMOKE_RUN`: the short teacher-continuity training probe exported an ONNX checkpoint.
- `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`: the exported checkpoint is not promotable. It stayed in-envelope but did not meet the compact positive-command progress threshold.
- The earlier `HOLD_REMOTE_NO_SENTINEL` results are now attributed to the detached/background Colab execution path, not to a proven recipe/runtime failure.

No robot test, SSH, deployment, grounded replay, or runtime behavior change was performed.

## Remote Run

- session: `open-duck-a100-poll`
- remote execution mode: `foreground-remote`
- workflow: `phase2-z002-teacher-continuity`
- candidate name: `phase2_z0026_teacher_continuity_a100_small_foreground_probe`
- training envs: `4`
- training timesteps: `8192`
- episode length: `128`
- command range: `x=[0.06, 0.10]`, `y=0`, `yaw=0`
- bridge during training: enabled, corrected bridge delay `3` ticks
- training status: `PASS_SMOKE_RUN`
- latest exported ONNX: `/content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260702T041920Z_gpu/2026_07_02_042523_8320.onnx`
- ONNX sha256: `ea691aa25895de3b70953e5ead605075d67b1af16845bb155debbbc4dd8cc120`
- artifact bundle sha256: `5367ea83205b9859f4f78497d1f426c02cf8e8d199b98386ea7acfe9cb38d0b5`

## Compact Sweep

The post-run compact CPU sweep evaluated `[0.0, 0.08]` for `1.0s` with the fitted corrected actuator bridge.

| command_x | status | samples | termination | max_pitch_vel_p95 | max_tracking_p95 | track_ratio | mean_local_vx |
|---:|---|---:|---|---:|---:|---:|---:|
| 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.0862 | 0.1936 | NA | 0.0067 |
| 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.5133 | 0.2174 | 0.2315 | 0.0185 |

Promotion decision:

- status: `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`
- pass count: `1/2`
- failure reasons:
  - `command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
  - `command 0.08: track ratio 0.2315 < 0.2500`
  - `command 0.08: mean vx 0.0185 < 0.0200`
- max action saturation: `0.0%`

## Interpretation

This run is a transport and recipe-startup pass, not a candidate pass. The foreground remote path should be used for subsequent A100 training probes because it preserves the remote process until artifact creation and download. The detached/background path remains unreliable for this workflow because several previous runs reached runner startup but failed to produce a recoverable sentinel or artifact.

The exported checkpoint is too short-trained to promote and still shows low positive-command progress. The next A100 probe should use the same foreground path with a longer bounded run before deciding whether this teacher-continuity recipe is improving or plateauing.

## Next Step

Run a bounded medium foreground A100 probe, still offline-only:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-z002-teacher-continuity \
  --session open-duck-a100-poll \
  --candidate-name phase2_z0026_teacher_continuity_a100_medium_foreground_probe \
  --phase2-num-timesteps 20480 \
  --phase2-ppo-num-envs 8 \
  --phase2-ppo-num-evals 1 \
  --phase2-episode-length 256 \
  --phase2-ppo-batch-size 64 \
  --phase2-ppo-num-minibatches 1 \
  --phase2-ppo-num-updates-per-batch 1 \
  --phase2-skip-post-training-gates \
  --foreground-remote \
  --foreground-remote-timeout-s 3600 \
  --timeout-s 4200 \
  --skip-deps \
  --skip-audit \
  --run
```
