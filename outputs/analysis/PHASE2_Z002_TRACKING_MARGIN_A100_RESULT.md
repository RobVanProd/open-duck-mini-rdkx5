# Phase 2 z=0.002 Tracking-Margin A100 Result

status: `HOLD_Z002_TRACKING_MARGIN_A100_NOT_PROMOTED`
generated_at: `2026-06-30T02:50:00Z`

This was an offline Colab A100 run. It did not SSH, deploy, touch the robot,
run grounded replay, or change runtime behavior.

## Scope

- workflow: `phase2-z002-tracking-margin`
- session: `open-duck-l4`
- hardware: `A100`
- jax/jaxlib: `0.7.2`
- warm start: `stage_c0_terrain_z002_preserve_from_a2_gpu/2026_06_28_064431_245760`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- terrain: `rough_terrain_backlash`, heightfield z scale `0.002`
- training timesteps: `122880`
- envs: `64`
- pushes during training: disabled

## Training

Training completed and exported three ONNX checkpoints.

| step | reward | onnx sha256 |
|---:|---:|---|
| `40960` | `37.8014` | `83b31d874ca6078953d4decb23909121e5914150229c3bdc2b406ced9208d510` |
| `81920` | `40.2106` | `ea01c7a9ae36d807d8ef5e5620213792bbb0a0b0adb4114f9753d238cc07e6bc` |
| `122880` | `40.9820` | `34ec5a7d533321e4430a180e8378bbbec45cb0c8aa28f19add7420b521333180` |

The local partial artifact is extractable and contains the training summary and
exported ONNX files:

```text
outputs/analysis/colab_cli/open-duck-l4-phase2-z002-tracking-margin-20260630T014242Z/open_duck_colab_cli_phase2-z002-tracking-margin_20260630T014331Z_artifacts.tar.gz.partial
```

## Compact Checkpoint Sweep

The compact sweep completed for commands `x=0.0` and `x=0.08`, duration `1s`,
with the corrected fitted bridge.

| checkpoint | x=0.0 | x=0.08 | track ratio | mean vx | max tracking p95 | max pitch vel p95 |
|---|---|---|---:|---:|---:|---:|
| `40960` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `0.2129` | `0.0170` | `0.2177` | `1.5267` |
| `81920` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_TRACKING` | `0.2939` | `0.0235` | `0.2184` | `1.4996` |
| `122880` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_TRACKING` | `0.2832` | `0.0227` | `0.2158` | `1.5373` |

All checkpoints stayed below the corrected measured velocity envelope and had
zero action saturation in the compact sweep. None passed the strict x=0.08
tracking gate (`tracking p95 <= 0.20`), so none is promotable.

## Full Seed Gate

The workflow selected the `81920` checkpoint as the best available but not
promoted checkpoint and started the full `x=0.08`, 8-seed, 15s seed gate.

The Colab session disappeared before the full seed gate completed. Captured
remote log evidence shows:

- seed `0` completed with `HOLD_CANDIDATE_TRACKING`
- seed `1` started
- the session was then no longer available through the Colab CLI

Because the full seed gate did not complete, this run cannot be used as a
promoted Phase 2 candidate.

## Decision

Do not promote this run.

The z=0.002 tracking-margin recipe preserved low target velocity and meaningful
forward motion, but did not recover enough tracking margin. The best checkpoint
still held around `0.216-0.218 rad` tracking p95 versus the `0.20 rad` gate.

Next aligned work should use the evidence already named in the sweep
interpretation: add a teacher-action or trust-region continuity mechanism around
the moving z=0.002 policy, rather than another small scalar reward tweak.

Robot validation remains blocked.
