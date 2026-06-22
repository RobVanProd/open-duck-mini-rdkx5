# Sim-To-Real Results Summary

Last updated: 2026-06-22

## Executive Summary

Current recommendation: **do not run grounded replay yet**.
No more robot motion is recommended until the sim actuator bridge eval is
reviewed.

The first evidence gates no longer point to a gross IMU axis flip, policy hash
mismatch, joint order failure, or zero-command policy explosion. The Duck can
hold home pose, pass the labeled IMU tilt sanity check, pass software feedback
joint identity, and run suspended `x=0.0` with clean timing and good tracking.

The first nonzero suspended command, `x=0.08`, looked like normal walking in
the air to the operator, but telemetry shows sustained dynamic tracking lag and
increased servo-bus read errors. Follow-up single-joint actuator sine sweeps at
`0.25 Hz` and `0.5 Hz` tracked well at small amplitude, which narrows the issue:
the robot can follow simple single-joint smooth targets, but the walking policy
target waveform is much more aggressive and exposes the effective delay.

Offline sim work has now reproduced the actuator-bridge degradation on a CUDA
backend and narrowed the local `7900 XTX` hold to the raw Open Duck
`mjx_env.step(...)` path on ROCm:

- CUDA L4 closed-loop eval: `PASS_CLOSED_LOOP_REPRODUCTION`
- local ROCm reset: `PASS`
- local ROCm direct Open Duck `mjx_env.step(...)`: `TIMEOUT`
- local CPU direct Open Duck `mjx_env.step(...)`: `PASS`

This keeps the robot parked. The local ROCm blocker is a backend workstream,
not a reason to revisit robot testing.

## Evidence Files

Small summaries:

- `outputs/analysis/ACTUATOR_RESPONSE_FIT.md`
- `outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_X0_15S.md`
- `outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_15S.md`
- `outputs/analysis/CPU_CANDIDATE_GATE_STEP8960_POS_TARGET_RATE_X008_HOLD.md`
- `outputs/analysis/CPU_CANDIDATE_GATE_STEP32800_HOLD.md`
- `outputs/analysis/CPU_ACTUATOR_BRIDGE_PILOT_SUMMARY.md`
- `outputs/analysis/POLICY_SIM_CONTRACT_AUDIT.md`
- `outputs/analysis/SIM_ACTUATOR_BRIDGE_EVAL.md`
- `outputs/analysis/FIRST_EVIDENCE_SUMMARY.md`
- `outputs/first_evidence/20260621T202826Z/imu_tilt_labeled_summary.md`
- `outputs/first_evidence/20260621T202826Z/joint_identity_summary.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x0_after_wire_routing_threshold_gate.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds_gate.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds_analysis.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds_warnings.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_target_waveform_analysis.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_target_velocity_analysis.md`
- `outputs/first_evidence/20260621T215022Z/actuator_sine_sweep_025_summary.md`
- `outputs/first_evidence/20260621T215022Z/actuator_sine_sweep_05_summary.md`

Raw JSONL logs and terminal logs remain outside git by default.

## Config Snapshot

From `outputs/analysis/FIRST_EVIDENCE_SUMMARY.md`:

- board hostname: `ubuntu`
- runtime path: `/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5`
- policy SHA256: `3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067`
- `imu_upside_down`: `True`
- `start_paused`: `True`
- `phase_frequency_factor_offset`: `0.0`
- IMU calibration file: `None`

Notable live offsets:

- `left_knee`: `-1.4880 rad`
- `right_knee`: `0.0798 rad`

The large left-knee offset remains a watch item, but home pose and joint
identity evidence show the compensated feedback path is not obviously broken.

## Home Pose Gate

From `outputs/first_evidence/20260621T215022Z/home_pose_after_pr4_analysis.md`:

- samples: `213`
- gyro means: `[0.0000, -0.0001, 0.0001]`
- upright accel mean: `[1.6028, 0.4430, 9.6695]`
- accel is +Z dominant
- joint tracking errors are small at home

Status: **PASS / watch x-axis accel bias**.

This weakens the gross IMU-axis-flip hypothesis. Upright accel is not perfectly
centered on x/y, but it is stable and +Z dominant.

## IMU Tilt Gate

From `outputs/first_evidence/20260621T202826Z/imu_tilt_labeled_summary.md`:

- upright accel: `[1.622, 0.338, 9.792]`
- nose forward changes `accel_x` negative: delta `-5.984 m/s^2`
- nose backward changes `accel_x` positive: delta `+4.602 m/s^2`
- left tilt changes `accel_y` negative: delta `-5.498 m/s^2`
- right tilt changes `accel_y` positive: delta `+4.994 m/s^2`

