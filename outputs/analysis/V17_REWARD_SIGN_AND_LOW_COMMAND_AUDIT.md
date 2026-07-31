# V17 Reward Sign And Low-Command Audit

This is an offline audit following the A100 `movement_bootstrap_v17` phase-1
hold. No robot tests, SSH, deployment, runtime behavior changes, or training
were performed.

## Question

V17 trained with hard signed-progress shaping over `x=0.04-0.06` but failed the
phase gate at `x=0.08`. The audit asked:

1. Was the phase-1 candidate evaluated under the intended reward overrides?
2. Is the local forward-velocity sign convention inconsistent between reward
   code and evaluator code?
3. Did V17 at least learn forward motion inside its own training command range?

## Source Audit

The source code does not show a sign mismatch:

- `joystick._update_command_window_progress()` uses
  `signed_vx = local_vx * sign(command_x)` and accumulates that distance.
- `reward_forward_progress()`, `cost_forward_shortfall()`, and
  `cost_forward_wrong_direction()` use the same `local_vel[0] * sign(command_x)`
  convention.
- The closed-loop evaluator reports `get_local_linvel(data)[0]` as
  `local_forward_velocity_m_s` and computes command tracking as
  `mean_local_vx / command_x`.

The command-progress termination is delayed and one-tick:

- V17 phase 1 sets `command_progress_failure_enable=True`,
  `command_progress_failure_min_ratio=0.40`, and
  `command_progress_failure_warmup_steps=60`.
- The env ORs this failure into `done`, then applies the reward for that tick.
- Rewards are multiplied by `dt=0.02`, so a `command_progress_failure_scale` of
  `-260` contributes about `-5.2` reward on the terminating tick before clipping.

## x=0.08 Replay With Reward Overrides

The reward-overridden `x=0.08` replay held on all four seeds:

```text
runs: 4
falls_or_terminations: 4
duration_complete: 0
track_ratio_mean: -0.2367
mean_local_vx_mean: -0.0189 m/s
```

Seeds `0`, `2`, and `3` terminate at the `60`-sample command-progress failure
boundary. Seed `1` reverses and collapses earlier at sample `32`.

## x=0.04 Replay With Reward Overrides

V17 also fails at `x=0.04`, the low end of its own phase-1 training command
range:

```text
runs: 4
falls_or_terminations: 4
duration_complete: 0
track_ratio_mean: -0.6911
mean_local_vx_mean: -0.0276 m/s
```

| seed | samples | termination | mean local vx | track ratio | body pitch p95 | base height min |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 60 | `fall_or_nan` | -0.0026 | -0.0652 | 0.0826 | 0.1535 |
| 1 | 35 | `fall_or_nan` | -0.0949 | -2.3730 | 0.0073 | 0.0961 |
| 2 | 60 | `fall_or_nan` | 0.0078 | 0.1945 | 0.0261 | 0.1526 |
| 3 | 60 | `fall_or_nan` | -0.0208 | -0.5206 | 0.0766 | 0.1586 |

## Interpretation

V17 did not fail because the evaluator used the wrong sign or omitted the
phase-1 reward overrides. The reward terms are active, the sign convention is
consistent, and the policy still fails below the easiest command it was trained
to solve.

This points away from an `x=0.08`-only gate problem and toward the discovery
objective itself. The delayed command-progress termination catches low progress
after `60` steps, but PPO still learned a low/reverse-progress behavior. The
hard-progress pressure may be too delayed, too sparse, or still dominated by
short-horizon support strategies.

## Recommendation

Do not launch V17 phase 2 and do not launch another large A100 run yet.

The next recipe should be a simpler low-command discovery experiment, graded at
the same low command it trains on. It should test whether dense per-step signed
progress and wrong-direction suppression can produce any coherent forward
motion before adding `x=0.08`, actuator bridge transfer, or stability
consolidation.
