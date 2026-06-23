# Sim-To-Real Results Summary

Last updated: 2026-06-23

## Executive Summary

Current recommendation: **do not run grounded replay yet**.
No more robot motion is recommended until a candidate policy passes both
offline suspended-style sim gates:

- `x=0.0`: stable, low target velocity, low tracking error
- `x=0.08`: meaningful forward progress while staying inside the measured
  actuator envelope

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

CUDA candidate work on June 22, 2026 adds a second conclusion: simply adding
the actuator bridge and smoothness pressure is not enough. The 50k and 300k
Colab candidate runs produced actuator-safe near-standstill policies, and a
five-checkpoint sweep of archived compatible `odm_phase_b` ONNX policies did
the same. All selected candidates held at `x=0.08` for
`HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`.

Current offline training recommendation: adjust reward/curriculum so nonzero
forward command tracking is required before launching another candidate run.
Do not run any of these candidates on the robot.

Reward-shape analysis confirms the issue. With `tracking_sigma=0.01`,
`tracking_lin_vel_scale=12`, and `x=0.08`, zero forward velocity still receives
`52.7%` of the raw target velocity-tracking reward and about `0.1266` per tick
from that term alone. Tightening the velocity-tracking reward shape or adding
an explicit nonzero-command progress term should happen before another
candidate run.

June 23 candidate sweeps add a sharper conclusion. Multiple actuator-aware
recipes can pass the `x=0.0` sim gate, but they collapse into near-standstill
at `x=0.08`. More aggressive forward recipes produce motion, but fail posture
or termination gates. The current search is stuck between:

```text
aggressive / moves / not safe
safe / stable / does not walk
```

`tools/analyze_policy_command_sensitivity.py` shows that the latest safe
candidates are not simply ignoring `obs[6]` command_x. They change their ONNX
actions when `command_x` changes, often more than `BEST_WALK_ONNX_2` in a
synthetic upright observation. The closed-loop failure is therefore not basic
command blindness; it is that the command-conditioned action sequence does not
become effective locomotion under the actuator bridge and environment dynamics.

The next offline training direction should be a staged locomotion bootstrap:
preserve forward intent first, then progressively add the measured actuator
bridge and smoothness constraints. Do not run any current candidate on the
robot.

A June 23 staged-curriculum run on Colab L4 completed all three phases and
produced a final ONNX at:

```text
outputs/analysis/colab_cli/open-duck-l4k-staged-curriculum-20260623T122935Z/artifact/open_duck_colab_cli_staged-curriculum_20260623T122947Z/open_duck_staged_curriculum_cli/03_phase3_fitted_bridge_consolidation/smoke_20260623T125713Z_gpu/2026_06_23_130935_307200.onnx
```

It passed the offline `x=0.0` candidate sim gate, but failed the `x=0.08`
gate with `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`. The `x=0.08` fitted-bridge
track ratio was only `0.0277` against the `0.25` threshold, with mean local
forward velocity about `0.0022 m/s` for a `0.08 m/s` command. This policy is
not a robot candidate.

Follow-up offline work added a default-off `forward_shortfall` reward term to
penalize satisfying nonzero forward commands by standing still. The staged
curriculum now enables that term explicitly across all three phases while
keeping positive straight-ahead command sampling and the actuator bridge
curriculum. A tiny CPU plumbing smoke passed on June 23, 2026:

```text
outputs/analysis/STAGED_CURRICULUM_SHORTFALL_SMOKE.md
```

This only proves the new reward/CLI/checkpoint path executes. The next useful
GPU job is a full Colab/CUDA staged-curriculum run with the shortfall term, then
the same `x=0.0` and `x=0.08` candidate gates. Robot validation remains blocked.

That full staged shortfall run completed on a Colab A100 on June 23, 2026:

```text
outputs/analysis/STAGED_CURRICULUM_SHORTFALL_A100_SUMMARY.md
```

