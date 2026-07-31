# Movement Bootstrap V13 A100 Phase-1 Summary

status: `HOLD_PHASE_FREEZE_OR_LOW_PROGRESS`

## Run

- session: `open-duck-a100`
- hardware: A100
- workflow: `staged-curriculum`
- recipe: `movement_bootstrap_v13`
- phase: `phase1_signed_failure_low_command`
- PR head: `dff8d69`
- JAX: `0.7.2`
- jaxlib: `0.7.2`
- Brax: `0.14.2`
- MuJoCo: `3.9.0`
- MuJoCo MJX: `3.9.0`

## Phase-1 Training

- requested timesteps: `220000`
- exported checkpoint step: `245760`
- elapsed training time: `619.68 s`
- signed failure scale: `-120.0`
- reward_clip_min: `-10.0`
- command x range: `[0.04, 0.06]`
- fitted actuator bridge: enabled
- ONNX SHA256: `23176692fe6f7f9f94c68d7bfad25d3f79293ef82172455c93ee982e89dbce01`

Training rewards were negative through the phase:

```text
STEP 0:      -189.59
STEP 81920:  -217.27
STEP 163840: -204.54
STEP 245760: -191.81
```

This confirms the signed failure / negative reward path was active during
training.

## Phase Gate

Gate command:

```text
x = 0.08
duration = 5 s
bridge = fitted
platform = gpu
```

Gate result:

```text
overall_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
candidate_gate_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
termination: duration_complete
```

Key metrics:

```text
forward_tracking_ratio: 0.01601
mean local vx: 0.0013 m/s
max_action_saturation_pct: 0.0
max_pitch_tracking_p95_rad: 0.07430
max_sent_target_velocity_p95_rad_s: 0.14604
max_abs_body_pitch_p95_rad: 0.05504
min_base_height_m: 0.15368
min_reward_mean: 0.53903
```

Interpretation: V13 stayed upright and inside the measured actuator envelope,
but still produced a near-standstill policy. The signed terminal penalty changed
training reward scale, but did not make forward motion cheaper than no-motion in
phase 1.

## Decision

Do not run phase 2.
Do not deploy this policy.
Do not request robot validation.

V13 is evidence that the current command-progress failure mechanism is still not
sufficient to escape the no-motion basin. The next offline step should inspect
whether the training environment exposes the low-progress failure signal often
enough during optimization and whether the main reward terms still dominate the
terminal penalty.
