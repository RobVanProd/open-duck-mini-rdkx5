# Movement Bootstrap V2 A100 Summary

generated_at: `2026-06-23`

## Executive Summary

The `movement_bootstrap_v2` staged curriculum completed on a Colab A100 CUDA
backend, but the final policy is **not a robot candidate**.

The run confirms that simply raising the minimum command, tightening
velocity-tracking reward shape, and adding stronger progress / shortfall
pressure still does not escape the current local optimum:

```text
stable / low action saturation / low target velocity
but not enough forward locomotion
and tracking is still above the candidate gate threshold
```

No robot motion, SSH, deployment, runtime behavior change, or policy overwrite
was performed.

## Backend And Artifact

- backend: Colab A100 / CUDA
- JAX backend: `gpu`
- artifact bundle:
  `outputs/analysis/colab_cli/open-duck-a100b-staged-curriculum-20260623T154051Z/open_duck_colab_cli_staged-curriculum_20260623T154144Z_artifacts.tar.gz`
- artifact bundle sha256:
  `4e708a406e996ff66ae14151af32561867e0f58451f1912153f6e5c1b1085b66`
- final policy sha256:
  `e9ff4fdb325908afb9adc5bc5bc83ed96ba1a0b355931cab9a55a5ecafbe427c`
- final policy source path:
  `/content/open_duck_staged_curriculum_cli/03_phase3_fitted_bridge_preserve_motion/smoke_20260623T155952Z_gpu/2026_06_23_160805_368640.onnx`
- workflow exit status: `1` because candidate gates held

Training phase elapsed times:

| phase | elapsed |
|---|---:|
| phase 1 | `558.8 s` |
| phase 2 | `499.1 s` |
| phase 3 | `503.4 s` |
| total training | `1561.3 s` |

## Recipe

Recipe: `movement_bootstrap_v2`

Final phase highlights:

- command range: `x = 0.06..0.12 m/s`
- zero-command probability: `0.0`
- tracking sigma: `0.00125`
- forward progress scale: `6`
- forward shortfall scale: `-6`
- required forward ratio: `0.6`
- action-rate scale: `-0.04`
- action-magnitude scale: `-0.01`
- actuator bridge:
  - delay: `3..6 ticks`
  - tau: `0.06..0.14 s`
  - velocity limit: `3.0..4.7 rad/s`
  - per-joint variation: `0.15`

## Candidate Gates

### `x=0.0`

Status: `HOLD_CANDIDATE_TRACKING`

| metric | value | threshold |
|---|---:|---:|
| max action saturation | `0.0000 %` | `1.0000 %` |
| max pitch tracking p95 | `0.1388 rad` | `0.0800 rad` |
| max sent target velocity p95 | `0.6699 rad/s` | `2.5000 rad/s` |
| max abs body pitch p95 | `0.2623 rad` | `0.2500 rad` |
| min base height | `0.1408 m` | `0.1200 m` |
| min reward mean | `0.4471` | `0.3000` |
| max abs forward velocity error | `0.0021 m/s` | n/a |

Interpretation: the candidate does not saturate actions and target velocity is
low, but zero-command tracking and body pitch are outside the gate. This alone
blocks robot validation.

### `x=0.08`

Status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

| metric | value | threshold |
|---|---:|---:|
| max action saturation | `0.0000 %` | `1.0000 %` |
| max pitch tracking p95 | `0.1473 rad` | `0.0800 rad` |
| max sent target velocity p95 | `0.6892 rad/s` | `2.5000 rad/s` |
| max abs body pitch p95 | `0.3103 rad` | `0.2500 rad` |
| min base height | `0.1392 m` | `0.1200 m` |
| min reward mean | `0.4414` | `0.3000` |
| min forward command tracking ratio | `0.0286` | `0.2500` |
| max abs forward velocity error | `0.0777 m/s` | n/a |
| max forward shortfall cost mean | `0.7051` | n/a |

Mode tracking ratios:

| mode | mean local forward velocity | command tracking ratio |
|---|---:|---:|
| vanilla | `0.0031 m/s` | `0.0384` |
| fitted | `0.0023 m/s` | `0.0286` |
| stress | `0.0027 m/s` | `0.0340` |

The evaluator's forward-shortfall diagnostic is now visible and reports large
normalized shortfall despite a `PASS_DIAGNOSTIC` label:

| mode | progress ratio mean | progress ratio p95 | normalized shortfall mean | shortfall cost mean |
|---|---:|---:|---:|---:|
| vanilla | `0.0384` | `0.5855` | `0.4923` | `0.4845` |
| fitted | `0.0286` | `0.6920` | `0.5157` | `0.5619` |
| stress | `0.0340` | `0.9284` | `0.5753` | `0.7051` |

Interpretation: the policy produces occasional forward bursts, but average
forward progress is still effectively standstill for a `0.08 m/s` command.

## Decision

Do not run this policy on the robot.

This recipe moved in the right direction on instrumentation and reward
visibility, but it did not solve the locomotion bootstrap problem. The next
offline work should not repeat the same three-phase recipe. It should make the
training objective care about sustained episode-level displacement and/or use a
stronger motion prior from a policy that already moves, while keeping the
actuator bridge gates in place.

Recommended next offline direction:

- add an episode-level forward displacement / minimum-progress gate to the
  training reward, not just per-step shaping
- evaluate whether the current reward is dominated by alive / posture terms
  despite shortfall pressure
- consider distillation or warm-start from `BEST_WALK_ONNX_2` movement
  structure, then penalize actuator-hostile target dynamics
- keep the two sim gates before any robot validation:
  - `x=0.0`: stable, low tracking error
  - `x=0.08`: meaningful sustained forward progress

No robot tests are justified by this result.