The final policy is still **not a robot candidate**. It held the zero-command
gate at low target velocity but narrowly missed pitch tracking:
`HOLD_CANDIDATE_TRACKING`, with max pitch tracking p95 `0.0851 rad` against the
`0.0800 rad` threshold. At `x=0.08`, it again failed for low forward progress:
`HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`, with fitted-bridge mean local forward
velocity about `0.0017 m/s` and command tracking ratio `0.0211`.

The A100 run confirms that simply adding `forward_shortfall` to the staged
actuator curriculum did not escape the safe standstill optimum. The next
offline training work should investigate locomotion bootstrapping, a stronger
motion prior, or an episode-level progress requirement before launching another
large run.

Follow-up inspection found that the A100 training manifests did include
`--forward_shortfall_scale`, but the packaged candidate-gate reward-term table
used the evaluator's default reward config and therefore did not list
`cost/forward_shortfall`. The gate decision remains valid because it is based
on measured local forward velocity and command tracking ratio. The evaluator now
adds a reward-config-independent forward-shortfall diagnostic to future
candidate gates.

The combined reward landscape for the failed final phase is now recorded in:

```text
outputs/analysis/FORWARD_REWARD_LANDSCAPE_SHORTFALL_CURRENT.md
```

It shows that the current final-phase shaping still leaves zero velocity
attractive at the lower end of the command curriculum. For `command_x=0.04`,
`tracking_sigma=0.0025`, `tracking_scale=25`, `forward_progress_scale=4`, and
`forward_shortfall_scale=-4`, zero velocity retains about `42%` of the shaped
target reward before alive/imitation terms. That supports shifting the next
recipe toward a stronger movement bootstrap or a higher minimum command rather
than simply repeating the same staged run.

