# Actuator Modeling Notes

Last updated: 2026-06-21

## Why The Sine Sweep Passed But `x=0.08` Failed

The slow sine sweep and the walking policy replay stress different parts of
the actuator chain.

The sine sweep used:

```text
amplitude = 0.03 rad
frequency = 0.25-0.5 Hz
```

For a sine wave:

```text
max velocity = 2 * pi * frequency * amplitude
```

So the tested sine targets were:

```text
0.25 Hz -> 0.047 rad/s
0.50 Hz -> 0.094 rad/s
```

These passed:

```text
max p95 tracking error ~= 0.011 rad
min amplitude ratio ~= 0.917
write errors = 0
```

Suspended `x=0.08` was much sharper:

```text
p95 pitch target velocity ~= 3.09-5.22 rad/s
p95 pitch tracking error ~= 0.12-0.17 rad
```

That is over `55x` faster than the `0.5 Hz`, `0.03 rad` sine target at p95.
The sine sweep passing therefore does not contradict the walking replay
failing. It shows the robot can track smooth, slow, single-joint targets, while
the current policy target waveform is too aggressive for the real actuator
chain.

## Why More Low-Frequency Sine Tests Are Not The Main Next Step

A `1.0 Hz`, `0.03 rad` sine wave has:

```text
2 * pi * 1.0 * 0.03 ~= 0.188 rad/s
```

That is still far below the `3-5 rad/s` target velocities seen in suspended
`x=0.08` replay. A `1.0 Hz` sine sweep can still be useful later as a hardware
gate, but it will not fully explain the walking target waveform.

The next useful model is policy-waveform fitting:

```text
sent_target -> delayed / lagged / velocity-limited actual_position
```

Fit this model against the existing suspended replay telemetry before running
more robot motion.

## Recommended First Sim Model

Use these as initial training/sim ranges, then revise after fitting:

```text
delay_ticks: UniformInt(3, 8)
tau_s: Uniform(0.06, 0.14)
effective_velocity_limit_rad_s: Uniform(2.5, 4.7)
```

Add per-joint asymmetry:

```text
hip pitch: faster / wider range
knee: medium
ankle: slower / more conservative
left-right variation: enabled
```

Add objective pressure:

```text
action-rate penalty
target-velocity penalty
tracking-friendly smoothness term
```

Evaluation must report:

```text
target velocity p95/p99/max
action delta p95/p99/max
simulated actuator tracking p95/p99/max
rate-limit activation percentage
action saturation percentage
```

## CRC / Read Error Interpretation

Read CRC warnings remain a watch item. They increased during suspended
`x=0.08`, and one read burst was detected.

However:

```text
slow sine sweeps had read CRCs but clean tracking
write errors stayed zero
dt stayed clean during replay
```

So CRC/read warnings alone are not sufficient to explain the dynamic lag. Treat
them as a secondary model only after actuator delay, lag, and velocity limits
are represented.

Do not add an aggressive feedback-dropout model until the baseline actuator
lag model reproduces the current policy degradation.

## Training Environment Note

Future training should run on the local `7900 XTX` setup. Before starting a
training job, verify the AMD/ROCm/MuJoCo environment and the MuJoCo rendering
fix. Local references observed on this workstation:

```text
../envs/rocm-baseline
../verify_scratch/render_mujoco_egl.py
../amdgpu-install_7.2.1.70201-1_all.deb
```

Do not commit local environment binaries, driver packages, screenshots, or
machine-specific cache files.
