# Phase 2 Live-Oracle Iteration 1 Seed5-Capped Decision

status: `HOLD_SEED5_CAPPED_NOT_SUFFICIENT`

This is an offline sim-side analysis. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or robot tuning were performed.

## Test

The previous selective aggregate improved neither the seed-5 reverse/fall nor
the broader rough-terrain gate. This branch tested a more local curation:

```text
base manifest: targeted right-swing command manifest
live x=0.08 relabels: keep seeds 0,1,2,3,5,6,7
live x=0.08 seed 4: dropped to preserve the targeted seed-4 right-swing labels
live x=0.08 seed 5: right_ankle action deltas capped at 2.25 rad/s equivalent
live x=0.08 seed 5: reverse/fall-tail rows weight-clamped to 0.25
live x=0.0 relabels: keep seeds 0 and 4
aggregate entries: 12
```

The curation artifact capped four right-ankle action-delta records and
weight-clamped 219 seed-5 rows.

## x=0.08 Rough z=0.002 Gate

| seed | status | vx | track ratio | velocity excess | tracking p95 | rel-x p95 |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TERRAIN_SWING` | 0.0311 | 0.3891 | 0.0000 | 0.1968 | 0.0024 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 0.0261 | 0.3263 | 0.0000 | 0.1964 | 0.0161 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 0.0363 | 0.4540 | 0.0000 | 0.1947 | 0.0071 |
| 3 | `PASS_CANDIDATE_SIM_GATE` | 0.0309 | 0.3865 | 0.0000 | 0.1889 | 0.0038 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 0.0356 | 0.4445 | 0.0000 | 0.1960 | 0.0067 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | -0.2492 | -3.1144 | 0.2094 | 0.2049 | 0.0069 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 0.0357 | 0.4468 | 0.0000 | 0.1993 | 0.0093 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 0.0288 | 0.3602 | 0.0000 | 0.1984 | 0.0044 |

Summary:

```text
passes: 6/8
duration_complete: 7/8
falls: 1/8
remaining holds: seed 0 terrain swing, seed 5 fall/reverse
```

## x=0 Rough z=0.002 Gate

The same candidate also failed command-zero robustness:

```text
passes: 7/8
duration_complete: 7/8
falls: 1/8
falling seed: 5
mean vx including fall: -0.0470 m/s
```

## Decision

This branch improved over flat selective aggregation but is not sufficient.

Positive movement:

- seed 3 no longer violates the target-velocity gate at x=0.08
- seed 4 preserves the targeted right-swing improvement at x=0.08
- seeds 1,2,3,4,6,7 pass the rough x=0.08 gate

Remaining blocker:

- seed 5 still collapses/reverses at x=0.08
- seed 5 also collapses at x=0.0

That means the right-ankle burst is not the whole mechanism. The curation
reduced one label-rate symptom, but seed 5 remains a broader state-dependent
stability basin problem.

## Next Step

Do not promote this candidate.

The next useful branch should treat seed 5 as a separate robustness mode rather
than only a label-rate burst:

- collect full-observation traces for seed 5 at x=0.0 and x=0.08 from this
  candidate
- compare seed 5 against neighboring passing seeds 4 and 6 to isolate the
  first divergent state feature
- test a seed-5-specific live-oracle correction with early-state emphasis
  before the fall tail, not another tail-only cap

Robot validation remains blocked.
