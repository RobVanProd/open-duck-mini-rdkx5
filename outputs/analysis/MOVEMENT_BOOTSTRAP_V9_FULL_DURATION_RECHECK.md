# Movement Bootstrap V9 Full-Duration Recheck

status: `HOLD_NON_DEPLOYABLE`

This was an offline CPU closed-loop sim recheck of the preserved
`movement_bootstrap_v9` candidate. It did not SSH, deploy, touch the robot, or
change runtime behavior.

## Why This Recheck Was Needed

The short checkpoint sweep made V9 look like the best middle point between V7's
lunge and V8's standstill:

```text
V7 1s x=0.08 track ratio: 1.8356
V8 1s x=0.08 track ratio: 0.2539
V9 1s x=0.08 track ratio: 0.9129
```

That sweep was intentionally short (`1.0 s` / about `50` samples). Earlier
unstable candidates usually failed around `60-80` samples, so V9 needed the
normal full-duration gate before it could be treated as a real anchor.

## Result

Policy:

```text
policy/candidates/movement_bootstrap_v9_progress_balanced_standstill_20260623/candidate.onnx
```

Command:

```text
command_x: 0.08
bridge_mode: fitted
duration: 15 s
jax_platform: cpu
```

| run | status | samples | termination | mean_local_vx | track_ratio | max_pitch_vel_p95 | max_tracking_p95 | body_pitch_p95 | base_height_min |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| seed 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 73 | `fall_or_nan` | 0.2217 | 2.7707 | 2.3669 | 0.1498 | 1.2604 | 0.0305 |
| seed 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | 0.0185 | 0.2314 | 1.7712 | 0.1850 | 0.0477 | 0.0672 |

The generated closed-loop report for the seed-1 run was created before
`closed_loop_actuator_bridge_eval.json` included the top-level seed field. The
worker command did include `--seed 1`, and the full
`sim_actuator_bridge_eval.json` records `seed: 1`.

## Interpretation

V9 is not a robot candidate and not a stable full-duration anchor. The short
one-second sweep selected a useful probe, but it cut off just before the
historical failure window.

The failure is still not an actuator-velocity or action-saturation wall:

```text
seed 0 max pitch target velocity p95: 2.3669 rad/s
seed 1 max pitch target velocity p95: 1.7712 rad/s
action saturation: 0%
measured envelope floor: about 2.25 rad/s
candidate gate velocity threshold: 2.5 rad/s
```

The remaining blocker is forward-motion stability under the fitted actuator
bridge. Seed 0 reproduces the lunge/pitch-over shape. Seed 1 fails even earlier
with base-height collapse and poor forward tracking. The exact failure shape is
rollout-sensitive, but the deployability decision is not: V9 does not survive
the full-duration `x=0.08` gate.

## Next Offline Target

Do not run another robot test and do not deploy V9.

The next useful training/tooling work is:

- expose deterministic seed control in all candidate gate summaries,
- run candidate gates across multiple seeds before declaring an anchor,
- design V10 around the `60-100` sample fall window instead of another
  target-velocity-envelope tweak,
- use a teacher/trust-region term to preserve early V7/V9 motion while adding
  explicit penalties for forward-speed overshoot, pitch growth, pitch-rate
  growth, and base-height collapse.

The objective has narrowed to: preserve in-envelope forward motion, prevent the
fall-window lunge/collapse, and avoid returning to the V8/V9 final standstill
basin.
