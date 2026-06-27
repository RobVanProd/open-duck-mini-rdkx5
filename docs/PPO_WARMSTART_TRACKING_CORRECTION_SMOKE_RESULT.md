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

## Behavior-Preservation Control

A second tiny PPO smoke removed the explicit target-rate and actuator-tracking
penalties, lowered the learning rate, and strengthened the frozen behavior
prior:

```text
num_timesteps: 512
actual checkpoint step: 640
behavior prior scale: -0.10
target-rate penalty: disabled
actuator-tracking penalty: disabled
learning rate: 1e-5
clipping epsilon: 0.03
```

Targeted seed screen:

```text
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_BEHAVIOR_PRESERVATION_CONTROL_SEED1_SEED4_SCREEN.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0008, track ratio -0.0104, velocity p95 1.2540, tracking p95 0.1213
seed 4: vx  0.0035, track ratio  0.0433, velocity p95 1.1863, tracking p95 0.1170
```

This control shows the collapse is not only caused by the tracking penalty.
Under the current PPO resume/reward setup, even a small behavior-anchored update
moves the policy from stable forward motion into a calm near-standstill.

## Low-Alpha PPO Update Direction Blend

To test whether the behavior-control PPO update contained a useful small
direction before the full update froze, the step-0 ONNX and behavior-control
step-640 ONNX were blended by initializer value:

```text
alphas: 0.01, 0.02, 0.05, 0.10
screen artifact: outputs/analysis/PPO_WARMSTART_BEHAVIOR_CONTROL_WEIGHT_BLENDS_SEED1_SEED4_SCREEN.md
screen status: HOLD_CANDIDATE_TRACKING
```

Targeted seed screen:

```text
alpha 0.01: vx mean 0.0388, track ratio 0.4847, tracking hold
alpha 0.02: vx mean 0.0397, track ratio 0.4966, tracking hold
alpha 0.05: vx mean 0.0395, track ratio 0.4939, tracking hold
alpha 0.10: vx mean 0.0401, track ratio 0.5010, tracking hold
```

The blends preserved the baseline walking basin, but they did not materially
reduce the fitted-bridge tracking plateau. The useful region between step-0 and
the frozen PPO update is effectively a no-op for the gate.

## Adaptive-KL PPO Control

A third tiny PPO smoke tested Brax's adaptive-KL learning-rate schedule while
keeping the explicit target-rate and actuator-tracking penalties disabled:

```text
num_timesteps: 512
actual checkpoint step: 640
behavior prior scale: -0.10
target-rate penalty: disabled
actuator-tracking penalty: disabled
learning rate schedule: ADAPTIVE_KL
desired KL: 0.0005
learning rate range: 1e-6 to 3e-5
```

The smoke completed and exported an ONNX:

```text
output: outputs/analysis/pitch_chain_4p3_ppo_warmstart_adaptive_kl_control/smoke_20260627T141703Z_cpu/2026_06_27_101744_640.onnx
status: PASS_SMOKE_RUN
```

Targeted seed screen:

```text
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_ADAPTIVE_KL_CONTROL_SEED1_SEED4_SCREEN.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0006, track ratio -0.0080, velocity p95 1.0896, tracking p95 0.1052
seed 4: vx  0.0034, track ratio  0.0426, velocity p95 1.1028, tracking p95 0.1064
```

This shows built-in adaptive-KL learning-rate control is not sufficient by
itself. It still lets the warm-started policy leave the walking basin and reduce
tracking error by nearly stopping.

## Conclusion

The PPO warm-start path is viable, but the naive tracking-correction reward
recipe, the behavior-preserving control, low-alpha blending, and built-in
adaptive-KL control are closed as standalone fixes. They reproduce the same old
failure mode:

```text
safe/calm policy
lower target velocity
lower tracking error
almost no forward motion
```

The next closed-loop branch must preserve the step-0 forward behavior more
explicitly while applying tracking correction. A useful next probe should be
trust-region style PPO fine-tuning at the policy-distribution level, an
imitation/advantage formulation that keeps the update inside the walking basin,
or a stronger behavior-preservation mechanism that treats loss of forward
progress as an immediate hold, not as an acceptable way to reduce tracking
error. Low-alpha post-hoc blending and the default Brax adaptive-KL schedule are
also not enough; they either preserve the baseline without moving the gate or
collapse into a near-standstill.
