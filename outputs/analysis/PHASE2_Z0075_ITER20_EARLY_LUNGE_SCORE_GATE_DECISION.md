# Phase 2 z=0.0075 Iter20 Early-Lunge Score Gate Decision

status: `HOLD_ITER20_SCORE_GATE_ATTENUATION_NOT_SUFFICIENT`

This is offline sim/analysis only. It did not train, SSH, deploy, run robot
tests, grounded replay, or change runtime behavior.

## Question

Iter19 showed that the seed0 first-push lunge is separable from the seed0
gain-0.95 pass before the lunge is fully developed. Iter20 packaged that early
contrast as a deployable ONNX linear-score gate and tested whether selective
output attenuation fixes the seed0 first-push failure.

The wrapper preserves:

```text
obs[1,101] -> continuous_actions[1,14]
```

## Linear Score

The gate uses the top early-window lunge/pass separators from Iter19:

```text
indices = [88, 46, 60, 74, 18]
score = sum((obs[indices] - centers) * weights)
scale when score >= 5.0
```

This score activates on the seed0 lunge trace and remains inactive on the
seed0 gain-0.95 pass and seed6 gain-0.95 collapse traces at the same threshold.

## Candidates

| candidate | sha256 | scale | verify |
|---|---|---:|---|
| `policy/candidates/phase2_z0075_iter20_early_lunge_score5_scale095_20260704/candidate.onnx` | `164839d2eb39d6712561afc5fe5e475886996b92a0cbf6a839da9b48201f18ba` | 0.95 | `PASS_ONNX_OBS_LINEAR_SCORE_SCALE_VERIFY` |
| `policy/candidates/phase2_z0075_iter20_early_lunge_score5_scale090_20260704/candidate.onnx` | `0de65c941e99d78a49d56b234f5b64555307488e6eb6e0c5493f9abcd929829f` | 0.90 | `PASS_ONNX_OBS_LINEAR_SCORE_SCALE_VERIFY` |

## Seed0 Screen

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

| candidate | status | samples | termination | mean vx | track ratio | pitch p95 | base min | max pitch vel p95 | max tracking p95 | push success |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `score>=5 scale=0.95` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 108 | `fall_or_nan` | 0.1811 | 2.2641 | 1.0413 | 0.0098 | 1.5796 | 0.1976 | 0.0000 |
| `score>=5 scale=0.90` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 107 | `fall_or_nan` | 0.1775 | 2.2182 | 1.0037 | 0.0200 | 1.6216 | 0.1906 | 0.0000 |

## Decision

`HOLD_ITER20_SCORE_GATE_ATTENUATION_NOT_SUFFICIENT`

The early-lunge classifier is packageable and useful diagnostically, but
selectively scaling the base action is still not the correct recovery action.
Both tested scales reproduce the same first-push forward lunge/pitchover
failure surface around sample 107-108.

Do not promote Iter20. Do not continue output-scaling wrappers as the next
Phase 2 action.

## Next Recommendation

Keep the early-lunge score as a classifier, but use it to select a different
recovery action/label source rather than multiplying the current action:

1. relabel early-lunge windows with the gain-0.95 seed0 pass behavior or another
   pass-control recovery source
2. keep seed6 gain-0.95 late collapse as a hard negative control so the recovery
   action does not become a global slowdown
3. gate immediately on seeds `0,2,6` before any full promotion test

Robot validation remains blocked.
