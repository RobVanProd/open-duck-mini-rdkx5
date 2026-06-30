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

## Next Direction

Before spending more A100 time on this exact path, debug why the z=0.002 C0-restore training process exits after step 0 without an exit file or traceback. Reasonable next checks:

- run a tiny local or Colab CPU/GPU reproduction with `export_min_step=0` to verify the C0 checkpoint restore/export path;
- test a different z=0.002 moving parent such as C2 if C0 restore is suspect;
- add stronger remote process/exit capture around the training subprocess so signal kills are recorded.

Do not treat this as evidence against the z=0.002 tracking-margin recipe itself.
