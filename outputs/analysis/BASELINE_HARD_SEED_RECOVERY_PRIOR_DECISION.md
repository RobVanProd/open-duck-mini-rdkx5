# Baseline Hard-Seed Recovery Prior Decision

status: `PASS_DIAGNOSTIC_PRIOR_HOLD_DIRECT_POLICY`

Purpose: test whether the baseline warm-start's hard-seed recovery behavior is
learnable as a supervised PPO-loc student. This is offline analysis only. It
does not authorize robot validation.

## Dataset

Manifest:

```text
outputs/analysis/BASELINE_STEP0_HARD_SEED_POSITIVE_TRACE_MANIFEST.md
```

Contents:

```text
seeds: 1, 3, 7
command_x: 0.08
samples: 2250
status: PASS_BC_TRACE_MANIFEST_READY
```

The traces come from the current warm-start baseline:

```text
outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0.onnx
```

They preserve the hard-seed forward behavior that the PPO smokes erased:

```text
vx: 0.0293-0.0374 m/s
track ratio: 0.3661-0.4674
target velocity p95: 1.7170-1.7409 rad/s
```

Raw JSONL traces remain outside git.

## Supervised Fit

Artifact:

```text
outputs/analysis/BASELINE_HARD_SEED_RECOVERY_PRIOR_BC_STUDENT.md
```

Result:

```text
status: PASS_PPO_LOC_BC_FIT_SMOKE
p95 action error: 0.014711
target-rate p95: 1.716564 rad/s
```

This proves the hard-seed recovery labels are learnable by the PPO-compatible
MLP contract.

## Closed-Loop Diagnostic Gates

x=0.08, canonical backlash, fitted bridge, seeds 1/3/7:

```text
artifact: outputs/analysis/BASELINE_HARD_SEED_RECOVERY_PRIOR_BACKLASH_X008_FITTED_15S_HARD_SEEDS.md
duration complete: 3 / 3
falls: 0
mean vx: 0.0314 m/s
mean track ratio: 0.3919
hold reason: tracking
```

x=0.08, canonical backlash, fitted bridge, seeds 0-7:

```text
artifact: outputs/analysis/BASELINE_HARD_SEED_RECOVERY_PRIOR_BACKLASH_X008_FITTED_15S.md
duration complete: 8 / 8
falls: 0
mean vx: 0.0243 m/s
mean track ratio: 0.3040
hold reasons: tracking plus low progress on seeds 4 and 6
```

x=0.0, canonical backlash, fitted bridge, seeds 0-7:

```text
artifact: outputs/analysis/BASELINE_HARD_SEED_RECOVERY_PRIOR_BACKLASH_X0_FITTED_15S.md
duration complete: 8 / 8
falls: 0
mean vx: 0.0244 m/s
hold reason: tracking
```

## Interpretation

The hard-seed recovery labels are useful:

```text
- seed 3 no longer falls
- seeds 1 and 7 preserve forward motion
- all x=0.08 seeds complete
```

But the direct student is not a deployable candidate because it is not
command-conditioned enough:

```text
- it moves forward at x=0.0
- it loses progress on x=0.08 seeds 4 and 6
- fitted tracking remains around 0.19 rad on moving seeds
```

## Decision

Use this as a recovery-prior data point, not as a policy.

The next dataset should combine:

```text
1. stable x=0.0 standstill traces
2. the hard-seed x=0.08 recovery traces from this artifact
3. existing broader x=0.08 moving traces
```

Then train or fine-tune a command-conditioned student/prior and gate it against
both:

```text
x=0.0: no forward drift
x=0.08: retain the hard-seed recovery behavior
```

Robot validation remains blocked.
