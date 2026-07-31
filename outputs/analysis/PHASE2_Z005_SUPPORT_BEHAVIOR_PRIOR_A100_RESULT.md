# Phase 2 z=0.005 Support Behavior-Prior A100 Result

status: `HOLD_LOW_FORWARD_PROGRESS`
generated_at: `2026-06-30T09:10:00Z`

## Scope

- Offline sim/training only.
- No robot test, SSH, deploy, grounded replay, or runtime behavior change.
- A100 Colab session: `open-duck-a100-phase2`
- Workflow: `phase2-z005-support`
- Candidate name: `phase2_z005_support_behavior_prior_cuda`
- Warm start: Phase A2 corrected-bridge candidate checkpoint.
- Behavior-prior MLP: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`

## Training Run

- returncode: `0`
- elapsed_s: `778.88`
- latest ONNX step: `122880`
- latest ONNX sha256: `b4338cf3c092a2cbc439646efb9a7e6720ecbe6b11cc3441a4734c14c6daa0da`
- actionable stderr warnings: `0`

The Colab wrapper downloaded the official artifact bundle after the session became idle. The bundle also contained files from the previous z=0.005 run because the remote output root was reused; the compact sweep below uses only the current `smoke_20260630T083803Z_gpu` checkpoints.

## Compact CPU Sweep

Evaluator:

- corrected-knee actuator fit: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- bridge mode: `fitted`
- commands: `x=0.0`, `x=0.08`
- duration: `1.0 s`
- platform: CPU
- measured velocity envelope: `2.0-3.25 rad/s`

| checkpoint | x=0.0 | x=0.08 | max pitch vel p95 | max tracking p95 | x=0.08 track ratio | mean local vx |
|---|---|---|---:|---:|---:|---:|
| `40960` | `PASS` | `HOLD_LOW_FORWARD_PROGRESS` | 1.4195 | 0.2109 | 0.1625 | 0.0130 |
| `81920` | `PASS` | `HOLD_LOW_FORWARD_PROGRESS` | 1.4179 | 0.2127 | 0.1661 | 0.0133 |
| `122880` | `PASS` | `HOLD_LOW_FORWARD_PROGRESS` | 1.4045 | 0.2117 | 0.2163 | 0.0173 |

## Interpretation

The behavior prior preserved safety and the corrected actuator envelope, but it did not preserve enough forward motion on z=0.005 support terrain. The best checkpoint remained below the compact promotion thresholds:

- track ratio `0.2163 < 0.25`
- mean local vx `0.0173 < 0.02 m/s`

This is consistent with the prior support-only z=0.005 hold: the current z=0.005 recipe is too conservative and strangles forward progress. Small scalar behavior-prior variants are unlikely to be the right next move.

## Next Direction

Do not promote this run. The next z=0.005 experiment should preserve the Phase A2 walking/action manifold more directly, for example by using a stronger teacher-action/DAgger-style continuity signal or by staging z=0.005 support from a verified walking rollout instead of relying on reward-side support penalties alone.
