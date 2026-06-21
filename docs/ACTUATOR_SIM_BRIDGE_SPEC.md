# Actuator Sim-To-Real Bridge Spec

Last updated: 2026-06-21

## Executive Summary

Suspended `x=0.08` is blocked because free-air dynamic tracking failed. The
failure is sustained pitch-chain lag, not gross joint mapping:

- Suspended `x=0.08` looked like coherent air-walking to the operator.
- Joint identity, software sign/order, home pose, and IMU tilt gates are not
  pointing to a gross mapping failure.
- Pitch-joint p95 tracking error during suspended `x=0.08` was about
  `0.12-0.17 rad`.
- The best target-to-actual alignment was about `3-4` control ticks behind the
  target in suspended replay.

Grounded replay remains blocked until actuator dynamics are bridged in
sim/training. The next policy should be trained/evaluated against a more honest
actuator model before being tested on the floor.

## Evidence Summary

| test | target velocity range | p95 tracking error | max tracking error | estimated lag | bus read errors | action saturation | visual observation | gate |
|---|---:|---:|---:|---:|---:|---:|---|---|
| suspended `x=0.0` | small post-startup pitch target ranges | pitch joints `0.0029-0.0100 rad` | pitch joints `0.0030-0.0140 rad` post-startup | `1-6` ticks on tiny target ranges | `8 / 747` | `0%` | no gross issue reported | `WARN_PROCEED_WITH_CAUTION` |
| suspended `x=0.08` | pitch target p95 velocity `3.09-5.22 rad/s` | pitch joints `0.1179-0.1673 rad` | pitch joints `0.1757-0.2688 rad` | `3-4` ticks in replay alignment | `20 / 747` | `right_hip_pitch 2.01%`, `right_ankle 0.13%` | coherent air-walking, no gross twitch/asymmetry reported | `HOLD` |
| sine sweep `0.25 Hz`, `0.03 rad` | max sine target velocity `0.047 rad/s` | max `0.0102 rad` | max `0.0116 rad` | effective `80-132 ms` in diagnostic loop | `14` total deltas | not policy-driven | clean low-speed single-joint motion | `PASS_WITH_CAUTION` |
| sine sweep `0.5 Hz`, `0.03 rad` | max sine target velocity `0.094 rad/s` | max `0.0110 rad` | max `0.0127 rad` | effective `79-92 ms` in diagnostic loop | `19` total deltas | not policy-driven | clean low-speed single-joint motion | `PASS_WITH_CAUTION` |

Key interpretation:

- Smooth single-joint targets are tracked well at low target velocity.
- Suspended `x=0.08` asks for pitch target velocities more than `55x` faster
  than the `0.5 Hz`, `0.03 rad` sine target.
- The sim-to-real target is not "make the servo follow a slow sine"; it is
  training a gait whose target changes remain trackable by the real actuator
  chain under measured delay and velocity limits.

Regenerate the suspended replay target-velocity evidence with:

```bash
python3 tools/analyze_policy_target_velocity.py \
  outputs/first_evidence/<timestamp>/suspended_policy_replay_x008_thresholds.jsonl \
  --output outputs/first_evidence/<timestamp>/suspended_policy_replay_x008_target_velocity_analysis.md
```

## Runtime And Training Actuator Contract

Current deployed runtime contract:

- control frequency: `50 Hz`
- control dt: `0.02 s`
- policy action shape: `[1, 14]`
- policy action range: tanh-normalized continuous action
- action scale: `0.25 rad`
- target equation:

```text
target = home + action * action_scale
```

Runtime target stages:

```text
ONNX action
  -> motor_targets_pre_rate_limit_rad
  -> motor_targets_post_rate_limit_rad
  -> motor_targets_sent_rad
```

Current configured runtime target velocity limit:

```text
max_motor_velocity = 5.24 rad/s
```

The audit indicates the training stack randomizes action delay only around
`0-3` environment steps. Real evidence now suggests the deployed actuator and
feedback chain behaves closer to about `4-7` ticks, or `80-130 ms`, depending
on test and analysis method.

Important caveat: sine sweep lag is an effective target-to-feedback lag from a
Python diagnostic loop that sets a target and then reads feedback. It is not a
precise servo-internal latency number. It is still useful because the same
hardware path is used for evidence collection.

## Hardware Context

The ST3215 is a 1 Mbps TTL bus servo with position, load, speed, and input
voltage feedback. Waveshare lists the ST3215 idling speed as
`0.222 sec / 60 deg` at `12 V`, which is about:

```text
(pi / 3 rad) / 0.222 s = 4.72 rad/s
```

Waveshare also lists idling current around `180-200 mA` and locked-rotor
current around `2.7 A` for this servo family.

