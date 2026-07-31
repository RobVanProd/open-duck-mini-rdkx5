# Phase 2 Stage-A2 / Seed5-Recovery Command Scale Diagnostic

status: `HOLD_CMDSCALE_FIXES_PUSH_ENVELOPE_BREAKS_NOPUSH_SWING`

This is an offline diagnostic. It did not train, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Candidate Tested

Input:

```text
outputs/analysis/phase2_seed5_neighbor_recovery_stagea2_command_gated_candidate/candidate.onnx
```

Command-scale wrapper:

```text
scale = 1.0 + (0.99 - 1.0) * clip(abs(obs[6]) / 0.08, 0, 1)
```

Generated diagnostic ONNX:

```text
outputs/analysis/phase2_seed5_neighbor_recovery_stagea2_command_gated_cmdscale_1p0_to_0p99_candidate/candidate.onnx
```

This wrapper keeps `x=0.0` at scale `1.0` and attenuates `x=0.08` to scale
`0.99`.

## Results

All tests used:

```text
task: rough_terrain_backlash
hfield z scale: 0.002
bridge: corrected fitted bridge
duration: 5 s
seeds: 0-7
```

### `x=0.08`, Gentle Push

Artifact:

```text
outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_CMDSCALE_1P0_TO_0P99_X008_ROUGH_Z002_GENTLE_PUSH_8SEED_GATE_CPU.md
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE 8/8
falls: 0/8
mean vx: 0.0322 m/s
mean track ratio: 0.4029
mean push recovery success: 0.9062
max velocity excess: 0.0000 rad/s
max tracking p95: 0.1985 rad
```

The 0.99 high-command scale fixed the prior gentle-push target-velocity hold.

### `x=0.0`, Gentle Push

Artifact:

```text
outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_CMDSCALE_1P0_TO_0P99_X0_ROUGH_Z002_GENTLE_PUSH_8SEED_GATE_CPU.md
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE 8/8
falls: 0/8
mean vx: 0.0023 m/s
mean push recovery success: 0.9062
max velocity excess: 0.0000 rad/s
max tracking p95: 0.1056 rad
```

Zero-command behavior remained intact.

### `x=0.08`, No Push

Artifact:

```text
outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_CMDSCALE_1P0_TO_0P99_X008_ROUGH_Z002_8SEED_GATE_CPU.md
```

Result:

```text
status: HOLD_CANDIDATE_TERRAIN_SWING
falls: 0/8
duration_complete: 8/8
mean vx: 0.0322 m/s
mean track ratio: 0.4030
max velocity excess: 0.0000 rad/s
max tracking p95: 0.1987 rad
seed 3 min swing rel-x p95 range: 0.0025 m
required min swing rel-x p95 range: 0.0030 m
```

## Decision

`HOLD_CMDSCALE_FIXES_PUSH_ENVELOPE_BREAKS_NOPUSH_SWING`

A uniform high-command attenuation is too blunt to promote. Scale `0.99` fixes
the gentle-push envelope excess, but it slightly erodes no-push rough-terrain
foot advance on seed 3. The promoted package remains the unscaled
command-gated candidate:

```text
policy/candidates/phase2_stagea2_seed5_recovery_command_gated_20260628/candidate.onnx
```

The next useful offline step is not global attenuation. It should add
perturbation-specific target-rate margin while preserving no-push swing
geometry, for example by fine-tuning with push perturbations active or using a
phase/contact-specific correction only during high-rate recovery moments.

## Scalar-Gain Bracket

Two eval-only follow-up screens bracketed the tradeoff:

```text
0.997 x=0.08 gentle push:
  artifact: outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_GAIN0997_X008_ROUGH_Z002_GENTLE_PUSH_8SEED_GATE_CPU.md
  result: HOLD_CANDIDATE_TARGET_VELOCITY on seed 5,
          HOLD_CANDIDATE_TRACKING on seed 7

0.995 x=0.08 gentle push:
  artifact: outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_GAIN0995_X008_ROUGH_Z002_GENTLE_PUSH_8SEED_GATE_CPU.md
  result: HOLD_CANDIDATE_TRACKING on seed 7
          max tracking p95: 0.2005 rad
```

This closes the scalar-gain sweep. The remaining push-margin issue needs a
more local correction than global command/action attenuation.
