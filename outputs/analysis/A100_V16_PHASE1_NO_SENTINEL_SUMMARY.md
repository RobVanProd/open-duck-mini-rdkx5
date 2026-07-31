# A100 V16 Phase-1 No-Sentinel Summary

status: `HOLD_A100_V16_PHASE1_NO_SENTINEL`

## Context

V16 was added as a V5-anchored continuation recipe. It must restore:

```text
policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/checkpoint_2026_06_23_205634_368640
```

The intended first run was:

```text
recipe: movement_bootstrap_v16
stop_after_phase: 1
timesteps_scale: 1.0
phase_gate_seeds: 0-3
phase_gate_max_fall_fraction: 0.0
phase_gate_min_track_ratio_mean: 0.25
phase_gate_min_vx_mean: 0.02
```

## Result

The A100 session launched, uploaded both repos, installed the pinned dependency
stack, and reached the V16 phase-1 runner. The partial phase output contains:

```text
smoke_manifest.start.json
stdout.txt
stderr.txt
events.out.tfevents...
```

`stdout.txt` shows the restored V5 checkpoint path and the phase-1 PPO startup:

```text
Observation size: 101
STEP: 0 reward: -52.476234436035156 reward_std: 93.70592498779297
Skipping checkpoint/export at step 0; export_min_step=1
```

No final manifest, ONNX, staged plan, exit sentinel, or artifact bundle was
created. The remote log stopped after the phase manifest, and the Colab status
API reported the session as idle while the raw console still appeared to show a
Python process. A second tiny diagnostic was started briefly, which made the
runtime state ambiguous. The session was then explicitly terminated to avoid
orphaned or overlapping remote jobs.

## Interpretation

This is an infrastructure/session hold, not a V16 policy verdict.

Do not treat this as evidence that V16 failed or succeeded. The only confirmed
training signal is step 0. There is no candidate checkpoint to evaluate.

## Local Evidence

```text
outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260624T111058Z/remote_final.log
outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260624T111058Z/partial_phase1/stdout.txt
outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260624T111058Z/partial_phase1/stderr.txt
outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260624T111058Z/partial_phase1/smoke_manifest.start.json
```

## Next Action

Before another V16 A100 launch, improve the Colab workflow so it can detect a
remote process that remains alive without an exit sentinel and avoid starting a
second job in the same session. Then rerun V16 phase 1 from a clean A100
session.

No robot tests, SSH, deployment, runtime behavior changes, or policy deployment
were performed.
