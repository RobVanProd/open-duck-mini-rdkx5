# PPO Warm-Start Tracking-Correction Smoke Result

This was an offline-only PPO resume-path probe. It did not run robot tests,
SSH, deploy, or change robot runtime behavior.

## Purpose

The pitch-chain `4.3 rad/s` PPO-shape BC student is stable under the strict
fitted-backlash x=0.08 gate, but it remains held by fitted-bridge tracking:

```text
duration_complete: 8/8
falls: 0/8
mean vx: ~0.039 m/s
mean track ratio: ~0.49
max tracking p95: ~0.25-0.26 rad
```

The next question was whether this deployable student could be converted into
a real Brax PPO checkpoint, resumed, and corrected with a short closed-loop
update instead of another static BC relabel.

## Step-0 Warm-Start

The BC NPZ was converted into a Brax PPO checkpoint and exported through the
same ONNX export path used by Playground training:

```text
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_WARMSTART_STEP0_EXPORT_FIDELITY.md
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
```

The exported step-0 ONNX was then run through the strict fitted-backlash
x=0.08 8-seed gate:

```text
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_WARMSTART_STEP0_MULTI_SEED_FITTED_BACKLASH.md
status: HOLD_CANDIDATE_TRACKING
duration_complete: 8/8
falls: 0/8
mean vx: 0.0396 m/s
mean track ratio: 0.4944
max pitch velocity p95: 3.6200-3.7078 rad/s
max tracking p95: 0.2522-0.2583 rad
```

This validates the checkpoint/export plumbing. The PPO step-0 policy preserves
the known stable-but-tracking-held baseline.

## Naive PPO Tracking-Correction Smoke

A tiny CPU PPO update was run from the warm-start checkpoint:

```text
num_timesteps: 512
actual checkpoint step: 640
task: flat_terrain_backlash
command_x: fixed 0.08
bridge: fitted-like, 3-4 tick delay, tau 0.06-0.14 s, velocity 2.25-3.75 rad/s
behavior prior: enabled, weak anchor to BC student
target-rate penalty: enabled
actuator-tracking penalty: enabled
forward-progress / shortfall / wrong-direction terms: enabled
```

The smoke completed and exported an ONNX:

```text
output: outputs/analysis/pitch_chain_4p3_ppo_warmstart_tracking_correction_smoke/smoke_20260627T133903Z_cpu/2026_06_27_093952_640.onnx
status: PASS_SMOKE_RUN
```

Targeted seed screen:

```text
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_TRACKING_CORRECTION_SMOKE_SEED1_SEED4_SCREEN.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0007, track ratio -0.0082, velocity p95 1.1218, tracking p95 0.1121
seed 4: vx  0.0031, track ratio  0.0392, velocity p95 1.2200, tracking p95 0.1078
```

The update reduced target velocity and tracking error by nearly freezing the
gait. This is not a deployable improvement.

## Conclusion

The PPO warm-start path is viable, but the naive tracking-correction reward
recipe is closed as a standalone fix. It reproduces the same old failure mode:

```text
safe/calm policy
lower target velocity
lower tracking error
almost no forward motion
```

The next closed-loop branch must preserve the step-0 forward behavior more
explicitly while applying tracking correction. A useful next probe should be
trust-region style PPO fine-tuning, very short update windows, or a stronger
behavior-preservation mechanism that treats loss of forward progress as an
immediate hold, not as an acceptable way to reduce tracking error.
