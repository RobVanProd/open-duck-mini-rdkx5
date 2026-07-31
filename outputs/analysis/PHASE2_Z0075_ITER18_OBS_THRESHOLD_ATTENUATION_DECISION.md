# Phase 2 z=0.0075 Iter18 Obs-Threshold Attenuation Decision

status: `HOLD_ITER18_OBS_THRESHOLD_ATTENUATION_NOT_SUFFICIENT`

This is offline sim/analysis only. It did not SSH, deploy, run robot tests,
grounded replay, train, or change runtime behavior.

## Question

Iter13 remains the best deployable feed-forward candidate for rough z=0.0075
with `home-support` reset and intermediate pushes, but it fails seed 0 on the
first push by a forward lunge/pitchover at about sample 105. Global output gain
`0.95` can make seed 0 pass, but it regresses seed 6, so Iter18 tested whether a
deployable observation-threshold wrapper could apply attenuation only in the
observed lunge state.

The wrapper preserves the deployable policy contract:

```text
obs[1,101] -> continuous_actions[1,14]
```

and applies:

```text
action = where(obs[index] >= threshold, action * scale, action)
```

## Tool

- tool: `tools/wrap_policy_obs_threshold_scale.py`
- base policy: `policy/candidates/phase2_z0075_iter13_push_window_recovery_rate150_20260704/candidate.onnx`
- gate condition: rough `z=0.0075`, `home-support`, `x=0.08`, corrected fitted bridge, intermediate push

All wrapper verification reports returned `PASS_ONNX_OBS_THRESHOLD_SCALE_VERIFY`
with `max_abs_error = 0.0` against the expected thresholded action transform.

## Tested Wrappers

| candidate | sha256 | obs condition | scale |
|---|---|---:|---:|
| `policy/candidates/phase2_z0075_iter18_obs1ge080_scale095_20260704/candidate.onnx` | `30e2a7b9b82c7177f5dd7d69918eef9d17cf3e9730b94f6743ba596668249614` | `obs[1] >= 0.80` | 0.95 |
| `policy/candidates/phase2_z0075_iter18_obs1ge100_scale095_20260704/candidate.onnx` | `7a660ab213aac3bfd2887c53f7010fa530a399d4e6ce8b4225c3fffc716001a3` | `obs[1] >= 1.00` | 0.95 |
| `policy/candidates/phase2_z0075_iter18_obs1ge065_scale095_20260704/candidate.onnx` | `375428a51597e25f672e77215b18b0ea68f8984637480fd376c46624bb45e4a5` | `obs[1] >= 0.65` | 0.95 |
| `policy/candidates/phase2_z0075_iter18_obs1ge065_scale090_20260704/candidate.onnx` | `8c14132e2d4481efe57d9fdc14d82e8110d6c9e374b4219551f92140a86a26ec` | `obs[1] >= 0.65` | 0.90 |
| `policy/candidates/phase2_z0075_iter18_obs1ge065_scale085_20260704/candidate.onnx` | `69f211159765ddcb7afe580c3af1706f2991f78af8d2a5c5d77f7af660ba40aa` | `obs[1] >= 0.65` | 0.85 |

## Seed 0 Screen

Condition:

- task: `rough_terrain_backlash`
- command_x: `0.08`
- bridge: corrected fitted bridge
- terrain z scale: `0.0075`
- reset mode: `home-support`
- push interval: `1.0-1.5s`
- push magnitude: `0.075-0.125`
- duration: `5s`
- seed: `0`

| wrapper | status | samples | termination | mean vx | track ratio | pitch p95 | base min | max pitch vel p95 | max tracking p95 | push success |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `obs[1]>=0.80 scale=0.95` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 106 | `fall_or_nan` | 0.1898 | 2.3731 | 1.0676 | 0.0018 | 1.5482 | 0.1854 | 0.0000 |
| `obs[1]>=1.00 scale=0.95` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 106 | `fall_or_nan` | 0.1902 | 2.3777 | 1.0717 | 0.0012 | 1.5482 | 0.1854 | 0.0000 |
| `obs[1]>=0.65 scale=0.95` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 106 | `fall_or_nan` | 0.1878 | 2.3471 | 1.0603 | 0.0051 | 1.5506 | 0.1835 | 0.0000 |
| `obs[1]>=0.65 scale=0.90` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 111 | `fall_or_nan` | 0.1861 | 2.3259 | 1.0911 | -0.0055 | 1.5712 | 0.1837 | 0.0000 |
| `obs[1]>=0.65 scale=0.85` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 107 | `fall_or_nan` | 0.1781 | 2.2265 | 1.0344 | 0.0157 | 1.5756 | 0.1817 | 0.0000 |

## Decision

`HOLD_ITER18_OBS_THRESHOLD_ATTENUATION_NOT_SUFFICIENT`

Single-channel `obs[1]` threshold attenuation is not enough to repair the seed0
first-push lunge. The best case delays the failure from about sample 106 to
sample 111, while still producing a high track-ratio forward lunge and zero push
success. The stronger `0.85` scale begins to introduce max corrected-envelope
velocity excess without solving the fall.

Do not promote any Iter18 wrapper. Do not continue scalar threshold/gain sweeps
as the next Phase 2 action.

## Next Recommendation

The next branch should be contrastive and push-window specific:

1. collect or reuse traces from the full-gain seed0 lunge, the eval-only
   gain-0.95 seed0 pass, and the gain-0.95 seed6 late collapse
2. build a lunge/recovery classifier or gate-aware live-oracle update that
   distinguishes those histories, rather than applying a single observation
   channel scale
3. gate immediately on seeds `0,2,6` under the same rough z=0.0075
   intermediate-push condition

Robot validation remains blocked.
