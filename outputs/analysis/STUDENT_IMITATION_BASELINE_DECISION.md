# Student Imitation Baseline Decision

status: `PLAN_CLOSED_LOOP_REGULARIZED_STUDENT`

This is an offline planning artifact. It does not run robot tests, SSH,
deployment, PPO training, or runtime behavior changes.

## Input Evidence

All rows use the same low-rate closed-loop teacher-window manifest:

```text
outputs/analysis/closed_loop_teacher_dataset_manifest.json
dataset_id: 407af2cbe0ad69e1
entries: 259
samples: 6475
source rollout dirs: 16
```

The gate was straight `x=0.08`, `5s`, seeds `0-7`, upstream-main
`flat_terrain_backlash`, CPU JAX/MJX.

| student | artifact | status | key result |
|---|---|---|---|
| kNN, k=5 | `CLOSED_LOOP_TEACHER_DATASET_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 5/8 moving, 2/8 near-standstill, 1/8 fall/reverse |
| aggregate sequence | `CLOSED_LOOP_TEACHER_SEQUENCE_REPLAY_X008.md` | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | all seeds complete, near-standstill, sent-vel p95 `0.2660` |
| aggregate sequence, no seam | `CLOSED_LOOP_TEACHER_SEQUENCE_REPLAY_X008_NO_SEAM.md` | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | all seeds complete, near-standstill, sent-vel p95 `0.2853` |
| MLP 64x64 | `CLOSED_LOOP_TEACHER_DATASET_MLP_BC_GATE_X008.md` | `HOLD_BC_REPLAY_LOW_FORWARD_MOTION` | 1/8 moving, sent-vel p95 `5.2400` every seed |
| MLP + target-rate pair loss | `CLOSED_LOOP_TEACHER_DATASET_MLP_RATE_REG_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 3/8 terminated, sent-vel p95 `5.2400` every seed |
| MLP + obs consistency | `CLOSED_LOOP_TEACHER_DATASET_MLP_CONSISTENCY_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 3/8 terminated, sent-vel p95 `5.2400` every seed |
| linear ridge | `CLOSED_LOOP_TEACHER_DATASET_LINEAR_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 0/8 moving, 1/8 fall/reverse, sent-vel p95 `0.7319-3.0866` |
| blend, kNN weight 0.75 | `CLOSED_LOOP_TEACHER_DATASET_BLEND075_BC_GATE_X008.md` | `HOLD_BC_REPLAY_LOW_FORWARD_MOTION` | 5/8 moving, 0/8 terminated, seeds 1/4/7 near-standstill |
| blend, kNN weight 0.80 | `CLOSED_LOOP_TEACHER_DATASET_BLEND080_BC_GATE_X008.md` | `HOLD_BC_REPLAY_LOW_FORWARD_MOTION` | best cheap baseline: 5/8 moving, 0/8 terminated, target-rate safe |
| blend, kNN weight 0.90 | `CLOSED_LOOP_TEACHER_DATASET_BLEND090_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 4/8 moving, seed 3 falls/reverses |
| kNN, k=3 | `CLOSED_LOOP_TEACHER_DATASET_KNN3_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | worse than k=5: 4/8 moving, seed 3 falls/reverses |

## Decision

Do not promote any current smoke student.

The curated low-rate teacher windows contain useful motion signal, but every
simple student has a distinct failure:

```text
kNN:
  preserves local motion, but is seed-fragile

aggregate sequence / linear:
  smooth enough, but too weak to propel

MLP:
  state-conditioned, but high-rate and low-progress in closed loop

MLP local regularizers:
  do not keep the rollout on the low-rate teacher manifold

blend 0.75-0.80:
  combines kNN motion with enough linear smoothing to remove the seed-3 fall,
  but still freezes seeds 1, 4, and 7
```

The next branch should be a closed-loop-regularized student, not another
one-step supervised fit scored only by action error.

Blend `0.80` is the best current cheap baseline to beat. A useful next student
must keep its no-termination behavior and recover forward motion on seeds
`1`, `4`, and `7`.

The traced blend `0.80` replay classifies that freeze as
`HOLD_FREEZE_LOW_ACTION_DOUBLE_SUPPORT`:

```text
moving seeds 0/2/3/5/6:
  single support mean: 46.24%
  pitch-chain target velocity p95 mean: 3.19 rad/s

frozen seeds 1/4/7:
  single support mean: 2.67%
  double support mean: 97.20%
  pitch-chain target velocity p95 mean: 0.40 rad/s
```

This means the next student must add closed-loop pressure against quiet
double-support dwell, not merely smooth the kNN policy further.

## Required Next Design

- Train or select using closed-loop rollouts, not only offline action loss.
- Preserve kNN-like local motion while enforcing linear/sequence-like smoothness.
- Beat blend `0.80`: no terminations and more than 5/8 moving seeds.
- Specifically recover seeds `1`, `4`, and `7` from low-action double-support
  dwell into alternating single support.
- Penalize or reject candidates whose closed-loop sent-target p95 reaches
  `5.24 rad/s`.
- Grade on all eight seeds for at least `5s` before any longer run.
- Gate on forward motion, fall/reverse count, near-standstill count, and
  max-joint pitch-chain p95 target velocity.
- Keep all behavior default-off and offline.

## Stop Rules

- Do not deploy or run robot validation.
- Do not treat the 2-seed kNN smoke as a pass.
- Do not use aggregate sequence replay as the student.
- Do not use plain one-step MLP BC as the student.
- Do not assume pairwise target-rate or observation-consistency regularization
  solves closed-loop rate saturation.
- Do not optimize supervised action error alone.
- Do not call blend `0.80` solved; it is only the current best cheap baseline.

## Current Next Step

Implement a reviewed offline student-selection/training loop that evaluates
candidate students in closed loop during selection. A valid first version can be
small and CPU-bound, but it must select on the actual gate metrics above rather
than only on one-step imitation loss.
