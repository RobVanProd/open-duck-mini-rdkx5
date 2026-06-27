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

## Hard Progress-Failure Control

A fourth tiny PPO smoke enabled the environment's default-off
`command_progress_failure` termination so low-progress positive-command
rollouts could not finish quietly:

```text
num_timesteps: 512
actual checkpoint step: 640
behavior prior scale: -0.10
target-rate penalty: disabled
actuator-tracking penalty: disabled
command_progress_failure_enable: true
command_progress_failure_min_ratio: 0.30
command_progress_failure_warmup_steps: 80
command_progress_failure_scale: -5.0
```

The smoke completed and exported an ONNX:

```text
output: outputs/analysis/pitch_chain_4p3_ppo_warmstart_progress_failure_control/smoke_20260627T142729Z_cpu/2026_06_27_102818_640.onnx
status: PASS_SMOKE_RUN
```

Targeted seed screen:

```text
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_PROGRESS_FAILURE_CONTROL_SEED1_SEED4_SCREEN.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0007, track ratio -0.0092, velocity p95 1.2083, tracking p95 0.1199
seed 4: vx  0.0033, track ratio  0.0417, velocity p95 1.0734, tracking p95 0.1016
```

This shows the existing hard progress-failure termination is also insufficient
as a tiny PPO correction. The exported policy still settles into the same
near-standstill basin under the fitted bridge.

## Restore-Policy KL Loss Controls

A default-off Playground PPO loss hook was added to penalize KL divergence from
the current policy distribution to the restored checkpoint policy distribution
on the same rollout observations:

```text
flag: --restore_policy_kl_scale
loss term: scale * KL(current_policy || restored_policy)
scope: optimizer-level PPO loss, not environment reward
requires: --restore_checkpoint_path
```

Two tiny CPU controls tested whether this stronger behavior-preservation
mechanism could keep the warm-started policy inside the walking basin:

```text
restore_policy_kl_scale: 1.0
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_RESTORE_POLICY_KL_CONTROL_SEED1_SEED4_SCREEN.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0005, track ratio -0.0064, velocity p95 1.3022, tracking p95 0.1198
seed 4: vx  0.0033, track ratio  0.0410, velocity p95 1.2986, tracking p95 0.1236

restore_policy_kl_scale: 100.0
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_RESTORE_POLICY_KL100_CONTROL_SEED1_SEED4_SCREEN.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0006, track ratio -0.0078, velocity p95 1.2197, tracking p95 0.1150
seed 4: vx  0.0033, track ratio  0.0413, velocity p95 1.2210, tracking p95 0.1195
```

The hook is wired and activated, but these two bounded controls still collapse
to near-standstill. A likely explanation is that the restored feed-forward
policy is being queried on low-progress states generated by the updated policy;
matching the restored policy there does not force recovery back into the
walking rollout distribution.

## Conclusion

The PPO warm-start path is viable, but the naive tracking-correction reward
recipe, the behavior-preserving control, low-alpha blending, and built-in
adaptive-KL control, and the hard progress-failure control are closed as
standalone fixes. Restore-policy KL loss at scales `1.0` and `100.0` is also
closed as a standalone candidate. They reproduce the same old failure mode:

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
collapse into a near-standstill. The existing command-progress failure
termination does not change that outcome in a tiny PPO update. Restore-policy
KL is now available as a default-off tool, but these screens show that simply
anchoring to the restored feed-forward policy distribution on PPO rollout states
does not solve the warm-start collapse.
