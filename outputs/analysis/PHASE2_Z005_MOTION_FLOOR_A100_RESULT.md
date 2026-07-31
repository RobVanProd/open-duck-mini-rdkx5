# Phase 2 z=0.005 Motion-Floor A100 Result

status: `HOLD_LOW_FORWARD_PROGRESS`
generated_at: `2026-06-30T09:35:00Z`

## Scope

- Offline sim/training only.
- No robot test, SSH, deploy, grounded replay, or runtime behavior change.
- A100 Colab session: `open-duck-a100-phase2b`
- Workflow: `phase2-z005-motion-floor`
- Candidate name: `phase2_z005_motion_floor_a100`
- Warm start: Phase A2 corrected-bridge candidate checkpoint.

## Training Run

- returncode: `0`
- elapsed_s: `799.22`
- latest ONNX step: `122880`
- latest ONNX sha256: `7a030ee89d417af49faa0eb76ef5cd6796a520eff017751afb4a7f3c971ef655`
- actionable stderr warnings: `0`

Recipe intent:

- reduce support/base-height damping relative to `phase2-z005-support`
- increase command-progress pressure
- preserve the corrected actuator envelope
- keep z=0.005 no-push terrain as the active rung

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
| `40960` | `PASS` | `HOLD_LOW_FORWARD_PROGRESS` | 1.4239 | 0.2130 | 0.1610 | 0.0129 |
| `81920` | `PASS` | `HOLD_LOW_FORWARD_PROGRESS` | 1.4045 | 0.2112 | 0.1680 | 0.0134 |
| `122880` | `PASS` | `HOLD_LOW_FORWARD_PROGRESS` | 1.4028 | 0.2116 | 0.1993 | 0.0159 |

## Interpretation

The motion-floor recipe improved reward but did not restore meaningful forward motion on z=0.005 terrain. The best checkpoint remained below the compact promotion thresholds:

- track ratio `0.1993 < 0.25`
- mean local vx `0.0159 < 0.02 m/s`

This result, together with `PHASE2_Z005_SUPPORT_A100_CACHEFIX_RESULT` and `PHASE2_Z005_SUPPORT_BEHAVIOR_PRIOR_A100_RESULT`, indicates that z=0.005 terrain support is still suppressing the Phase A2 walking manifold. The current reward-side support/motion-floor variants are not enough.

## Next Direction

Do not promote this run. The next Phase 2 training branch should stop small scalar z=0.005 reward variants and either:

- back off to an intermediate z=0.0035 terrain rung, or
- add a direct teacher-action / live-oracle continuity mechanism that preserves the Phase A2 action manifold while terrain support is introduced.
