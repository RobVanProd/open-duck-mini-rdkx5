# V18 Phase-1 Reward-Override Replay Summary

Date: 2026-06-24

Purpose:

Replay the V18 phase-1 A100 candidate with the intended V18 phase reward
overrides active in the evaluator. The original A100 phase gate correctly failed
on motion/fall metrics, but its raw reward-term diagnostics used default eval
reward settings because phase-gate reward overrides were not passed through.

Replay command:

```text
policy: V18 phase-1 final ONNX, 276480 step export
command_x: 0.04
bridge_mode: vanilla
seeds: 0-1
platform: CPU
reward_overrides_json: outputs/analysis/v18_a100_staged_plan.json
reward_overrides_phase: phase1_x004_dense_progress_discovery
robot tests: none
deploy/SSH: none
```

Gate result:

```text
seed 0: HOLD_CANDIDATE_FALL_OR_TERMINATION, 50 samples
seed 1: HOLD_CANDIDATE_FALL_OR_TERMINATION, 33 samples
```

Per-seed motion:

| seed | samples | termination | mean_local_vx | track_ratio | reward_mean | forward_shortfall_cost_mean | command_progress_failure_max |
|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 50 | fall_or_nan | 0.0034 | 0.0845 | -1.9374 | 0.5499 | 1.0 |
| 1 | 33 | fall_or_nan | -0.0954 | -2.3845 | -17.4591 | 11.8133 | 0.0 |

Interpretation:

The corrected reward replay strengthens the V18 hold. With the intended reward
config active, seed 0 reaches the command-progress failure boundary at 50
samples instead of surviving as a low-progress rollout. Seed 1 still reverses
and collapses before the command-progress failure warmup can act.

Reward-term notes:

```text
seed 0:
  reward/forward_progress mean: 12.6660
  reward/command_progress mean: 2.6731
  cost/forward_shortfall mean: 89.0719
  cost/forward_wrong_direction mean: 19.9080
  cost/command_progress_failure mean: 3.2000

seed 1:
  reward/forward_progress mean: 0.0000
  reward/command_progress mean: -15.4957
  cost/forward_shortfall mean: 1524.1375
  cost/forward_wrong_direction mean: 1101.4566
  cost/command_progress_failure mean: 0.0000
```

The reward machinery is not silently inactive. The intended signed progress,
shortfall, wrong-direction, and command-progress terms apply, yet the trained
policy still does not produce coherent low-command forward motion. This points
away from a simple phase-gate reward plumbing issue and toward the reward/task
construction or optimization landscape itself.

Next implication:

Do not launch V18 phase 2. Do not launch another large recipe that only changes
scales blindly. The next useful offline work is to characterize why PPO is
failing to discover a gait seed under this low-command task, for example by
comparing reward components against a hand-authored or teacher-generated forward
stepping action pattern.

Artifacts:

```text
outputs/analysis/V18_PHASE1_REWARD_OVERRIDE_REPLAY.md
outputs/analysis/v18_phase1_reward_override_replay.json
```