The `movement_bootstrap_v2` A100 run completed on June 23, 2026:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V2_A100_SUMMARY.md
```

It is also **not a robot candidate**. It failed `x=0.0` with
`HOLD_CANDIDATE_TRACKING`: max pitch tracking p95 was `0.1388 rad` against the
`0.0800 rad` threshold, and body pitch p95 was `0.2623 rad` against the
`0.2500 rad` threshold. It failed `x=0.08` with
`HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`: fitted-bridge mean local forward
velocity was only `0.0023 m/s` for a `0.08 m/s` command, with command tracking
ratio `0.0286`.

This result means the current bootstrap recipe still lands in a low-motion
local optimum while also missing tracking/posture gates. The next offline work
should add a stronger episode-level displacement or minimum-progress objective,
or use a movement prior/distillation from `BEST_WALK_ONNX_2`, before launching
another large candidate run.

The next staged plan now defaults to `movement_bootstrap_v3`:

```text
outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN.md
```

This recipe keeps `movement_bootstrap_v2` reproducible but adds default-off
command-window cumulative progress and shortfall terms in the Playground
training env. The intended change is to reward sustained displacement over the
active command window, not just instantaneous forward-velocity samples. The
corresponding Playground implementation is on
`RobVanProd/Open_Duck_Playground` branch `codex/forward-progress-reward` at
commit `4c99d40`.

## Evidence Files

Small summaries:

- `outputs/analysis/ACTUATOR_RESPONSE_FIT.md`
- `outputs/analysis/CANDIDATE_RECIPE_SEARCH_SUMMARY.md`
- `outputs/analysis/FORWARD_REWARD_LANDSCAPE_SHORTFALL_CURRENT.md`
- `outputs/analysis/FORWARD_REWARD_LANDSCAPE_MOVEMENT_BOOTSTRAP_V2.md`
- `outputs/analysis/MOVEMENT_BOOTSTRAP_V2_A100_SUMMARY.md`
- `outputs/analysis/POLICY_COMMAND_SENSITIVITY.md`
- `outputs/analysis/STAGED_CURRICULUM_SHORTFALL_A100_SUMMARY.md`
- `outputs/analysis/STAGED_CURRICULUM_SHORTFALL_SMOKE.md`
- `outputs/analysis/colab_cli/open-duck-l4m-candidate-eval-only-20260623T133849Z/artifact/open_duck_colab_cli_candidate-eval-only_20260623T133902Z/staged_curriculum_20260623T130935_candidate_gate_x0.md`
- `outputs/analysis/colab_cli/open-duck-l4m-candidate-eval-only-20260623T133849Z/artifact/open_duck_colab_cli_candidate-eval-only_20260623T133902Z/staged_curriculum_20260623T130935_candidate_gate_x008.md`
- `outputs/analysis/FORWARD_REWARD_LANDSCAPE.md`
- `outputs/analysis/PHASE_B_CHECKPOINT_SWEEP_SUMMARY.md`
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
- A more aggressive CPU forward-pressure ablation also reached step `61440` and
  is recorded in
  `outputs/analysis/CPU_AGGRESSIVE_FORWARD_PROBE_STEP61440_HOLD.md`. It used
  `tracking_lin_vel_scale = 30.0`, `alive_scale = 0.5`,
  `stand_still_scale = 0.0`, `imitation_scale = 0.0`, and
  `lin_vel_x = 0.08-0.16`. It passed `x=0.0` but still held at `x=0.08` with
  `min_forward_command_tracking_ratio = -0.0014`.

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

Closed-loop host-loop follow-up:

```text
tools/eval_policy_with_actuator_bridge.py --mjx-step-loop-mode python
tools/eval_policy_with_actuator_bridge.py --mjx-step-loop-mode python_block_each
```

Tiny local `7900 XTX` smoke results:

```text
python:            PASS_CLOSED_LOOP_REPRODUCTION, 10 samples, 104.79s
python_block_each: PASS_CLOSED_LOOP_REPRODUCTION, 10 samples, 107.02s
```

Interpretation: the full closed-loop policy/eval path can run on local ROCm
when repeated MJX substeps are driven from the host instead of lowered through
XLA control flow. This is a correctness workaround for tiny local probes only.
It is not fast enough for full-horizon eval or training. CUDA remains the
confirmed backend for full candidate evaluation and training.

## PufferLib ROCm Archive Review

The local `PufferLib.rar` lead was inspected and summarized in:

```text
outputs/analysis/PUFFERLIB_ROCM_ARCHIVE_REVIEW.md
```

Result: the archive documents a PufferLib-specific PyTorch/HIP ROCm port for
Windows/WSL on `gfx1100` hardware. It is useful context for RDNA3 ROCm work, but
it does not address JAX/XLA/MuJoCo MJX or the local Open Duck
`mjx_env.step(...)` blocker. It does not change the current backend decision:
CUDA/Colab remains the full candidate eval/training backend, CPU remains for
reduced local checks, and local RX `7900 XTX` ROCm remains a backend-debug
workstream.

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
- CUDA artifact import can verify the generated `.sha256` sidecar
  automatically, with manual `--expected-sha256` still available as a fallback
- CUDA bundles include `pip_freeze.txt`, `nvidia_smi.txt`, repo commits, and
  package metadata; the failure EXIT trap no longer imports JAX/MJX runtime
- the generated CUDA cell now selects one `PYTHON_BIN`, preferring
  `/usr/bin/python3` on Colab, and passes it explicitly to `--env-python`
- the generated CUDA cell uses `GIT_ASKPASS` only when `GITHUB_TOKEN` or
  `GH_TOKEN` is already set; Colab `%%bash` interactive token prompts were
  removed because `getpass`/TTY input failed in practice
- CUDA artifact ingest can now find the newest downloaded bundle, verify its
  `.sha256` sidecar, and skip already-imported bundles by SHA256
- the generator can also write an uploadable one-code-cell Colab notebook with
  `--notebook-output`
- the generator can write a complete local handoff directory with
  `--handoff-dir`, including notebook, raw cell, and bundle import checklist
- `tools/run_colab_cli_cuda_workflow.py` now provides the preferred headless
  route: upload local RDK/Playground tarballs through `google-colab-cli`, avoid
  GitHub tokens in Colab, pin `jax/jaxlib==0.7.2`, and download the artifact
  bundle after remote eval/smoke/candidate gates
- Colab L4 smoke training passed with `jax/jaxlib==0.7.2`; an unpinned newer
  JAX install failed Brax training because `jax.device_put_replicated` had been
  removed
- patched Colab L4 closed-loop eval reran successfully after the worker JSON
  fix:

```text
overall_status: PASS_CLOSED_LOOP_REPRODUCTION
worker_returncode: 0
jax backend/device: gpu / cuda:0
samples: 750 per mode
fitted pitch-chain lag: 3-4 ticks
fitted pitch-chain joint_tracking_p95: 0.1069-0.2143 rad
```

Interpretation: the L4 path can reproduce the current policy's actuator-lag
failure signature in closed loop, and the false empty-worker-JSON hold is fixed
for future runs.

Next useful headless action:

```bash
python3 tools/run_colab_cli_cuda_workflow.py --workflow eval --run
```

After the eval artifact reports `PASS_CLOSED_LOOP_REPRODUCTION`, move to
`--workflow smoke` and then `--workflow candidate`.

Manual notebook fallback:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate
```