Status: **PASS / IMU frame now less likely as root cause**.

The policy receives raw gyro and accel, not RPY. These logs show the physical
tilt axes are separated and repeatable.

## Foot Contact Gate

From `outputs/analysis/FIRST_EVIDENCE_SUMMARY.md`:

- contact channels changed independently
- all four contact states appeared
- raw GPIO `False` maps to contact `True`

Status: **PASS for electrical responsiveness**.

The operator sequence was not timestamp-labeled, so this proves electrical
response and polarity behavior, not a strict left-first/right-first script.

## Joint Identity Gate

From `outputs/first_evidence/20260621T202826Z/joint_identity_summary.md`:

- all 14 joints passed software feedback identity
- commanded `+/-0.03 rad` produced measured `+/-0.03 rad` responses
- worst small-step tracking error: `0.0060 rad`
- one CRC mismatch printed during the run

Status: **PASS for servo ID/order and feedback sign**.

Physical visual direction is still not fully annotated. This remains less
likely than dynamic tracking because the feedback identity test passed cleanly.

## Suspended Replay `x=0.0`

From
`outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x0_after_wire_routing_threshold_gate.md`:

- samples: `747`
- command: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
- gate: `WARN_PROCEED_WITH_CAUTION`
- dt mean / p95 / p99 / max: `0.02009 / 0.02009 / 0.02010 / 0.02015 s`
- read errors: `8 / 747 = 1.071%`
- write errors: `0`
- action saturation: `0%`
- bus read burst count: `0`
- post-startup tracking spikes above `0.05 rad`: `0`

Pitch joint post-startup tracking stayed small:

| joint | p95 abs tracking error |
|---|---:|
| left_hip_pitch | `0.0098 rad` |
| left_knee | `0.0082 rad` |
| left_ankle | `0.0074 rad` |
| right_hip_pitch | `0.0100 rad` |
| right_knee | `0.0056 rad` |
| right_ankle | `0.0029 rad` |

Status: **WARN_PROCEED_WITH_CAUTION**.

Interpretation: zero-command suspended replay does not show a wild policy,
gross action mapping failure, or free-air actuator collapse.

## Suspended Replay `x=0.08`

From
`outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds_gate.md`:

- samples: `747`
- command: `[0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
- gate: `HOLD_CRC_OR_TIMING`
- dt mean / p95 / p99 / max: `0.02010 / 0.02009 / 0.02010 / 0.02603 s`
- read errors: `20 / 747 = 2.677%`
- write errors: `0`
- read burst detected: `[609, 612, 612]`
- action saturation:
  - `right_hip_pitch`: `2.01%`
  - `right_ankle`: `0.13%`
- largest tracking spike: tick `200`, `left_hip_pitch`, `0.2688 rad`
- post-startup tracking spikes above `0.05 rad`: `2492`

Pitch joint tracking at `x=0.08`:

| joint | p95 abs tracking error | max abs tracking error |
|---|---:|---:|
| left_hip_pitch | `0.1433 rad` | `0.2688 rad` |
| left_knee | `0.1431 rad` | `0.2264 rad` |
| left_ankle | `0.1179 rad` | `0.2002 rad` |
| right_hip_pitch | `0.1287 rad` | `0.1757 rad` |
| right_knee | `0.1673 rad` | `0.2085 rad` |
| right_ankle | `0.1218 rad` | `0.1962 rad` |

Offline lag check, post-startup:

| joint | target range | actual range | best lag |
|---|---:|---:|---:|
| left_hip_pitch | `0.349 rad` | `0.276 rad` | `4 ticks` |
| left_knee | `0.356 rad` | `0.323 rad` | `3 ticks` |
| left_ankle | `0.244 rad` | `0.203 rad` | `3 ticks` |
| right_hip_pitch | `0.249 rad` | `0.270 rad` | `3 ticks` |
| right_knee | `0.361 rad` | `0.321 rad` | `3 ticks` |
| right_ankle | `0.280 rad` | `0.247 rad` | `3 ticks` |

Operator observation: the robot looked like it was walking in the air, with no
explicit visible twitch/asymmetry reported. This is consistent with coherent
gait motion plus measurable phase lag, not total policy nonsense.

Status: **HOLD**.

Interpretation: do not move to grounded replay. The nonzero command already
shows sustained actuator/feedback tracking lag in suspension.

## Suspended `x=0.08` Target Waveform

From
`outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_target_velocity_analysis.md`.
Post-startup ticks only.

For comparison, a `0.03 rad` sine wave has max target velocity:

- `0.25 Hz`: `0.047 rad/s`
- `0.5 Hz`: `0.094 rad/s`

The suspended `x=0.08` target waveform is much sharper:

| joint | sent step p95 | sent velocity p95 | rate-limit active | tracking p95 |
|---|---:|---:|---:|---:|
| left_hip_pitch | `0.1048 rad` | `5.22 rad/s` | `6.4%` | `0.1456 rad` |
| left_knee | `0.0759 rad` | `3.78 rad/s` | `0.4%` | `0.1428 rad` |
| left_ankle | `0.0744 rad` | `3.70 rad/s` | `2.6%` | `0.1132 rad` |
| right_hip_pitch | `0.0621 rad` | `3.09 rad/s` | `0.1%` | `0.1309 rad` |
| right_knee | `0.0956 rad` | `4.76 rad/s` | `3.1%` | `0.1680 rad` |
| right_ankle | `0.0707 rad` | `3.52 rad/s` | `0.3%` | `0.1227 rad` |

Maximum p95 target velocity ratio:

- vs `0.25 Hz` sine target: `110.7x`
- vs `0.5 Hz` sine target: `55.4x`

Interpretation: the `x=0.08` gait lag is not contradicted by the smooth sine
sweep pass. The walking policy target waveform is dramatically faster and is
already near the configured motor velocity limit in several joints.

Reusable analyzer:

```bash
python3 tools/analyze_policy_target_velocity.py \
  outputs/first_evidence/<timestamp>/suspended_policy_replay_x008_thresholds.jsonl \
  --output outputs/first_evidence/<timestamp>/suspended_policy_replay_x008_target_velocity_analysis.md
