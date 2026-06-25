# V23 L4 Artifact Recovery Summary

status: `HOLD_V23_ARTIFACT_RECOVERED_GATE_FAILED`
generated_at: `2026-06-25T16:55:00Z`

## Summary

A second Colab L4 run recovered the V23 staged-curriculum artifact bundle after
the earlier seed sweep lost its remote runtime. The recovered package confirms
the V23 support-contact recipe trained and exported a final ONNX, but the
candidate still fails the sim gates and must not be promoted.

This is an offline-only result. No robot test, SSH, deployment, runtime behavior
change, or policy replacement was performed.

## Artifact

```text
bundle:
  outputs/analysis/colab_cli/open-duck-l4-v23-artifact-staged-curriculum-20260625T154558Z/open_duck_colab_cli_staged-curriculum_20260625T154613Z_artifacts.tar.gz

extracted:
  outputs/analysis/colab_cli/open-duck-l4-v23-artifact-staged-curriculum-20260625T154558Z/extracted/open_duck_colab_cli_staged-curriculum_20260625T154613Z

bundle exit status:
  exit_status=1
```

The bundle exit status is nonzero because candidate packaging returned a hold.
The package files were still produced and are usable as evidence.

## Candidate

```text
name:
  open_duck_mini_staged_curriculum_cli_20260625T154643Z

final ONNX:
  2026_06_25_160007_184320.onnx

sha256:
  d8a92162cfee07cb4c6f2643c5206a182882fd46c0098f93a1c65c03e99c86c7

size:
  884094 bytes

contract:
  obs[1,101] -> continuous_actions[1,14]
```

The candidate ONNX is preserved in the ignored Colab artifact tree. It is not
added as a promoted tracked policy because the gates below failed.

## Gate Results

### x=0.0 Candidate Gate

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`

| mode | samples | termination | base_height_min | mean_local_vx | pitch_tracking_p95_max | sent_target_velocity_p95_max |
|---|---:|---|---:|---:|---:|---:|
| vanilla | 71 | fall_or_nan | 0.0556 | -0.2485 | 0.1313 | 1.4454 |
| fitted | 55 | fall_or_nan | 0.0405 | -0.3327 | 0.1632 | 1.6843 |
| stress | 66 | fall_or_nan | 0.0629 | -0.2529 | 0.1246 | 1.7766 |

Gate metrics:

```text
max_action_saturation_pct:       0.0000
max_pitch_tracking_p95_rad:      0.1632
max_sent_target_velocity_p95:    1.7766 rad/s
max_abs_body_pitch_p95_rad:      0.0707
min_base_height_m:               0.0405
min_reward_mean:                 0.4201
```

### x=0.08 Candidate Gate

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`

| mode | samples | termination | base_height_min | mean_local_vx | track_ratio | pitch_tracking_p95_max | sent_target_velocity_p95_max |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 125 | fall_or_nan | 0.0452 | -0.1429 | -1.7863 | 0.0831 | 0.3429 |
| fitted | 98 | fall_or_nan | 0.0599 | -0.1717 | -2.1467 | 0.0832 | 0.6026 |
| stress | 140 | fall_or_nan | 0.0567 | -0.1232 | -1.5405 | 0.0786 | 0.4508 |

Gate metrics:

```text
max_action_saturation_pct:       0.0000
max_pitch_tracking_p95_rad:      0.0832
max_sent_target_velocity_p95:    0.6026 rad/s
max_abs_body_pitch_p95_rad:      0.0970
min_base_height_m:               0.0452
min_reward_mean:                 0.4385
min_forward_tracking_ratio:     -2.1467
max_forward_shortfall_cost_mean: 23.5323
```

## Interpretation

V23 is a decisive negative result for the first explicit support-contact reward
probe:

```text
not actuator-envelope limited:
  x=0.08 sent target velocity p95 stays below 0.61 rad/s

not action-saturation limited:
  action saturation is 0%

not robot-ready:
  x=0.0 falls in all modes
  x=0.08 moves backward in local body frame and then falls
```

This means the simple learning-objective hook:

```text
reward exactly-one-support during forward command
penalize double-support dwell during forward command
```

is not enough to create coherent weight transfer or forward support mechanics.
Do not rerun V23 unchanged.

## Next Decision

The useful next work is not another scalar reward-weight retry. Pick one
structural path:

```text
1. targeted V23 fall trace:
   inspect seed-0 x=0.04 or x=0.08 contact sequence, base height, pitch,
   local velocity, and support dwell to see how the support reward is being
   exploited or bypassed;

2. richer contact/weight-transfer teacher:
   use a horizon teacher/optimizer with explicit foot placement, support
   transition state, and body placement, not just target action tables;

3. closed-loop controller/reference generator:
   react to pitch, height, lateral velocity, and foot contacts while generating
   the next support transition.
```

Robot validation remains blocked.