Run that generated cell only in a trusted manual CUDA/Colab session. Browser
automation is still blocked by Google's secure-login warning, and robot motion
remains blocked until a candidate reaches reviewed sim-gate status.

## Movement Bootstrap V3 A100 Result

The `movement_bootstrap_v3` command-window progress curriculum completed all
three A100 training phases, but the final candidate failed the first no-command
candidate gate.

Evidence:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V3_A100_SUMMARY.md
outputs/analysis/movement_bootstrap_v3_a100_summary.json
```

Key result:

```text
final candidate ONNX sha256: 85e2e29d1539edba991576583cad1869fec2f80e0d4fc0b7c0cd499018a2964d
x=0.0 fitted-bridge gate: HOLD_CANDIDATE_FALL_OR_TERMINATION
samples before termination: 79
body pitch p95: 1.1393 rad
min base height: 0.0298 m
max pitch tracking p95: 0.1190 rad
```

Interpretation: v3 escaped pure standstill but lost zero-command stability under
the fitted actuator bridge. Because `x=0.0` failed, `x=0.08` was not run. This
candidate is not deployable and should not be tested on the robot.

The subsequent v4 attempt recovered a fitted-bridge `x=0.0` stability stage but
was stopped before continuing because the missing feasibility-curve analysis was
more important than another blind curriculum escalation.

The next planned recipe is now `movement_bootstrap_v5`:

```text
phase 1: x=0.04-0.06, mild bridge, Huber-shaped smoothness costs
phase 2: x=0.04-0.06, robust fitted actuator envelope
phase 3: x=0.04-0.08, expand only after low-command motion exists
```

This is an offline training plan only. It does not change robot runtime behavior
and does not authorize robot validation.

## Robust Actuator Fit Check

The actuator response fit now supports robust selection metrics. A rerun with
trimmed RMSE and p95 absolute error selection did not raise the fitted
velocity-limit range:

```text
original RMSE:       2.25-3.75 rad/s
trimmed RMSE 95:    2.50-3.50 rad/s
p95 absolute error: 2.25-3.25 rad/s
```

Evidence:

```text
outputs/analysis/ROBUST_ACTUATOR_FIT_CHECK.md
outputs/analysis/ACTUATOR_RESPONSE_FIT_TRIMMED_RMSE95.md
outputs/analysis/ACTUATOR_RESPONSE_FIT_P95.md
```

Interpretation: the measured velocity ceiling is not obviously an
outlier-contaminated RMSE artifact. The next missing analysis is a
command-feasibility curve that sweeps command_x and reports where pitch-chain
target velocity crosses the fitted actuator envelope.

## BEST_WALK Command Feasibility Curve

The first command-feasibility curve was run for `BEST_WALK_ONNX_2` on CPU with
the fitted actuator bridge:

```text
outputs/analysis/best_walk_command_feasibility_curve_cpu/COMMAND_FEASIBILITY_CURVE.md
```

Result:

```text
x=0.00 max pitch p95 target velocity: 0.5331 rad/s
x=0.02 max pitch p95 target velocity: 0.5229 rad/s
x=0.04 max pitch p95 target velocity: 0.6609 rad/s
x=0.06 max pitch p95 target velocity: 0.7821 rad/s
x=0.08 max pitch p95 target velocity: 4.7277 rad/s
x=0.10 max pitch p95 target velocity: 5.2400 rad/s
x=0.12 max pitch p95 target velocity: 5.2400 rad/s
```

Interpretation: `x=0.08` is the first swept command where the pitch-chain p95
target velocity jumps above the measured fitted actuator envelope
(`~2.25-3.75 rad/s`). This directly supports the actuator-ceiling hypothesis for
the current baseline policy. Commands up to `x=0.06` stay inside the target-rate
envelope but show almost no forward progress in this closed-loop sim gate.

Do not spend more large training runs until the next candidate objective is
explicitly tied to this feasibility curve: make low-command movement below the
envelope work first, then raise the command ceiling gradually.

## Movement Bootstrap V5 Plan

`movement_bootstrap_v5` is now the default staged recipe in
`tools/plan_staged_curriculum_training.py`.

Evidence:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V5_PLAN.md
outputs/analysis/movement_bootstrap_v5_plan.json
```