```

## Actuator Sine Sweep

Policy disabled. Robot supported on the stand. Motors were turned off after
each command. Amplitude was `0.03 rad`; each joint moved one at a time.

From
`outputs/first_evidence/20260621T215022Z/actuator_sine_sweep_025_summary.md`:

| joint | freq | p95 error | amp ratio | best lag |
|---|---:|---:|---:|---:|
| left_hip_pitch | `0.25 Hz` | `0.0074 rad` | `0.934` | `2 ticks / 91.6 ms` |
| right_hip_pitch | `0.25 Hz` | `0.0076 rad` | `0.983` | `2 ticks / 79.8 ms` |
| left_knee | `0.25 Hz` | `0.0102 rad` | `0.933` | `3 ticks / 132.1 ms` |
| right_knee | `0.25 Hz` | `0.0095 rad` | `0.917` | `3 ticks / 122.3 ms` |
| left_ankle | `0.25 Hz` | `0.0063 rad` | `0.917` | `2 ticks / 83.8 ms` |
| right_ankle | `0.25 Hz` | `0.0072 rad` | `0.917` | `3 ticks / 116.9 ms` |

Gate: `PASS_025_PROCEED_TO_05_HZ_WITH_CAUTION`.

From
`outputs/first_evidence/20260621T215022Z/actuator_sine_sweep_05_summary.md`:

| joint | freq | p95 error | amp ratio | best lag |
|---|---:|---:|---:|---:|
| left_hip_pitch | `0.5 Hz` | `0.0091 rad` | `1.033` | `2 ticks / 91.7 ms` |
| right_hip_pitch | `0.5 Hz` | `0.0085 rad` | `1.050` | `2 ticks / 90.7 ms` |
| left_knee | `0.5 Hz` | `0.0110 rad` | `0.917` | `2 ticks / 91.5 ms` |
| right_knee | `0.5 Hz` | `0.0102 rad` | `0.967` | `2 ticks / 81.9 ms` |
| left_ankle | `0.5 Hz` | `0.0083 rad` | `0.934` | `2 ticks / 85.4 ms` |
| right_ankle | `0.5 Hz` | `0.0096 rad` | `0.950` | `2 ticks / 79.0 ms` |

Gate: `PASS_05_HZ`.

The sine sweep loop logs one sample every roughly `0.039-0.046 s` because it
sets a target and then reads feedback inside the same Python loop. These lag
numbers should be treated as effective target-to-feedback lag for this
diagnostic, not as a precise servo-internal latency measurement.

Interpretation:

- Smooth single-joint tracking at `0.03 rad` is good through `0.5 Hz`.
- Effective lag is still visible, around `80-130 ms`.
- At sine-sweep target velocities, that delay produces only `~0.006-0.011 rad`
  p95 error.
- In suspended `x=0.08`, target steps are more than `55x` faster than the
  `0.5 Hz` sine target at p95, so the same delay produces much larger
  hip/knee/ankle errors.
- Read CRCs continue to appear during motion, but write errors stayed zero and
  low-frequency sine tracking stayed good.

## Root-Cause Ranking

1. **Policy target waveform too aggressive for the measured effective delay**
   - Evidence: `x=0.08` pitch joints show p95 errors of `0.1179-0.1673 rad`,
     while smooth single-joint sine sweeps at `0.25-0.5 Hz` stay near
     `0.006-0.011 rad` p95 error.
2. **Dynamic actuator/feedback delay**
   - Evidence: sine sweeps show best target-to-actual alignment at roughly
     `80-130 ms`; this is harmless for slow small sine waves but important for
     walking targets.
3. **Servo bus read reliability under motion**
   - Evidence: read errors rise from `8/747` at `x=0.0` to `20/747` at
     `x=0.08`, with one read burst. Write errors remain zero and dt is clean,
     so this is not the only explanation, but it is now a serious watch item.
4. **Policy command magnitude / action saturation at `x=0.08`**
   - Evidence: `right_hip_pitch` hits action saturation `2.01%`, while `x=0.0`
     had `0%`.
5. **Joint offsets/home pose**
   - Evidence: large left-knee offset is suspicious, but home pose and small
     identity movements track well after compensation.
6. **Joint sign/order**
   - Evidence: software feedback identity passed all joints; physical visual
     sign notes remain incomplete.
7. **IMU frame/offset**
   - Evidence: home pose and labeled tilt are +Z dominant and axis-separated.
8. **Foot contacts**
   - Evidence: electrical responsiveness passed; suspended replay does not
     depend on ground contact.
9. **Ground contact/friction/load**
   - Evidence: not tested yet; do not test until suspended `x=0.08` dynamics
     are understood.

## Next Action

Latest offline fit:

- `tools/fit_actuator_response_model.py` was run on suspended `x=0.08` replay
  and compared with suspended `x=0.0`.
- Summary artifact: `outputs/analysis/ACTUATOR_RESPONSE_FIT.md`.
- JSON artifact: `outputs/analysis/actuator_response_fit.json`.
- Fit confidence: `MEDIUM`.
- Combined delayed/lagged/velocity-limited model reduces pitch-chain model p95
  error to about `0.019-0.035 rad`.
- Best combined fit chose `delay_ticks = 3` for all pitch-chain joints.
- Best effective velocity limits were `2.25-3.75 rad/s`.
- Best tau hit the lower grid bound (`0.020 s`) in this fit, so do not
  overinterpret fitted tau; use the broader `0.06-0.14 s` training stress range
  from the bridge spec.

Latest sim/eval harness result:

- `tools/eval_policy_with_actuator_bridge.py` was run in telemetry replay mode
  on suspended `x=0.08`.
- Summary artifact: `outputs/analysis/SIM_ACTUATOR_BRIDGE_EVAL.md`.
- JSON artifact: `outputs/analysis/sim_actuator_bridge_eval.json`.
- Telemetry replay status: `PASS_TELEMETRY_REPLAY_REPRODUCTION`.
- Fitted bridge median sim/real pitch-chain p95 tracking ratio: about `0.981`.
- Fitted bridge max p95 model error: about `0.035 rad`.

Latest policy/sim contract and environment result:

- `tools/audit_policy_sim_contract.py` was run against
  `../Open_Duck_Playground` with `../envs/open-duck-playground/bin/python`.
- Summary artifact: `outputs/analysis/POLICY_SIM_CONTRACT_AUDIT.md`.
- JSON artifact: `outputs/analysis/policy_sim_contract_audit.json`.
- Contract status: `PASS_POLICY_SIM_CONTRACT`.
- Instantiated sim state observation length: `101`.
- Instantiated sim action size: `14`.
- Instantiated actuator order matches the runtime/policy order, including
  `neck_pitch`, `head_pitch`, `head_yaw`, and `head_roll`.
- MJCF `nu/nq/nv`: `14/21/20`.
- Home keyframe ctrl length: `14`.
- JAX backend under `../envs/open-duck-playground/bin/python`: `gpu`.
- JAX device: `rocm:0`.
- `../envs/rocm-baseline` sees the ROCm device but lacks several
  project-specific packages, so use `../envs/open-duck-playground/bin/python`
  for Open Duck sim eval and future training.
- Full MuJoCo policy-loop reproduction is no longer blocked by contract
  mismatch.

Latest closed-loop actuator bridge eval result:

- `tools/eval_policy_with_actuator_bridge.py --mode closed-loop-sim` was run
  with `--bridge-mode all`.
- Summary artifact:
  `outputs/analysis/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md`.
- JSON artifact:
  `outputs/analysis/closed_loop_actuator_bridge_eval.json`.
- Contract preflight still passes: instantiated Playground state obs `101`,
  actions `14`, matching actuator order.
- Bridge insertion point is implemented at target stage: after
  `target = home + delayed_action * action_scale` and the built-in
  `max_motor_velocity` rate limit, before `mjx_env.step(...)`.
- `state.info["motor_targets"]` remains the sent target so obs `83:97` keeps
  commanded target history.
- Closed-loop gate result: `HOLD_SIM_RUNTIME_ERROR`.
- Worker failure: `ROCM_ERROR_ILLEGAL_ADDRESS` during the JAX/MJX GPU step.

Latest ROCm/MJX isolation result:

- `tools/isolate_rocm_mjx_failure.py` was run with GPU and CPU platforms,
  steps `1,2,10,100`, and bridge tests enabled.
- Summary artifact:
  `outputs/analysis/ROCM_MJX_RUNTIME_ISOLATION.md`.
- JSON artifact:
  `outputs/analysis/rocm_mjx_runtime_isolation.json`.
- Gate result: `HOLD_PLAYGROUND_GPU_STEP`.
- Smallest failing subtest:
  `default_gpu_playground_one_step_vanilla`.
- Passing GPU subtests:
  - basic JAX arithmetic
  - JAX jit/scan
  - minimal MJX step/scan
  - Open Duck Playground contract construction
  - Open Duck Playground reset
- Failing GPU subtests:
  - Open Duck Playground one-step vanilla times out
  - Open Duck Playground multi-step vanilla times out
  - Open Duck Playground bridge path times out
  - closed-loop GPU policy eval aborts with `ROCM_ERROR_ILLEGAL_ADDRESS`
- CPU subtests show reduced-horizon usefulness:
  - CPU Playground reset and one-step pass
  - CPU closed-loop vanilla short matrix passes
  - CPU bridge/multi-step path progresses through short steps but times out
    before the full requested horizon under `120 s`
- Focused JAX allocation variants on the smallest failing GPU subtest
  `playground_one_step_vanilla` did not clear the hang:
  - `XLA_PYTHON_CLIENT_PREALLOCATE=false`: timeout
  - `XLA_PYTHON_CLIENT_MEM_FRACTION=0.50`: timeout
  - `XLA_PYTHON_CLIENT_MEM_FRACTION=0.60`: timeout
  - `XLA_PYTHON_CLIENT_ALLOCATOR=platform`: timeout
- The host currently reports `amdgpu` `cwsr_enable = 1`; changing this is a
  system-level module setting and was not attempted.
- Follow-up execution-mode checks did not clear the failure:
  - `playground_one_step_jit`: `ROCM_ERROR_ILLEGAL_ADDRESS`
  - `playground_scan_step_vanilla`: `ROCM_ERROR_ILLEGAL_ADDRESS`
- Compiler/debug variants on `playground_scan_step_vanilla` did not produce a
  usable GPU pass:
  - `JAX_DEBUG_NANS=true,JAX_DEBUG_INFS=true`: `FloatingPointError` inside MJX
    convex collision
  - `MIOPEN_DEBUG_FUSION_ENGINE_DISABLE=1`: `ROCM_ERROR_ILLEGAL_ADDRESS`
  - `MIOPEN_DEBUG_FUSION_ENGINE_DISABLE=1` plus conservative XLA flags: timeout
- The debug nan/inf failure also occurs on CPU during Playground reset because
  MJX convex collision uses a `-inf` sentinel path. Treat it as a locator for
  the collision code path, not as proof that the model state is corrupt.
- Local JAX `0.8.2` does not expose a `jax_three_fry_gpu_global_pool` config
  key, so that suggested knob was not added.
- Additional strict/Triton variants did not clear the fault:
  - `--xla_gpu_enable_triton_softmax=false`: unknown XLA flag
  - `ROCM_CHIP_COMPILER_FLAGS=-fno-fast-math -fhonor-infinities -fhonor-nans`:
    `ROCM_ERROR_ILLEGAL_ADDRESS`
  - `--xla_gpu_target_cuda_data_dir=/opt/rocm/lib`: unknown XLA flag
- Reset-state finite checks show `qpos`, `qvel`, `qacc`, `ctrl`, and
  `qfrc_constraint` are finite after reset on CPU and GPU.
- Post-reset sanitation of `qpos`, `qvel`, `qacc`, `ctrl`, and `act` does not
  fix the GPU scan-step fault. CPU sanitized scan passes; GPU sanitized scan
  still hits `ROCM_ERROR_ILLEGAL_ADDRESS`.
- MJCF contact audit found seven contact-relevant floor/foot entries without
  explicit `solref` or `solimp`. This is now a candidate offline sim-model
  probe, not a robot-runtime or training fix.
- After a full GPU unplug/replug power-cycle, a reduced one-step isolation
  matrix was rerun under
  `outputs/analysis/rocm_mjx_recheck_after_reset/`.
- Result remains `HOLD_PLAYGROUND_GPU_STEP`.
- GPU still passes basic JAX, JAX jit/scan, minimal MJX, Playground contract,
  Playground reset, and reset finite-state checks.
- GPU still fails at the Playground step layer:
  - `playground_one_step_vanilla`: timeout
  - `playground_one_step_jit`: returncode `-6`
  - `playground_scan_step_vanilla`: returncode `-6`
  - `playground_multi_step_bridge`: timeout
  - `closed_loop_policy_eval_gpu`: returncode `-6`
- CPU passes the same reduced one-step path, including one-step, JIT, scan,
  bridge, and closed-loop CPU. This weakens the stale-device-state hypothesis
  and keeps the blocker isolated to local ROCm/MJX Playground stepping.
- A focused RX `7900 XTX` architecture-override check was run after confirming
  `/dev/kfd` and `/dev/dri/renderD*` are visible through the `render` group.
  Plain JAX still reports `RocmDevice(id=0)`.
- `TENSOR_PARALLEL_SIZE=1` passed a basic JAX GPU smoke test.
- `HSA_OVERRIDE_GFX_VERSION=11.0.0` failed basic JAX with
  `ROCM_ERROR_ILLEGAL_ADDRESS`, both alone and with
  `XLA_PYTHON_CLIENT_PREALLOCATE=false` plus
  `XLA_PYTHON_CLIENT_MEM_FRACTION=0.60`.
- Do not use `HSA_OVERRIDE_GFX_VERSION=11.0.0` in this local env. The GPU is
  already detected without it, and the override breaks the smallest GPU test.
- Summary artifact:
  `outputs/analysis/rocm_mjx_isolation_gfx_override/ROCM_MJX_RUNTIME_ISOLATION.md`.
- A Google Colab NVIDIA L4 / CUDA run completed the full closed-loop actuator
  bridge eval and returned `PASS_CLOSED_LOOP_REPRODUCTION`.
- CUDA contract/eval details:
  - `state` observation size: `101`
  - action size: `14`
  - actuator order matches `BEST_WALK_ONNX_2`
  - bridge insertion point: `target_stage_direct`
  - `double_rate_limit: False`
  - vanilla, fitted, and stress modes each completed `750` samples
  - fitted pitch-chain lag: `3-4` ticks
- Summary artifact:
  `outputs/analysis/CUDA_L4_CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md`.

Choose exactly one next step: **implement the training-time actuator wrapper**,
without robot motion and without changing robot runtime behavior yet.

Purpose:

- encode the measured `80-130 ms` effective delay as a sim/training hypothesis
- encode the real motor target velocity limit and observed target-step
  distribution
- use fitted effective velocity limits around `2.25-3.75 rad/s` as evidence
  when selecting training randomization ranges
- add action-rate / target-velocity diagnostics to the training bridge notes
- use the verified `101` observation / `14` action sim environment
- use the CUDA L4 `PASS_CLOSED_LOOP_REPRODUCTION` result as the current
  closed-loop sim proof
- implement the JAX/MJX training actuator wrapper next

Do not patch runtime behavior, action scale, gains, offsets, or phase timing
until the bridge spec is reviewed.

Do not run more robot motion or grounded replay until a candidate policy is
trained with the actuator bridge and passes suspended validation.

## Post-Merge CPU Pilot Runs

After the default-off Playground actuator bridge and RDK training workflow were
merged, small local CPU pilots were run to validate the offline training/export
and packaging path on `main`.

Summary artifact:

```text
outputs/analysis/CPU_ACTUATOR_BRIDGE_PILOT_SUMMARY.md
```

Results:

- step-level CPU bridge smoke: `PASS_ACTUATOR_BRIDGE_SMOKE`
- tiny `256` timestep PPO smoke: `PASS_SMOKE_RUN`
- `8192` timestep target-rate pilot: `PASS_SMOKE_RUN`, non-deployable
- `8192` timestep zero-penalty pilot: `PASS_SMOKE_RUN`, non-deployable
- `8960` step positive target-rate pilot: `PASS_SMOKE_RUN`, non-deployable
- `32768` timestep zero-penalty pilot: `PASS_SMOKE_RUN`, non-deployable
- all exported ONNX files preserved the `101 -> 14` policy contract
- candidate-mode closed-loop CPU eval now distinguishes a sim-gate pass from
  failed candidate behavior:
  - `step8240_zero_penalty`, `x=0.0`: `PASS_CANDIDATE_SIM_GATE` over `15 s`
  - `step8240_zero_penalty`, `x=0.04`:
    `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` over `15 s`
  - `step8240_zero_penalty`, `x=0.08`:
    `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` over `15 s`
  - `step8240_target_rate`, `x=0.08`:
    `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` over `15 s`
  - `step8240_negative_target_rate`, `x=0.08`:
    `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` over `15 s`
  - `step8960_positive_target_rate`, `x=0.08`:
    `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` over `15 s`
  - `step32800_zero_penalty`: `HOLD_CANDIDATE_FALL_OR_TERMINATION` over `2 s`
- the review-only `step8240_zero_penalty` ONNX is preserved under
  `policy/candidates/open_duck_mini_actuator_bridge_cpu_pilot_20260622_step8240/`

Interpretation:

- The merged training loop, ONNX export, summary, and package tooling work.
- The small CPU PPO shape is a correctness path, not a candidate generator.
- The short CPU pilots either passed the zero-command stability gate or held on
  nonzero forward-command gates because mean forward velocity stayed near zero.
  They are preserved as training/export evidence, not as walking candidates.
- The step8960 positive target-rate pilot stayed stable and smooth but still had
  effectively no forward progress at `x=0.08`
  (`min_forward_command_tracking_ratio = -0.0027`).
- A stronger CPU forward-curriculum probe reached step `61440` and is recorded
  in `outputs/analysis/CPU_FORWARD_PROBE_STEP61440_HOLD.md`. It passed the
  corrected CPU `x=0.0` candidate gate but still held at `x=0.08`:
  `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`, with
  `min_forward_command_tracking_ratio = -0.0005`.

Next offline move: run a larger CUDA-backed candidate training job with
command-tracking retained under the actuator bridge, and keep
`--eval-role candidate` command-tracking gates in front of any robot-side
approval discussion.

## Current ROCm / MJX Recheck

After the local GPU/device reset and cost-scale sign fix, a compact 7900 XTX
ROCm/MJX recheck was run:

```text
outputs/analysis/rocm_mjx_recheck_after_cost_sign/ROCM_MJX_RUNTIME_ISOLATION.md
```

Result:

- `basic_jax`: `PASS`
- `minimal_mjx_step`: `PASS`
- `playground_one_step_vanilla`: `TIMEOUT`
- `playground_one_step_jit`: `FAIL`
- gate: `HOLD_PLAYGROUND_GPU_STEP`

Interpretation: the local GPU can run basic JAX and a minimal MJX model, but
the Open Duck Playground GPU step path remains blocked. Use CPU or CUDA-backed
eval/training for correctness until the Playground ROCm step failure is fixed.

## ROCm Version-Matrix Probe

Consolidated matrix summary:

```text
outputs/analysis/ROCM_VERSION_MATRIX_SUMMARY.md
```

A disposable ROCm env tested the first version-matrix lead:

```text
env: ../envs/open-duck-playground-rocm-playground005
jax/jaxlib: 0.8.2
jax-rocm7-pjrt/plugin: 0.8.2+rocm7.2.1
mujoco/mujoco-mjx: 3.9.0
playground: 0.0.5
evidence: outputs/analysis/rocm_mjx_version_matrix_playground005/
```

Result:

- `basic_jax`: `PASS`
- `minimal_mjx_step`: `PASS`
- `playground_contract_only`: `PASS`
- `playground_reset`: `PASS`
- `playground_direct_mjx_step` on GPU: `TIMEOUT`
- `playground_direct_mjx_step` on CPU: `PASS`
- gate: `HOLD_PLAYGROUND_GPU_STEP`

Interpretation: matching the CUDA-passing `playground==0.0.5` dependency does
not clear the local 7900 XTX Open Duck MJX direct-step hang while MuJoCo/MJX is
still `3.9.0`. Future ROCm work should test older MuJoCo/MJX versions in
disposable envs; do not mutate the known `../envs/open-duck-playground` env.

A second disposable ROCm env tested older MuJoCo/MJX:

```text
env: ../envs/open-duck-playground-rocm-mujoco337
jax/jaxlib: 0.8.2
jax-rocm7-pjrt/plugin: 0.8.2+rocm7.2.1
mujoco/mujoco-mjx: 3.3.7
playground: 0.0.5
evidence: outputs/analysis/rocm_mjx_version_matrix_mujoco337/
```

Result:

- `basic_jax`: `PASS`
- `minimal_mjx_step`: `PASS`
- `playground_contract_only`: `PASS`
- `playground_reset`: `PASS`
- `playground_direct_mjx_step` on GPU: `TIMEOUT`
- `playground_direct_mjx_step` on CPU: `PASS`
- gate: `HOLD_PLAYGROUND_GPU_STEP`

Interpretation: downgrading MuJoCo/MJX to `3.3.7` with `playground==0.0.5`
also does not clear the local 7900 XTX direct Open Duck MJX step hang.

A third disposable ROCm env tested MuJoCo/MJX `3.2.7`:

```text
env: ../envs/open-duck-playground-rocm-mujoco327
jax/jaxlib: 0.8.2
jax-rocm7-pjrt/plugin: 0.8.2+rocm7.2.1
mujoco/mujoco-mjx: 3.2.7
playground: 0.0.5
evidence: outputs/analysis/rocm_mjx_version_matrix_mujoco327/
```

Result:

- `basic_jax`: `PASS`
- `minimal_mjx_step`: `PASS`
- `playground_contract_only`: `PASS`
- `playground_reset`: `FAIL` on GPU and CPU
- `playground_direct_mjx_step`: `FAIL` on GPU and CPU
- failure: `AttributeError: 'Data' object has no attribute '_impl'`
- reclassified gate: `HOLD_ENV_API_INCOMPATIBLE`

Interpretation: MuJoCo/MJX `3.2.7` is incompatible with the current
`playground==0.0.5` collision helper / Open Duck env path, so it is not a
candidate local ROCm fix.

Future disposable ROCm package probes should use the dry-run-first helper:

```bash
python3 tools/run_rocm_version_matrix.py
```

Apply mode creates only disposable `../envs/open-duck-playground-rocm-*` envs
and then runs the direct-step matrix:

```bash
python3 tools/run_rocm_version_matrix.py --apply
```

Add `--force-recreate` only when intentionally replacing existing disposable
matrix envs.

## ROCm MJX Model Feature Audit

An offline model-feature audit was added for the Open Duck MJCF/MuJoCo model:

```text
docs/ROCM_MJX_MODEL_FEATURE_AUDIT.md
outputs/analysis/ROCM_MJX_MODEL_FEATURE_AUDIT.md
outputs/analysis/rocm_mjx_model_feature_audit.json
```

Result:

```text
compile_status: PASS_MUJOCO_COMPILE
nq / nv / nu: 21 / 20 / 14
bodies / joints / geoms / sites / sensors: 18 / 15 / 47 / 5 / 15
mesh assets: 28
contact-relevant compiled geoms: left_foot_bottom_tpu, right_foot_bottom_tpu, floor
```

Interpretation: the current model compiles without stepping physics. The most
useful future ROCm minimization probe is mesh TPU foot collision against the
floor plane, because the local hold remains inside the full Open Duck
`mjx_env.step(...)` path.

## ROCm Reduced Model Probe

An offline reduced-model probe was added:

```text
docs/ROCM_MJX_REDUCED_MODEL_PROBE.md
outputs/analysis/ROCM_MJX_REDUCED_MODEL_PROBE_SUMMARY.md
outputs/analysis/rocm_mjx_reduced_model_probe_summary.json
```

Result:

```text
single raw mjx.step on GPU: PASS
10-step lax.scan of mjx.step on CPU: PASS
10-step lax.scan of mjx.step on GPU: TIMEOUT / ROCM_ERROR_ILLEGAL_ADDRESS
```

Disabling contact did not clear the GPU 10-substep hold, and replacing TPU foot
collision meshes with simple boxes plus removing visual meshes did not clear it
either. The local ROCm blocker is now narrowed to the JAX/ROCm scanned substep
execution path around `mjx.step`, not MJCF compile, single raw MJX stepping, or
foot contact alone.

Loop-mode follow-up:

```text
GPU baseline n_substeps=10 loop_mode=scan: TIMEOUT
GPU baseline n_substeps=10 loop_mode=fori: TIMEOUT
GPU baseline n_substeps=10 loop_mode=python: PASS
GPU baseline n_substeps=10 loop_mode=python_block_each: PASS
```

Interpretation: repeated MJX stepping can run on ROCm when driven by a host
Python loop. The local hold is tied to JAX/XLA control-flow lowering of repeated
`mjx.step`, so a slow local ROCm correctness-eval workaround may be possible.
CUDA remains the full closed-loop eval/training backend.

## CUDA Candidate Handoff

The current CUDA candidate handoff is recorded in:

```text
outputs/analysis/CUDA_CANDIDATE_HANDOFF_READY.md
```

Recent repo fixes prepared the next manual Colab/CUDA run:

- explicit `--jax-platform` support prevents accidental local ROCm use in CPU
  gates and makes CUDA gates request GPU explicitly
- candidate packaging treats standalone target-velocity summaries as optional,
  while still enforcing the training manifest, contract audit, and candidate
  sim gate evidence
- CUDA artifact import now reports a conservative review gate from the bundle

Next useful action remains:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate
```

Run that generated cell only in a trusted manual CUDA/Colab session. Browser
automation is still blocked by Google's secure-login warning, and robot motion
remains blocked until a candidate reaches reviewed sim-gate status.
