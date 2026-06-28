# Phase 2 Live-Oracle Iteration 1 Selective Aggregate Decision

status: `HOLD_SELECTIVE_AGGREGATE_NOT_SUFFICIENT`

This is an offline sim-side analysis. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or robot tuning were performed.

## Test

The first live-oracle aggregate improved several seeds but regressed seed 4 and
made seed 5 fall/reverse. A selective aggregate was tested:

```text
base manifest: targeted right-swing command manifest
live x=0.08 relabels: keep all except live seed 4 and live seed 5
live x=0.0 relabels: keep seeds 0 and 4
kept entries: 11
```

The filter used a precise source exclusion:

```text
^rollouts_x008/student/seed_00[45]/trace\.jsonl$
```

This preserves the original targeted seed-4 right-swing labels while removing
the two live x=0.08 entries most likely to cause the seed-4/seed-5 regressions.

## Result

The selective aggregate did not pass the rough 8-seed gate.

| seed | status | vx | track ratio | velocity excess | tracking p95 | rel-x p95 |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TERRAIN_SWING` | 0.0339 | 0.4238 | 0.0000 | 0.1996 | 0.0030 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 0.0298 | 0.3719 | 0.0000 | 0.1991 | 0.0158 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 0.0326 | 0.4077 | 0.0000 | 0.1951 | 0.0066 |
| 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 0.0274 | 0.3427 | 0.0336 | 0.1911 | 0.0034 |
| 4 | `HOLD_CANDIDATE_TRACKING` | 0.0347 | 0.4332 | 0.0000 | 0.2001 | 0.0054 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | -0.2703 | -3.3791 | 2.2516 | 0.2821 | 0.0139 |
| 6 | `HOLD_CANDIDATE_TRACKING` | 0.0319 | 0.3986 | 0.0000 | 0.2030 | 0.0082 |
| 7 | `HOLD_CANDIDATE_TRACKING` | 0.0311 | 0.3885 | 0.0000 | 0.2032 | 0.0168 |

## Decision

Selective entry exclusion is not enough.

The seed-5 reverse/fall is not caused only by the live seed-5 source entry, and
the seed-4/local right-swing improvement is not preserved by simply excluding
live seed 4. The aggregate changes the learned action manifold globally.

## Next Step

Do not continue flat aggregate variants.

The next useful branch must be structurally more local:

- trace seed 5's reverse/fall action sequence and cap/filter the right-ankle
  burst directly
- preserve targeted seed-4 right-swing rows with per-record weighting
- add per-record or per-phase weighting to live-oracle rows that improved seeds
  1, 3, and 7, instead of treating every live-oracle sample equally

The current best artifact remains the targeted right-swing local diagnostic
pass, not either live-oracle iter1 student.