Key changes:

```text
- starts at x=0.04-0.06 instead of x=0.08
- uses the robust fitted velocity envelope, 2.5-3.75 rad/s, before expansion
- adds opt-in pseudo-Huber costs for action-rate, target-rate,
  actuator-tracking, and forward/command shortfall terms
- expands toward x=0.08 only after low-command motion exists
```

A tiny CPU smoke validated that the new Huber reward flags are accepted by the
Playground runner and complete a minimal offline PPO run. No robot work was
performed.

The post-v5 decision is not just `pass` or `hold` on `x=0.08`. The candidate
must get its own command feasibility curve. The useful breakthrough is any
nonzero forward motion below the measured target-velocity envelope. If multiple
feasibility-curve-targeted recipes only produce motion above the envelope, the
project should stop escalating curricula and move the conclusion toward actuator
bandwidth, not another training recipe.

Stop rule:

```text
docs/CANDIDATE_FEASIBILITY_STOP_RULE.md
```

## Movement Bootstrap V5 A100 Result

The A100 `movement_bootstrap_v5` run completed, but the candidate is not
deployable.

Evidence:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V5_A100_SUMMARY.md
outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/COMMAND_FEASIBILITY_CURVE.md
```

Final candidate:

```text
sha256: 622661f17a59b82dc9e920f694a9c849336f9bb7d580e52c5e04beeef62b9750
```

Gate results:

```text
x=0.0:  HOLD_CANDIDATE_FALL_OR_TERMINATION
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

The candidate is actuator-safe at nonzero commands but nearly stationary:

```text
x=0.04 mean local vx: 0.0017 m/s, pitch p95 target velocity 1.0697 rad/s
x=0.06 mean local vx: 0.0023 m/s, pitch p95 target velocity 1.2235 rad/s
x=0.08 mean local vx: 0.0031 m/s, pitch p95 target velocity 1.4159 rad/s
x=0.12 mean local vx: 0.0070 m/s, pitch p95 target velocity 1.0454 rad/s
```

At `x=0.0` and `x=0.02`, it produces above-envelope target spikes and falls.

Interpretation: v5 did not find an in-envelope forward gait. It counts as
feasibility-targeted attempt `1 / 3` under the stop rule. Robot validation
remains blocked.

Phase checkpoint audit refined that conclusion:

```text
phase 1 x=0.0:  duration_complete, below envelope, tracking hold only
phase 1 x=0.08: fall after 80 samples, below envelope, mean local vx 0.1892 m/s
phase 2 x=0.08: fall after 61 samples, above envelope, mean local vx 0.2628 m/s
final x=0.08:   duration_complete, below envelope, mean local vx 0.0031 m/s
```

This means v5 did briefly find in-envelope forward motion in phase 1, but it was
unstable and then lost during later fitted-bridge consolidation. The next
training attempt should be framed as preserving and stabilizing the phase-1
motion pattern, not as another generic progress-reward escalation.

## Phase-1 In-Envelope Motion Lead

