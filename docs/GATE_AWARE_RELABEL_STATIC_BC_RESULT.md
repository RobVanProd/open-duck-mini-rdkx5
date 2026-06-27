# Gate-Aware Static Relabel BC Result

status: `HOLD_CANDIDATE_TRACKING`

This was an offline rollout-correction probe. It did not SSH, deploy, run robot
tests, train PPO, or change robot runtime behavior.

## Purpose

The pitch-chain `4.3 rad/s` PPO-shape student was stable and target-rate safe
but still failed the fitted-bridge tracking gate. This probe tested the smallest
gate-aware correction path:

1. collect full-observation traces from the strict fitted-backlash gate states
   that still held;
2. relabel those visited states with the source-VX teacher that proved
   in-envelope walking feasibility;
3. merge the correction labels back into the curated pitch-chain dataset;
4. train another PPO-shape feed-forward student;
5. screen the exact targeted seeds before spending a full 8-seed gate.

## Artifacts

- targeted trace sweep:
  `outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_GATE_FAILURE_TRACES.md`
- seed 1 trace analysis:
  `outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_GATE_FAILURE_SEED1_TRACE.md`
- seed 4 trace analysis:
  `outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_GATE_FAILURE_SEED4_TRACE.md`
- gate-failure trace manifest:
  `outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_GATE_FAILURE_TRACE_MANIFEST.md`
- source-VX relabel:
  `outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_GATE_FAILURE_RELABEL_SOURCE_VX.md`
- relabel manifest:
  `outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_GATE_FAILURE_RELABEL_SOURCE_VX_MANIFEST.md`
- merged weighted manifest:
  `outputs/analysis/PITCH_CHAIN_4P3_GATE_AWARE_RELABEL_WEIGHTED_MANIFEST.md`
- student fit:
  `outputs/analysis/PITCH_CHAIN_4P3_GATE_AWARE_RELABEL_PPO_SHAPE_STUDENT.md`
- targeted screen:
  `outputs/analysis/PITCH_CHAIN_4P3_GATE_AWARE_RELABEL_PPO_SHAPE_STUDENT_SEED1_SEED4_SCREEN.md`

Raw JSONL traces are ignored local artifacts and were not committed.

## Gate-Failure Trace Finding

The targeted full-observation traces reproduced the same failure class:

```text
seed 1: duration complete, mean vx 0.0359, track ratio 0.4484, tracking p95 0.2554
seed 4: duration complete, mean vx 0.0393, track ratio 0.4918, tracking p95 0.2561
```

Both traces stayed upright. The hold is persistent pitch-chain tracking, not
termination.

Right knee remains the worst tracking joint:

```text
seed 1 right_knee tracking p95: 0.2554 rad
seed 4 right_knee tracking p95: 0.2561 rad
```

The relabel action deltas were nontrivial:

```text
seed 1 action_delta_p95: 0.0848
seed 4 action_delta_p95: 0.0968
```

So the source-VX teacher did prescribe different actions at the visited
gate-failure states.

## Gate-Aware Student Screen

The relabeled strict-gate states were merged with the pitch-chain `4.3 rad/s`
base manifest and weighted `12x`. A PPO-shape feed-forward student was trained
from the weighted manifest and screened on the two targeted seeds.

| seed | baseline vx | baseline ratio | baseline vel p95 | baseline tracking p95 | relabel vx | relabel ratio | relabel vel p95 | relabel tracking p95 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.0359 | 0.4484 | 3.7059 | 0.2554 | 0.0372 | 0.4652 | 3.7264 | 0.2548 |
| 4 | 0.0393 | 0.4918 | 3.7024 | 0.2561 | 0.0380 | 0.4747 | 3.6821 | 0.2536 |

Result:

```text
duration_complete: 2/2
falls: 0/2
status: HOLD_CANDIDATE_TRACKING
```

## Decision

Static gate-aware relabeling is not enough as a standalone fix.

The relabel moved the labels and preserved stability, but it did not materially
reduce the tracking plateau. The improvement is far too small to justify a full
8-seed gate from this candidate.

```text
closed:
  static gate-aware relabeling into feed-forward BC

still needed:
  closed-loop fine-tuning with gate feedback
  recurrent/phase-aware policy state
  explicit support-transition correction objective
```

Do not robot-test this candidate. Robot validation remains blocked.
