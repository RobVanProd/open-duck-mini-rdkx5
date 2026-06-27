# Command-Conditioned Hard-Seed Recovery DAgger Rate-175 Decision

status: `HOLD_RATE_TIGHTENING_BREAKS_X0_SEED5`

Purpose: test whether stronger BC target-rate pressure improves fitted-bridge
tracking while preserving the DAgger seed-5 zero-command fix.

This is offline analysis only. It did not train PPO, deploy, SSH, run robot
tests, or change robot runtime behavior.

## Change Tested

Same DAgger seed-5 manifest as the current best command-conditioned candidate:

```text
manifest: outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_manifest.json
```

BC target-rate settings:

```text
target_rate_scale: 0.6
target_rate_limit_rad_s: 1.75
```

The baseline DAgger seed-5 candidate used:

```text
target_rate_scale: 0.2
target_rate_limit_rad_s: 2.25
```

## Supervised Fit

Artifact:

```text
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DAGGER_SEED5_X0_RATE175_BC_STUDENT.md
```

Result:

```text
status: PASS_PPO_LOC_BC_FIT_SMOKE
MAE: 0.010691
p95 action error: 0.040171
target-rate p95: 1.573163 rad/s
target-rate max: 1.997019 rad/s
```

This successfully lowered the supervised target-rate metric, but increased
action fit error.

## x=0 Gate

Canonical backlash, fitted bridge, 10 seconds, seeds 0-7:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DAGGER_SEED5_X0_RATE175_X0_FITTED_10S.md
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
falls: 1 / 8
failing seed: 5
seed 5 samples: 59
seed 5 mean vx: -0.2491 m/s
seed 5 base_height_min: 0.0639 m
seed 5 tracking_p95: 0.2102 rad
```

The baseline DAgger seed-5 candidate fixed seed 5 at x=0.0. The tighter-rate
variant breaks that fix and falls at 59 samples.

## Decision

Do not run x=0.08 or promote this ONNX. The targeted x=0 stability gate already
failed.

This negative result means target-rate tightening alone is not a safe next
tracking fix. The next tracking branch must preserve the DAgger seed-5
zero-command correction explicitly, instead of globally increasing rate
pressure in the supervised loss.

Robot validation remains blocked.