The phase-1 checkpoint is now preserved as a first-class evidence artifact:

```text
policy/candidates/movement_bootstrap_v5_phase1_in_envelope_unstable_20260623/candidate.onnx
sha256: dcaa47993f65f4eedf980a78255d723409873b9b65e6a7d3d1002beeea7a3b48
```

The traced `x=0.08` failure shows:

```text
samples: 80
done tick: 79 / 1.58 s
mean local vx: 0.1892 m/s
max pitch-chain p95 target velocity: 1.9529 rad/s
body pitch abs p95/max: 1.1841 / 1.4642 rad
base height min: 0.0434 m
action saturation: 0%
```

Evidence:

```text
docs/PHASE1_IN_ENVELOPE_MOTION_LEAD.md
outputs/analysis/PHASE1_X008_FAILURE_TRACE.md
outputs/analysis/phase1_x008_failure_trace.json
```

Current conclusion: stable in-envelope walking has not been produced yet, but
unstable in-envelope forward motion exists. That shifts the next target from
"prove feasibility" to "stabilize phase-1 motion without leaving the measured
actuator envelope or collapsing to standstill."

The next planned recipe is `movement_bootstrap_v6`, documented in:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V6_PLAN.md
outputs/analysis/movement_bootstrap_v6_plan.json
```

V6 is deliberately not the default recipe. It must be selected explicitly. It
keeps the fitted actuator velocity envelope active in every phase and uses
small PPO updates plus light orientation/base-height costs during consolidation.
A true teacher-policy/action-anchor loss is still not implemented; if V6 loses
the phase-1 motion again, the next offline task should add that mechanism
instead of escalating generic reward terms.

## Movement Bootstrap V6 Result

The A100 `movement_bootstrap_v6` run completed all three phases, but the final
candidate is not deployable:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V6_A100_SUMMARY.md
```

Final gates:

```text
x=0.0:  HOLD_CANDIDATE_FALL_OR_TERMINATION, 78 samples, mean local vx 0.1935 m/s
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, 750 samples, mean local vx 0.0009 m/s
```

Phase checkpoint curves show that v6 did not recover the v5 phase-1 moving
gait:

```text
phase 1 x=0.06: mean local vx 0.0004 m/s, max pitch p95 target velocity 0.1254 rad/s
phase 1 x=0.08: mean local vx 0.0009 m/s, max pitch p95 target velocity 0.1077 rad/s
phase 2 x=0.06: mean local vx 0.0005 m/s, max pitch p95 target velocity 0.1741 rad/s
phase 2 x=0.08: mean local vx 0.0010 m/s, max pitch p95 target velocity 0.1390 rad/s
```

Interpretation: v6 kept the actuator envelope active, but the stricter phase-1
search collapsed directly into standstill. This is evidence against another
generic stability/reward escalation. The next useful offline work is:

```text
1. Preserve staged training checkpoint directories in Colab artifacts.
2. Reproduce or recover the moving v5 phase-1 checkpoint with trainable state,
   not only ONNX export.
3. Add an action-level teacher/trust-region continuity mechanism before adding
   more stability pressure.
```

Robot validation remains blocked.

## V5 Phase-1 Trainable Recovery

A one-phase A100 rerun of `movement_bootstrap_v5` stopped after phase 1 and
preserved the latest trainable checkpoint:

```text
policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/
candidate sha256: 0b7d9c3b24ac047a0a7d5e2e2c15f8e03280a2e30389d4c102dd44a733ce03e5
checkpoint: checkpoint_2026_06_23_205634_368640/
```

It is still not deployable:

```text
x=0.0:  HOLD_CANDIDATE_FALL_OR_TERMINATION
x=0.08: HOLD_CANDIDATE_FALL_OR_TERMINATION
```

At `x=0.08` with the fitted bridge it reproduces the useful lead:

```text
fitted samples: 52
mean local vx: 0.2989 m/s
track ratio: 3.7362
max pitch-chain p95 target velocity: 1.7912 rad/s
max pitch tracking p95: 0.2553 rad
action saturation: 0%
```

