# Command-Conditioned Hard-Seed Recovery DAgger Seed-5 Decision

status: `HOLD_X008_TRACKING_BUT_X0_SEED5_FIXED`

Purpose: test whether adding corrective on-policy labels from the failing
`x=0.0` seed-5 visited states fixes the zero-command hard-seed collapse while
preserving the `x=0.08` moving branch.

This is offline analysis only. It did not train PPO, deploy, SSH, run robot
tests, or change robot runtime behavior.

## Corrective Relabel

Artifact:

```text
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DAGGER_SEED5_X0_RELABEL.md
```

The failing `x=0.0` seed-5 trace was relabeled with the existing blend teacher
and truncated before the terminal row:

```text
status: PASS_BC_TRACE_RELABEL_READY
samples_out: 72
action_delta_p50: 0.0194
action_delta_p95: 0.1005
action_delta_max: 0.2867
```

This relabel is materially different from simply increasing weight on the old
stable seed-5 source trace. The previous weighted experiment failed seed 5
earlier; this experiment adds labels for states the failing student actually
visited.

## Dataset And Fit

Manifest:

```text
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DAGGER_SEED5_X0_MANIFEST.md
status: PASS_BC_TRACE_MANIFEST_READY
entries: 20
samples: 10322
```

BC student:

```text
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DAGGER_SEED5_X0_BC_STUDENT.md
status: PASS_PPO_LOC_BC_FIT_SMOKE
```

## x=0 Gate

Canonical backlash, fitted bridge, 10 seconds, seeds 0-7:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DAGGER_SEED5_X0_FITTED_10S.md
status: all seeds PASS_CANDIDATE_SIM_GATE
falls: 0 / 8
duration complete: 8 / 8
mean vx: 0.0004 m/s
body pitch p95 mean: 0.0207 rad
base height min mean: 0.1527 m
seed 5: PASS, 500 samples, vx_mean 0.0053, tracking_p95 0.0763
```

This fixes the exposed zero-command seed-5 collapse. The earlier unweighted
candidate failed seed 5 at 73 samples, and the weighted-only candidate failed
seed 5 at 57 samples.

## x=0.08 Gate

Canonical backlash, fitted bridge, 10 seconds, seeds 0-7:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DAGGER_SEED5_X008_FITTED_10S.md
status: HOLD_CANDIDATE_TRACKING
falls: 0 / 8
duration complete: 8 / 8
mean vx: 0.0344 m/s
mean track ratio: 0.4294
body pitch p95 mean: 0.1147 rad
max pitch-chain target velocity p95 range: 2.1043-2.1639 rad/s
tracking p95 range: 0.1875-0.1985 rad
```

The moving branch survives and remains inside the fitted actuator velocity
envelope, but it is still not a robot candidate because tracking p95 remains
well above the preferred/acceptable gate.

## Decision

Do not promote the ONNX to robot validation.

This is nevertheless the best result in the command-conditioned hard-seed line:

```text
- x=0.0 hard-seed stability is fixed across all eight seeds
- x=0.08 forward branch remains stable across all eight seeds
- target rates stay inside the fitted actuator envelope
- remaining hold is x=0.08 tracking error, not fall, saturation, or target-rate violation
```

Next offline branch should target fitted-bridge tracking at `x=0.08` without
breaking the newly fixed zero-command stability. That means adding tracking or
target-stage feedback to the student objective, or PPO fine-tuning from this
DAgger seed-5 checkpoint with the fitted actuator bridge active. Do not return
to raw sample weighting for seed 5.

Robot validation remains blocked.
