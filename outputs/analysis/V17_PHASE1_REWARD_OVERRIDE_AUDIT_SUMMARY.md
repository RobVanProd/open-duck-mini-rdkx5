# V17 Phase-1 Reward Override Audit

This is an offline CPU replay of the A100 `movement_bootstrap_v17` phase-1
checkpoint using the actual phase-1 reward override config from the staged
curriculum plan. No robot tests, SSH, deployment, runtime behavior changes, or
training were performed.

## Inputs

- policy: `2026_06_24_142512_276480.onnx`
- recipe: `movement_bootstrap_v17`
- phase: `phase1_hard_signed_progress_discovery`
- command: `x=0.08`
- bridge: `vanilla`
- seeds: `0-3`
- duration: `5 s`
- reward overrides: `open_duck_mini_staged_curriculum_cli_20260624T141603Z_staged_curriculum_plan.json`

## Result

The reward-overridden replay held on all four seeds:

```text
runs: 4
falls_or_terminations: 4
duration_complete: 0
samples_mean: 53
track_ratio_mean: -0.2367
mean_local_vx_mean: -0.0189 m/s
```

| seed | samples | termination | mean local vx | track ratio | body pitch p95 | base height min | interpretation |
|---:|---:|---|---:|---:|---:|---:|---|
| 0 | 60 | `fall_or_nan` | 0.0111 | 0.1391 | 0.1681 | 0.1536 | command-progress failure at warmup boundary |
| 1 | 32 | `fall_or_nan` | -0.0996 | -1.2447 | 0.0006 | 0.1026 | early reverse/collapse before progress gate |
| 2 | 60 | `fall_or_nan` | 0.0182 | 0.2281 | 0.1274 | 0.1525 | command-progress failure at warmup boundary |
| 3 | 60 | `fall_or_nan` | -0.0055 | -0.0692 | 0.1465 | 0.1561 | command-progress failure at warmup boundary |

## Reward-Term Readout

Seeds `0`, `2`, and `3` terminate exactly at the `60`-sample command-progress
warmup boundary. Their trace diagnostics show `diagnostic/command_progress_failure`
becoming active. This means the V17 progress gate is present in replay; the
candidate learned behavior that fails it.

Seed `1` terminates earlier at sample `32`, before command-progress failure can
activate. It moves backward (`track_ratio=-1.2447`) and loses support
(`base_height_min=0.1026 m`), so this is a physical reverse/collapse mode rather
than the delayed progress gate.

## Interpretation

This audit rules out a missing reward-override explanation for V17's A100 hold.
The hard signed-progress recipe was evaluated with the intended phase-1 reward
config, and the policy still failed to produce sustained forward progress.

The failure has two parts:

- Seeds `0`, `2`, and `3` are posture-stable enough to reach the warmup
  boundary, but their command-progress ratio remains too low.
- Seed `1` collapses while moving backward before the progress gate can act.

The next recipe should not proceed to V17 phase 2. It should first address why
the policy can still settle into low/reverse progress under the hard-progress
phase-1 objective.

## Next Offline Work

- Verify the training and evaluator local-forward-velocity sign convention from
  the reward source code, not only from replay metrics.
- Inspect whether delayed terminal command-progress failure is too sparse for
  PPO to learn from and whether the dense positive-progress signal is being
  diluted by posture/contact survival rewards.
- Consider a next recipe with earlier dense per-step signed progress pressure,
  explicit wrong-direction suppression from the start, and a lower-command
  discovery gate before returning to `x=0.08`.
- Do not launch another large A100 run until the reward/sign audit is complete.