This is now the trainable anchor for the next offline task: add continuity
pressure around this moving behavior while improving stability. Do not request
robot validation for this policy.

The next planned recipe is `movement_bootstrap_v7`: a checkpoint-anchored
continuation run that starts from
`policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/checkpoint_2026_06_23_205634_368640/`
with small PPO updates, low clipping, and light stability pressure. It is not a
true teacher-action loss yet. If v7 also collapses to standstill or remains
unstable, the next offline implementation should add an explicit teacher-action
regularizer rather than more generic reward terms.

## Movement Bootstrap V7 Result

The A100 `movement_bootstrap_v7` checkpoint-anchored run completed and is
preserved as:

```text
policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/
sha256: fa1157ea81dacbf7e7fc1dd2835963017616c8d0be3b3dc19e2389db0307def8
```

Summary:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V7_A100_SUMMARY.md
```

Gate result:

```text
x=0.0:  HOLD_CANDIDATE_TRACKING, 750 samples, max pitch tracking p95 0.0860 rad
x=0.08: HOLD_CANDIDATE_FALL_OR_TERMINATION, 60 samples, mean local vx 0.2640 m/s
```

Interpretation: checkpoint anchoring improved the zero-command case from a fall
to a near-pass tracking hold, and it preserved in-envelope forward motion at
`x=0.08`, but nonzero-command walking still falls quickly. The `x=0.08` fitted
rollout stayed under the target-velocity envelope:

```text
max pitch-chain p95 target velocity: 2.2663 rad/s
action saturation: 0%
```

So the remaining blocker is now more specifically forward-motion stability and
contact timing under fitted actuator dynamics, not actuator target-rate
violation. Robot validation remains blocked.

The compact onset trace is preserved here:

```text
outputs/analysis/V7_X008_ONSET_ANALYSIS.md
```

It shows the `x=0.08` rollout exceeding the commanded forward velocity by tick
`3` / `0.06s`, while body pitch does not exceed `0.25 rad` until tick `15` /
`0.30s`. The largest velocity and pitch collapse happen later, with local
forward velocity reaching `1.3183 m/s` at the terminal tick. This points the
next recipe toward velocity-overshoot and pitch/pitch-rate stabilization under
forward command before adding more contact-timing terms.

`movement_bootstrap_v8` is now planned as that exact offline continuation:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V8_PLAN.md
```

It starts from the v7 anchored checkpoint, keeps the fitted actuator bridge and
`2.5-3.75 rad/s` velocity envelope active, and adds default-off Playground
reward terms for forward overshoot plus forward-command pitch and pitch-rate
costs. Robot validation remains blocked.

## Movement Bootstrap V8 Result

The A100 `movement_bootstrap_v8` overshoot-stabilization run completed and is
preserved as:

```text
policy/candidates/movement_bootstrap_v8_overshoot_stabilized_standstill_20260623/
sha256: b8528e43083e3b9ea920a2847e6a9cfb30e11f7960433565f0945eb529bc4642
summary: outputs/analysis/MOVEMENT_BOOTSTRAP_V8_A100_SUMMARY.md
```

Gate result:

```text
x=0.0:  HOLD_CANDIDATE_TRACKING, 750 samples, max pitch tracking p95 0.0863 rad
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, 750 samples, fitted mean local vx 0.0015 m/s
```

Interpretation: V8 did what it was designed to do mechanically: it eliminated
the v7 `x=0.08` lunge/fall. The fitted-bridge `x=0.08` rollout completed the
full duration with `0%` action saturation, body pitch p95 `0.1953 rad`, and
healthy base height. However, it overcorrected into near-standstill:

```text
x=0.08 fitted command tracking ratio: 0.0190
candidate threshold: 0.25
max pitch-chain p95 target velocity: 0.2760 rad/s
```

The current blocker is now tightly defined: preserve V8's overshoot damping
without erasing forward progress. The next offline recipe should either anneal
the overshoot/pitch stabilizers or increase command-window progress pressure so
standing still at nonzero command is no longer an attractive solution. Robot
validation remains blocked.