No-load speed is not the same as loaded, multi-joint, reversing gait tracking.
The deployed runtime `max_motor_velocity = 5.24 rad/s` is near or above the
published no-load speed, so sim/runtime assumptions are likely optimistic for
real walking under load, linkage drag, voltage sag, reversals, cable motion,
print compliance, and multiple moving joints.

Reference: https://www.waveshare.com/wiki/ST3215_Servo

## Proposed Sim Actuator Model

### 1. Action / Target Delay

Baseline random delay:

```text
3-8 ticks at 50 Hz
```

Wider stress range:

```text
2-10 ticks at 50 Hz
```

Apply delay per episode and optionally per joint. Per-joint delay should be
small but nonzero to model left/right and hip/knee/ankle variation.

### 2. First-Order Actuator Lag

Use a first-order lag on motor targets:

```text
y[t] = y[t-1] + alpha * (target[t] - y[t-1])
alpha = 1 - exp(-dt / tau)
```

Recommended tau range:

```text
0.06-0.14 s
```

At `dt = 0.02 s`, this implies roughly:

| tau_s | alpha |
|---:|---:|
| 0.06 | 0.283 |
| 0.10 | 0.181 |
| 0.14 | 0.133 |

Randomize `tau` per episode and add per-joint asymmetry.

### 3. Velocity Limit

Do not assume `5.24 rad/s` is always achievable.

Train with randomized effective max target velocity:

```text
2.5-4.7 rad/s
```

Stress-test lower limits for knees and ankles. Allow per-joint variation and
per-episode voltage/load effects.

### 4. Acceleration / Jerk Limit

Rapid reversals are harder than straight-line no-load motion. Add one or more
of:

- acceleration clipping on target changes
- jerk clipping on target changes
- action-rate penalty in reward
- target-velocity penalty in reward
- curriculum that starts with smoother targets and increases command range

### 5. Observation Delay / Stale Feedback

Add only after actuator lag is modeled.

Initial model:

```text
hold-last joint observation for 0-1 ticks
```

Rare dropout model:

```text
low-probability hold-last position/velocity for one tick
```

Do not overfit to CRC read errors yet. Current evidence shows read CRCs during
motion, but write errors stayed zero and slow sine tracking stayed clean. Treat
CRC as a watch item unless correlated with control damage.

### 6. Joint Asymmetry

Randomize per build and per episode:

- hip pitch, knee, and ankle bandwidth
- left/right delay
- knee/ankle velocity limits lower than hip
- small gain/lag asymmetry

The goal is not to reproduce one exact Duck. It is to train a policy that
remains stable under plausible actuator-chain variation.

## Training Objective Changes

Add or evaluate:

- action-rate penalty
- target-velocity penalty
- tracking-friendly smoothness term
- stability reward under actuator lag
- command curriculum:

```text
x = 0.00 -> 0.04 -> 0.08 -> higher
```

Evaluation should report more than reward:

- target velocity p50/p95/p99/max per joint
- target acceleration/jerk per joint
- action delta p50/p95/p99/max per joint
- simulated actuator tracking error p50/p95/p99/max
- action saturation percentage
- delay/lag robustness score

## Validation Gates Before Robot Deployment

### Sim-Side Gates

Before exporting a candidate policy:

- target velocity p95 is reduced compared with current suspended `x=0.08`
- action saturation is low and not sustained
- simulated actuator tracking p95 is below threshold
- stable walking with `3-8` tick action/target delay
- stable walking with randomized velocity limits
- stable walking with first-order lag `tau = 0.06-0.14 s`
- stable walking with per-joint lag/asymmetry
- stable walking at command curriculum checkpoints:
  `x=0.00`, `0.04`, `0.08`

### Robot-Side Gates

First robot validation for any new policy:

- suspended replay only
- start with `x=0.0`
- then suspended `x=0.08` only if `x=0.0` is clean
- no grounded replay until suspended dynamic tracking is acceptable

Preferred suspended `x=0.08` robot gate:

```text
pitch-chain p95 tracking error < 0.05 rad
```

Acceptable caution gate:

```text
pitch-chain p95 tracking error < 0.08 rad
```

Hard holds:

- sustained post-startup pitch tracking error above `0.10 rad`
- action saturation bursts
- repeated write errors
- CRC read errors correlated with dt spikes, tracking spikes, action jumps, or
  visible twitching

CRC read errors alone remain warnings, not automatic blockers.

## Non-Goals

- Do not tune physical gains yet.
- Do not alter offsets or remaps.
- Do not change action scale or phase timing yet.
- Do not blame TPU/friction yet.
- Do not run grounded replay until suspended dynamic tracking is acceptable.
- Do not train blindly without actuator model changes.

## Immediate Next Step

Create a small training/sim PR that exposes actuator delay, first-order lag,
velocity limit, and action-rate metrics as configurable experiment parameters.
No robot behavior should change in that PR.
