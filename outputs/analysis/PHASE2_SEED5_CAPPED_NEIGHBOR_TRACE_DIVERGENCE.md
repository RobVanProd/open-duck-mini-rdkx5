# Phase 2 Seed5-Capped Neighbor Trace Divergence

status: `PASS_TRACE_DIVERGENCE_CHARACTERIZED`

This is an offline trace-comparison artifact. No robot tests, SSH, deploy,
grounded replay, runtime behavior changes, or robot tuning were performed.
Raw full-observation JSONL traces remain generated local artifacts and are not
committed.

## Inputs

Candidate:

```text
outputs/analysis/phase2_live_oracle_right_swing_iter1_seed5_capped_phasecmd_bc_student/candidate.onnx
```

Trace sweeps:

```text
x=0.08: outputs/analysis/PHASE2_SEED5_CAPPED_NEIGHBOR_TRACE_COMPARE_X008.md
x=0.0:  outputs/analysis/PHASE2_SEED5_CAPPED_NEIGHBOR_TRACE_COMPARE_X0.md
```

Seeds compared:

```text
passing neighbors: 4,6
failing seed: 5
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: fitted
duration: 5s
```

## x=0.08 Result

Seed 5 reproduced the failure:

```text
seed 4: PASS, duration_complete
seed 5: HOLD_CANDIDATE_FALL_OR_TERMINATION, fall_or_nan at 55 samples
seed 6: PASS, duration_complete
```

Earliest divergences versus neighbor mean:

| event | first tick |
|---|---:|
| contact/support differs from both neighbors | 0 |
| pitch-chain sent-target velocity > 2.5 rad/s | 1 |
| pitch-chain action velocity > 2.5 rad/s | 1 |
| local vx becomes negative | 10 |
| local vx trails neighbor mean by >0.10 m/s | 17 |
| body pitch differs from neighbor mean by >0.20 rad | 25 |
| abs body pitch exceeds 0.30 rad | 30 |
| base height trails neighbor mean by >0.03 m | 51 |
| base height below 0.13 m | 51 |
| base height below 0.10 m | 54 |

Interpretation:

The seed5 fall is not only the late right-ankle burst. It has a visible early
contact/support mismatch and early over-envelope pitch-chain rate before
backward velocity, pitch divergence, and height collapse.

## x=0.0 Result

Seed 5 also reproduced the command-zero fall:

```text
seed 4: PASS, duration_complete
seed 5: HOLD_CANDIDATE_FALL_OR_TERMINATION, fall_or_nan at 42 samples
seed 6: PASS, duration_complete
```

Earliest divergences versus neighbor mean:

| event | first tick |
|---|---:|
| local vx negative | 0 |
| contact/support differs from both neighbors | 0 |
| pitch-chain sent-target velocity > 2.5 rad/s | 1 |
| pitch-chain action velocity > 2.5 rad/s | 1 |
| local vx trails neighbor mean by >0.10 m/s | 12 |
| body pitch differs from neighbor mean by >0.20 rad | 18 |
| abs body pitch exceeds 0.30 rad | 22 |
| base height trails neighbor mean by >0.03 m | 36 |
| base height below 0.13 m | 37 |
| base height below 0.10 m | 39 |

Interpretation:

Seed5 is a command-independent stability mode. Because it fails even at x=0.0,
the next correction should not be framed only as forward walking or rough
swing clearance.

## Decision

Seed5 needs an early-state correction branch, not another fall-tail-only cap.

The next useful branch should:

- keep the targeted seed4 right-swing labels
- keep the x=0 zero-command labels that preserve command semantics
- collect/live-relabel seed5 early states before pitch divergence
- downweight or exclude seed5 states only after early divergence becomes
  unrecoverable
- evaluate x=0.0 and x=0.08 together because seed5 fails both

Robot validation remains blocked.
