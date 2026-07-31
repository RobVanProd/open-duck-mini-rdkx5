# Phase 2 z=0.002 Tracking-Margin A100 Runtime Hold

status: `HOLD_A100_INTERRUPTED_BEFORE_EXPORT`
generated_at: `2026-06-30T10:10:00Z`

## Scope

- Offline sim/training only.
- No robot test, SSH, deploy, grounded replay, or runtime behavior change.
- Workflow: `phase2-z002-tracking-margin`
- Intent: recover strict tracking margin from the moving z=0.002 C0 parent before returning to higher terrain.

## Attempts

| attempt | session | PPO envs | PPO batch | result |
|---|---|---:|---:|---|
| full shape | `open-duck-a100-phase2b` | 64 | 512 | stopped after `STEP: 0`, no checkpoint, no exit file |
| reduced shape | `open-duck-a100-phase2b` | 32 | 256 | stopped after `STEP: 0`, no checkpoint, no exit file |

Both attempts reached Playground startup and PPO step 0:

```text
Observation size: 101
Enabled restore-policy KL loss: scale=6.0
STEP: 0 reward: ...
Skipping checkpoint/export at step 0; export_min_step=1
```

Neither attempt exported an ONNX checkpoint. There is therefore no policy gate result to interpret.

## Interpretation

This is a runtime/execution hold, not a policy hold. The repeated pre-export interruption appears specific to the z=0.002 tracking-margin path using the C0 restore checkpoint on this Colab A100 session. The prior z=0.005 support, behavior-prior, and motion-floor workflows completed and exported checkpoints on the same A100 setup.

## Local Restore/Export Probe

A tiny local CPU probe was run after the A100 interruptions:

```text
output_root: outputs/phase2_domain_randomization/stage_z002_tracking_margin_restore_export_probe_cpu
platform: CPU
restore: stage_c0_terrain_z002_preserve_from_a2_gpu/.../2026_06_28_064431_245760
num_timesteps: 1
export_min_step: 0
```

Result:

- status: `PASS_SMOKE_RUN`
- returncode: `0`
- exported ONNX at step `0`
- exported ONNX at step `1`

This confirms the local C0 restore/export path is valid. The A100 issue is therefore not a missing or corrupt C0 checkpoint.

## Next Direction

Before spending more A100 time on this exact full recipe, debug why the z=0.002 C0-restore training process exits after step 0 without an exit file or traceback on Colab/A100. Reasonable next checks:

- test a different z=0.002 moving parent such as C2 if C0 restore is suspect;
- add stronger remote process/exit capture around the training subprocess so signal kills are recorded.

Do not treat this as evidence against the z=0.002 tracking-margin recipe itself.
