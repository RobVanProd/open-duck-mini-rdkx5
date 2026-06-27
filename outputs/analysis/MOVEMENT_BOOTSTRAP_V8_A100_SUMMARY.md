# Movement Bootstrap V8 A100 Summary

status: `HOLD_NON_DEPLOYABLE`

This was an offline A100 staged-curriculum run. It did not SSH, deploy, touch
the robot, or change runtime behavior.

## Candidate

- recipe: `movement_bootstrap_v8`
- initial checkpoint:
  `policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320`
- final ONNX sha256:
  `b8528e43083e3b9ea920a2847e6a9cfb30e11f7960433565f0945eb529bc4642`
- preserved candidate:
  `policy/candidates/movement_bootstrap_v8_overshoot_stabilized_standstill_20260623/`
- robot validation: `BLOCKED`

## Gates

| gate | status | samples | termination | mean_local_vx | track_ratio | max_pitch_vel_p95 | max_tracking_p95 | body_pitch_p95 | base_height_min |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| x=0.0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0003 | NA | 0.2186 | 0.0863 | 0.0539 | 0.1537 |
| x=0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0190 | 0.2760 | 0.0871 | 0.2062 | 0.1486 |

## Interpretation

V8 fixed the immediate v7 lunge/fall failure shape. At `x=0.08`, all modes ran
for the full 750 samples, body pitch stayed below the candidate gate limit, base
height stayed healthy, action saturation was `0%`, and pitch-chain target
velocity was far below the measured actuator envelope.

The cost is that forward motion was erased:

```text
x=0.08 fitted mean local vx: 0.0015 m/s
x=0.08 fitted command tracking ratio: 0.0190
candidate threshold: 0.25
```

The result is therefore not a deployable policy and not a robot candidate. It
does narrow the next offline target: keep overshoot damping, but rebalance or
anneal it so the policy does not choose standstill as the easiest stable answer
to nonzero command.

## Next Offline Target

The next recipe should test one of these changes before another robot-side
validation request:

- reduce or anneal `forward_overshoot`, `forward_pitch`, and `forward_pitch_rate`
  after early stabilization
- raise command-window progress and shortfall pressure enough that `x=0.08`
  standstill is unattractive
- stage commands around `0.04-0.06` first, then expand to `0.08` only after
  measurable progress survives
- keep the fitted actuator bridge and velocity envelope active

Robot validation remains blocked.
