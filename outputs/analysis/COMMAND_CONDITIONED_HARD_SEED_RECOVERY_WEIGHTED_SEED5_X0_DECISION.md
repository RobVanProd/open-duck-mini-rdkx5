# Command-Conditioned Hard-Seed Recovery Weighted Seed-5 Decision

status: `HOLD_WEIGHTED_SEED5_X0_STILL_FAILS`

Purpose: test whether giving extra supervised weight to the stable `x=0.0`
seed-5 source trace fixes the remaining zero-command hard-seed failure while
preserving the command-conditioned recovery line.

This is offline analysis only. It did not train PPO, deploy, SSH, run robot
tests, or change robot runtime behavior.

## Change Tested

A weighted manifest was built from the command-conditioned hard-seed recovery
manifest:

```text
input: outputs/analysis/command_conditioned_hard_seed_recovery_manifest.json
weighted: outputs/analysis/command_conditioned_hard_seed_recovery_weighted_seed5_x0_manifest.json
```

Only the stable x=0.0 seed-5 source trace was upweighted:

```text
rule: scale0p75_x0_full_obs_traces.*/seed_005/trace\.jsonl -> 8.0
weighted samples: 13750.0000
```

The x=0.08 seed-5 moving source trace remained at weight 1.0.

## Supervised Fit

Artifact:

```text
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_WEIGHTED_SEED5_X0_BC_STUDENT.md
```

Result:

```text
status: PASS_PPO_LOC_BC_FIT_SMOKE
MAE: 0.007371
p95 action error: 0.025259
target-rate p95: 1.740643 rad/s
target-rate max: 2.535732 rad/s
sample weight p50/p95/max: 1.0 / 1.0 / 8.0
```

## x=0 Gate

Canonical backlash, fitted bridge, 10 seconds, seeds 0-7:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_WEIGHTED_SEED5_X0_FITTED_10S.md
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
falls: 1 / 8
failing seed: 5
seed 5 samples: 57
seed 5 mean vx: -0.2567 m/s
seed 5 base_height_min: 0.0680 m
seed 5 tracking p95: 0.1956 rad
```

The unweighted command-conditioned candidate failed seed 5 at 73 samples. This
weighted variant fails the same seed earlier, so simple sample weighting of the
stable x=0 seed-5 trace is not the fix.

## Decision

Do not run x=0.08 or promote this ONNX. The targeted x=0 gate already failed.

This negative result reinforces the previous failure analysis:

```text
status: HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY
```

The next branch should not just increase supervised weight on existing x=0 seed
5 labels. It needs a closed-loop stabilization mechanism for seed 5 at
zero-command, such as corrective on-policy relabeling from seed-5 visited states
or a command-conditioned stabilizer that changes the early x=0 seed-5 response
without globally damping x=0.08 movement.

Robot validation remains blocked.
