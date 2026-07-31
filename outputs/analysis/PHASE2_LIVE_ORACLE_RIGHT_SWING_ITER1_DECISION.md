# Phase 2 Live-Oracle Right-Swing Iteration 1 Decision

status: `HOLD_LIVE_ORACLE_ITER1_MIXED_IMPROVEMENT`

This is an offline sim-side analysis. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or robot tuning were performed.

## Context

The targeted right-foot swing weighting candidate passed the local rough
diagnostic on seeds 2 and 4, but the 8-seed rough gate exposed a broader
distribution problem:

```text
passes: seeds 2,4,6
low-progress holds: seeds 0,1,5,7
target-velocity hold: seed 3
falls: 0/8
```

A live-oracle DAgger data iteration was run to relabel the student's own
visited rough-terrain states:

```text
tool: tools/run_live_oracle_dagger_iteration.py
teacher manifest: outputs/analysis/phase2_seed4_right_swing_weighted_command_manifest.json
base manifest: outputs/analysis/phase2_seed4_right_swing_weighted_command_manifest.json
x=0.08 seeds: 0-7
x=0.0 seeds: 0,4
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
```

The iteration produced:

```text
x=0.08 relabel manifest: 8 entries / 2000 samples
x=0.0 relabel manifest: 2 entries / 500 samples
aggregate manifest: 13 entries / 3250 samples
```

## Result

The live-oracle iter1 phase/command student improved the distribution, but did
not clear the 8-seed rough gate.

| seed | previous status | iter1 status | iter1 vx | iter1 track ratio | iter1 excess | iter1 tracking | iter1 rel-x |
|---:|---|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_LOW_FORWARD_PROGRESS` | `HOLD_CANDIDATE_TERRAIN_SWING` | 0.0337 | 0.4216 | 0.0000 | 0.1988 | 0.0022 |
| 1 | `HOLD_LOW_FORWARD_PROGRESS` | `PASS_CANDIDATE_SIM_GATE` | 0.0331 | 0.4138 | 0.0000 | 0.1960 | 0.0171 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | `PASS_CANDIDATE_SIM_GATE` | 0.0428 | 0.5352 | 0.0000 | 0.1907 | 0.0064 |
| 3 | `HOLD_TARGET_VELOCITY` | `PASS_CANDIDATE_SIM_GATE` | 0.0283 | 0.3542 | 0.0000 | 0.1905 | 0.0034 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_TERRAIN_SWING` | 0.0334 | 0.4178 | 0.0000 | 0.1951 | 0.0024 |
| 5 | `HOLD_LOW_FORWARD_PROGRESS` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | -0.2401 | -3.0018 | 1.0416 | 0.1878 | 0.0508 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | `PASS_CANDIDATE_SIM_GATE` | 0.0283 | 0.3542 | 0.0000 | 0.1983 | 0.0080 |
| 7 | `HOLD_LOW_FORWARD_PROGRESS` | `PASS_CANDIDATE_SIM_GATE` | 0.0358 | 0.4469 | 0.0000 | 0.1975 | 0.0100 |

## Decision

Live-oracle relabeling is useful but the aggregate is not yet safe.

What improved:

- low-progress seeds 1 and 7 became passes
- seed 3 target-velocity excess was fixed
- seed 0 moved forward and only missed the swing/advance gate

What regressed:

- seed 4 lost the local right-swing pass and became a swing hold
- seed 5 became a hard reverse/fall with target-velocity excess

The next iteration should not simply aggregate all live-oracle labels equally.
It needs selective protection:

- preserve the targeted seed-4 right-swing labels from the local pass
- inspect and cap/relabel seed-5 live-oracle labels before training
- retain live-oracle relabels for seeds 1,3,7 where they clearly improved the
  outcome

## Gate

No robot validation. No promotion.

Next useful sim step:

```text
trace seed 5 under live_oracle_iter1_phasecmd
identify which contact/action segment produced the reverse/fall
filter or rate-limit that segment before a second aggregate fit
```
