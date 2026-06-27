# V23 Seed-0 x=0.04 Trace Summary

status: `HOLD_DOUBLE_SUPPORT_STANDSTILL`
generated_at: `2026-06-25T17:15:00Z`

## Summary

A targeted CPU-forced closed-loop trace was run from the recovered V23 ONNX:

```text
policy sha256:
  d8a92162cfee07cb4c6f2643c5206a182882fd46c0098f93a1c65c03e99c86c7

command:
  x=0.04

seed:
  0

bridge mode:
  vanilla

platform:
  CPU

raw trace:
  outputs/analysis/v23_seed0_x004_vanilla_trace_cpu/trace.jsonl
```

The raw trace is kept in the ignored output tree. This committed file records
only compact metrics.

## Gate Result

```text
overall_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
samples: 750
termination: duration_complete
mean_local_vx: -0.0002 m/s
track_ratio: -0.0051
base_height_min: 0.1537 m
body_pitch_p95: 0.0105 rad
max_pitch_tracking_p95: 0.0446 rad
max_sent_target_velocity_p95: 0.0974 rad/s
action_saturation: 0%
```

This candidate is stable in the narrow sense that it does not fall in the
vanilla `x=0.04` seed-0 trace, but it does not produce coherent forward motion.

## Contact Trace

| contact state | ticks | percent |
|---|---:|---:|
| `01` | 5 | 0.67% |
| `11` | 745 | 99.33% |

Contact runs:

```text
01: ticks 0-1    (2 ticks)
11: ticks 2-5    (4 ticks)
01: ticks 6-8    (3 ticks)
11: ticks 9-749  (741 ticks)
```

The full 15-second trace has only three contact transitions. After tick 9 the
policy stays in double support for the rest of the rollout.

## Interpretation

This validates the contact/weight-transfer diagnosis for V23:

```text
the support-contact reward did not create alternating support transfer
the policy found a stable double-support standstill
forward-progress tracking stayed effectively zero
the failure is not actuator target velocity or action saturation
```

Do not rerun V23 unchanged or tune only the single-support/double-support scalar
weights. The next useful branch needs a structural support-transition mechanism:

```text
1. a teacher/optimizer that explicitly chooses stance side, foot placement,
   body placement, and push timing; or
2. a closed-loop reference/controller that reacts to contacts, pitch, height,
   and lateral velocity while forcing support transition; or
3. a learning objective that directly rewards support-state transition and
   forward displacement together, not single-support occupancy in isolation.
```

Robot validation remains blocked.
