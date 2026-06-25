# Sim-To-Real Results Summary

Last updated: 2026-06-24

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

## V11 Fresh-Lineage Plan

V11 has been prepared as the next offline training experiment:

```text
recipe: movement_bootstrap_v11
plan: outputs/analysis/MOVEMENT_BOOTSTRAP_V11_TRAINING_PLAN.md
json: outputs/analysis/movement_bootstrap_v11_training_plan.json
restore checkpoint: none by default
```

This is intentionally not another V7/V9/V10 continuation. The main change is a
hard progress floor:

```text
forward_shortfall_huber_delta: 0.0
command_progress_shortfall_huber_delta: 0.0
strong wrong-direction penalty
positive x command only
fitted actuator envelope active in all phases
```

Hypothesis:

```text
V10 froze because the Huberized shortfall penalties were too gentle near zero
speed. V11 makes zero/reverse progress expensive enough to compete with the
safe standstill basin before adding stronger stability pressure.
```

This is still an offline-only candidate-generation plan. No robot validation is
allowed until a candidate passes the multi-seed sim gates.

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

`movement_bootstrap_v9` is now planned as the next offline A100 recipe:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V9_PLAN.md
```

It starts from the v7 anchored checkpoint again, not from the V8 standstill,
and keeps the fitted actuator bridge plus `2.5-3.75 rad/s` envelope active. The
deliberate difference from V8 is lighter overshoot/pitch damping paired with
stronger command-window progress pressure, to search the narrow region between
V7's lunge and V8's near-standstill.

## Movement Bootstrap V9 Result

The A100 `movement_bootstrap_v9` run completed and is preserved as:

```text
policy/candidates/movement_bootstrap_v9_progress_balanced_standstill_20260623/
sha256: e281667087140800d5b06d547ea6644fdf40af7c49897e6774ea913e5fb41839
summary: outputs/analysis/MOVEMENT_BOOTSTRAP_V9_A100_SUMMARY.md
```

Gate result:

```text
x=0.0:  HOLD_CANDIDATE_TRACKING, 750 samples, max pitch tracking p95 0.0932 rad
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, 750 samples, fitted mean local vx 0.0017 m/s
```

Interpretation: V9 did not recover the moving gait. Lighter damping plus
stronger command-window progress still converged to the same stable
near-standstill basin:

```text
V8 x=0.08 fitted track ratio: 0.0190
V9 x=0.08 fitted track ratio: 0.0206
```

The next offline work should stop making small reward-weight adjustments in the
same family. The more useful direction is checkpoint selection or explicit
teacher-action/trust-region continuity from a moving checkpoint, so
stabilization cannot silently erase the gait. Robot validation remains blocked.

## Movement Bootstrap V9 Full-Duration Recheck

A short one-second checkpoint sweep initially made V9 look like the best
middle point between V7's lunge and V8's standstill:

```text
V7 1s x=0.08 track ratio: 1.8356
V8 1s x=0.08 track ratio: 0.2539
V9 1s x=0.08 track ratio: 0.9129
```

That was useful for checkpoint selection, but it did not clear V9. The short
horizon ends at about `50` samples, while the moving candidates have been
failing around `60-80` samples.

Full-duration CPU recheck:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V9_FULL_DURATION_RECHECK.md
```

Result:

```text
seed 0: HOLD_CANDIDATE_FALL_OR_TERMINATION, 73 samples,
        mean local vx 0.2217 m/s, track ratio 2.7707,
        body pitch p95 1.2604 rad, target velocity p95 2.3669 rad/s

seed 1: HOLD_CANDIDATE_FALL_OR_TERMINATION, 32 samples,
        mean local vx 0.0185 m/s, track ratio 0.2314,
        base height min 0.0672 m, target velocity p95 1.7712 rad/s
```

Both rechecks had `0%` action saturation and stayed within the actuator target
velocity threshold. The failure is therefore not the original actuator-envelope
wall. It is full-horizon stability under forward command: either the rollout
lunges and pitches over, or it collapses before establishing useful forward
tracking.

This also exposes a tooling gap: candidate evaluation needs explicit seed
control and multi-seed full-duration gates. A single short rollout is useful for
triage but cannot promote a checkpoint to robot-candidate status.

Next offline target: design V10 around the `60-100` sample fall window. Preserve
early in-envelope forward motion with a teacher/trust-region term, then add
stability pressure for forward-speed overshoot, pitch/pitch-rate growth, and
base-height collapse without returning to the V8/V9 standstill basin.

## V7 / V9 Multi-Seed Stability Baseline

The two-seed V9 result showed two different failure modes, so the next question
was distribution, not another single rollout. An eight-seed `x=0.08`
fitted-bridge CPU baseline is now recorded in:

```text
outputs/analysis/V7_V9_MULTI_SEED_STABILITY_BASELINE.md
```

Summary:

```text
V7: 8 seeds, 5 falls, 3 duration-complete standstill holds,
    mean samples 311.75, mean track ratio 0.2351

V9: 8 seeds, 5 falls, 3 duration-complete standstill holds,
    mean samples 312.00, mean track ratio 0.3282
```

V9 did not materially improve the stability distribution versus V7. Both
policies fail across multiple surfaces:

```text
seeds 0 and 6: lunge / pitch-over
seed 5: reverse or negative local velocity failure
seeds 1 and 7: early base-height/contact collapse
seeds 2, 3, and 4: stable low-forward-progress standstill
```

Trace analysis confirms the two main V9 failure modes:

```text
V9 seed 0: 73 samples, track ratio 2.7707,
           body pitch abs p95 1.2604 rad, base height min 0.0305 m

V9 seed 1: 32 samples, track ratio 0.2314,
           body pitch abs p95 0.0496 rad, base height min 0.0672 m
```

This means V10 should be judged by multi-seed distribution shift. The baseline
to beat is `5/8` falls, mean lifetime about `312` samples, and `3/8` seeds
surviving only by standing still. V10 should keep the broad stabilizer set:
forward-speed overshoot, pitch/pitch-rate growth, base-height collapse, contact
support timing, and teacher/trust-region continuity for gait shape.

A follow-up V9 four-surface trace comparison is recorded in:

```text
outputs/analysis/v9_four_surface_trace_recheck_x008_fitted/V9_FOUR_SURFACE_ONSET_COMPARISON.md
```

It shows the regimes branch within the first few ticks by contact/support state
and velocity sign. The failures are not one common lunge mechanism with several
late endings:

```text
seed 0: forward lunge, pitch >0.25 rad at tick 15
seed 1: contact-asymmetric collapse, height <0.12 m at tick 29, no pitch >0.25
seed 2: standstill, full duration, no height collapse
seed 5: reverse/negative velocity by tick 25, then pitch/base-height failure
seed 6: lunge after initial negative velocity and contact switching
seed 7: contact-asymmetric collapse, height <0.12 m at tick 25, no pitch >0.25
```

The next planned offline recipe is now:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V10_PLAN.md
```

V10 should target behavioral consistency across seeds first. If it does not
move the distribution away from the V7/V9 baseline, stop iterating on this
anchor lineage and switch to a structurally different bootstrap.

## V10 Training Recipe Prepared

V10 is now an executable staged recipe, not only a plan:

```text
recipe: movement_bootstrap_v10
plan: outputs/analysis/MOVEMENT_BOOTSTRAP_V10_TRAINING_PLAN.md
json: outputs/analysis/movement_bootstrap_v10_training_plan.json
starting checkpoint:
  policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320
```

The recipe keeps the fitted actuator envelope active in every phase:

```text
delay: 3-6 ticks
tau: 0.06-0.14 s
velocity limit: 2.5-3.75 rad/s
command_x: 0.04-0.08
zero_command_probability: 0.0
```

Two default-off Playground reward hooks were added for the V10 failure surfaces:

```text
forward_wrong_direction: penalizes reverse motion under positive command
forward_contact_support: penalizes no-contact support collapse, with only a
                         tiny one-sided-contact weight
Playground dependency: RobVanProd/Open_Duck_Playground
                       codex/forward-progress-reward @ f7b817d
```

A tiny CPU smoke run with these hooks passed, so the new config path is viable.
This was not candidate training and produced no deployable policy.

V10 must be judged against the established eight-seed V7/V9 baseline, not one
rollout:

```text
baseline to beat: 5/8 falls, 3/8 standstill completions, mean ~312 samples
target: fewer falls, fewer standstill seeds, later failures, useful forward
        tracking on more seeds
```

If V10 lands back at roughly the same distribution with the same four failure
surfaces, stop this V7/V9 anchor lineage and switch to a structurally different
bootstrap. Robot validation remains blocked.

## V10 Seed Sweep Result

V10 completed all three A100 staged-training phases, but it did not produce a
usable candidate. The final Phase 3 ONNX was:

```text
checkpoint: 2026_06_24_024457_153600
onnx_sha256: 54f5619c0a50f8064aa4b11e02b5a66125f0a27526ad83416e8d3e049e92254e
```

The eight-seed `x=0.08` fitted-bridge CPU gate is recorded in:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V10_SEED_SWEEP_SUMMARY.md
```

Result:

```text
V10: 8 seeds, 3 falls, 5 duration-complete low-progress holds,
     mean samples 482.75, mean track ratio -0.4610
```

This is not a deployable improvement. V10 reduced falls compared with V7/V9
mostly by freezing, and seed 5 still produced a strong reverse-motion failure.
The current V7/V9/V10 anchor lineage should no longer be the primary training
path. Next work should use a structurally different bootstrap/objective that
establishes one coherent forward behavior across seeds before strong stability
consolidation.

Robot validation remains blocked.

## V11 A100 Result

V11 was the first fresh hard-progress bootstrap after exiting the V7/V9/V10
anchor lineage. It trained successfully on Colab A100 with the known-good stack:

```text
jax/jaxlib: 0.7.2
brax: 0.14.2
mujoco/mujoco-mjx: 3.9.0
candidate: movement_bootstrap_v11_hard_progress_a100_20260624
onnx_sha256: a3f30d64f21334a5263df15d0b8c11576a04c4fe280c2a082cecb4e2038a13c7
summary: outputs/analysis/MOVEMENT_BOOTSTRAP_V11_A100_SUMMARY.md
```

Gate result:

```text
x=0.0:  PASS_CANDIDATE_SIM_GATE
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

At `x=0.08`, V11 survived the full 750-sample gate in vanilla, fitted, and
stress modes, but only by barely moving:

```text
track ratio: ~0.0107-0.0115
mean local vx: ~0.0009 m/s
max target velocity p95: 0.2749 rad/s
action saturation: 0%
max pitch tracking p95: 0.0734 rad
base height min: 0.1536 m
```

This is another stable no-motion solution, not a walking candidate. The hard
progress floor and reverse-motion penalties did not make forward locomotion the
cheapest solution. Robot validation remains blocked.

Next work should inspect the reward/episode mechanics instead of launching a
V12 blind recipe. In particular, determine why `x=0.08` standstill can still
survive the objective, then make low-progress command failure impossible to
score as a viable episode.

### V11 Reward Mechanics Audit

The first V11 postmortem is recorded in:

```text
outputs/analysis/V11_REWARD_MECHANICS_AUDIT.md
outputs/analysis/V11_FORWARD_REWARD_LANDSCAPE.md
```

The scalar reward-landscape check says the intended V11 phase scales should
prefer forward progress over zero velocity. The failure is therefore not well
explained by simply making `forward_shortfall_scale` larger again. The current
working diagnosis is that positive-command no-motion remains viable because the
task mechanics do not terminate or otherwise invalidate low-progress episodes,
and because the closed-loop gate reward-term table is not replaying the exact
V11 training reward override configuration.

Next change should be mechanics-first:

```text
1. use the default-off command-progress failure or truncation path after warmup
2. evaluate reward terms under the same config used for training
3. add a cheap per-phase freeze detector before later A100 phases
4. only then launch another candidate recipe
```

Do not deploy V11. Robot validation remains blocked.

## V12 Mechanics-Test Plan

V12 is prepared as a dry-run plan, not yet trained:

```text
recipe: movement_bootstrap_v12
plan: outputs/analysis/MOVEMENT_BOOTSTRAP_V12_TRAINING_PLAN.md
json: outputs/analysis/movement_bootstrap_v12_training_plan.json
training_started: false
robot_touched: false
```

V12 keeps the V11 fresh hard-progress structure but enables the default-off
command-progress failure hook in every phase. Persistent low progress under a
positive command should now terminate the episode instead of remaining a viable
standstill basin. The staged runner also has an opt-in per-phase freeze gate;
the V12 plan is generated with that gate enabled so a frozen phase can stop the
curriculum before later A100 phases consolidate it.

Next offline step is an A100 V12 run only after PR #74 and Playground PR #4 are
reviewed. Robot validation remains blocked.

### V12 A100 Phase-1 Gate Result

V12 was launched on an A100 from PR #74 head `79c0e21` with the corrected
per-phase gate. Phase 1 completed and exported an ONNX, but the gate stopped the
staged run before phase 2:

```text
status: HOLD_PHASE_FREEZE_OR_LOW_PROGRESS
candidate_gate_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
termination: duration_complete
forward_tracking_ratio: 0.04537
max_action_saturation_pct: 0.0
max_pitch_tracking_p95_rad: 0.07263
max_sent_target_velocity_p95_rad_s: 0.17286
```

Interpretation: V12 did not escape the stable low-motion basin. The policy stayed
upright and inside the actuator envelope, but it barely moved at `x=0.08`. The
corrected gate did its job by stopping the staged curriculum before later phases
consolidated the no-motion behavior. Robot validation remains blocked.

Summary artifact: `outputs/analysis/MOVEMENT_BOOTSTRAP_V12_A100_PHASE1_SUMMARY.md`.

## V13 Signed-Failure Mechanics Plan

The V12 phase-1 gate narrowed the current blocker to reward mechanics. Episode
termination for low command progress was not enough: the candidate stayed
upright, inside the actuator envelope, and nearly motionless at `x=0.08`.
Inspection of the Playground reward path showed the scalar reward is clipped at
zero by default, so a low-progress terminal event can still fail to become a
meaningful signed cost.

V13 is prepared as a dry-run plan:

```text
recipe: movement_bootstrap_v13
plan: outputs/analysis/MOVEMENT_BOOTSTRAP_V13_TRAINING_PLAN.md
json: outputs/analysis/movement_bootstrap_v13_training_plan.json
training_started: false
robot_touched: false
```

V13 keeps the V12 fitted-bridge curriculum but adds signed
command-progress-failure penalties and lowers `reward_clip_min` to `-10.0`:

```text
phase1 failure scale: -120.0
phase2 failure scale: -140.0
phase3 failure scale: -160.0
```

The per-phase gate remains enabled. If phase 1 freezes again, the staged run
should stop before spending later A100 phases consolidating no-motion behavior.
Robot validation and grounded replay remain blocked.

### V13 A100 Phase-1 Gate Result

V13 was launched on an A100 from PR #74 head `dff8d69`. Phase 1 completed and
exported an ONNX, but the per-phase gate stopped the staged run before phase 2:

```text
status: HOLD_PHASE_FREEZE_OR_LOW_PROGRESS
candidate_gate_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
termination: duration_complete
forward_tracking_ratio: 0.01601
mean local vx: 0.0013 m/s
max_action_saturation_pct: 0.0
max_pitch_tracking_p95_rad: 0.07430
max_sent_target_velocity_p95_rad_s: 0.14604
max_abs_body_pitch_p95_rad: 0.05504
min_base_height_m: 0.15368
```

Training rewards were negative through phase 1, confirming the signed
failure / negative reward path was active. The candidate still learned
near-standstill at `x=0.08`, so V13 did not escape the no-motion basin.

Current conclusion: the reward/termination plumbing now works well enough to
make low-progress training reward negative, but it still does not generate
coherent forward motion. The next offline task is to inspect command-progress
failure frequency and reward-term dominance during training before another A100
recipe is launched. Robot validation remains blocked.

Summary artifact: `outputs/analysis/MOVEMENT_BOOTSTRAP_V13_A100_PHASE1_SUMMARY.md`.

### V13 Training-Reward Replay

The closed-loop evaluator and staged-plan manifest were corrected to replay the
complete V13 phase reward contract while manually inserting the actuator bridge.
The initial replay path applied command-progress/posture terms but the
staged-plan JSON had omitted core fields such as `tracking_lin_vel_scale`,
`alive_scale`, and `target_rate_scale`, and it did not record the hardcoded
`tracking_ang_vel_scale=0.0` training flag. The manifest now carries the full
phase dataclass payload plus the reward-relevant hardcoded command settings.

With the complete V13 phase-1 reward settings applied, the phase-1 candidate
terminates at the configured 80-step low-progress boundary:

```text
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
samples: 80
termination: fall_or_nan
forward_tracking_ratio: 0.04657
mean local vx: 0.0037 m/s
diagnostic/command_progress_failure max: 1.0
cost/command_progress_failure max: 120.0
reward_mean: -0.38404
reward_min: -2.76543
```

This confirms V13's signed failure mechanism and negative terminal reward are
active. The remaining problem is not missing termination or missing reward
plumbing; PPO still learns a short-lived low-motion behavior that reaches the
failure boundary instead of discovering forward motion. Do not launch another
A100 recipe until the next change directly targets that local optimum.

Summary artifact: `outputs/analysis/V13_TRAINING_REWARD_REPLAY_SUMMARY.md`.

### V14 Motion-Discovery Ladder Plan

The next staged recipe is `movement_bootstrap_v14`. It is not another signed
penalty test. V13 already proved that signed command-progress failure and
negative reward are active, but the policy still learned a short-lived
low-motion behavior under the fitted bridge from step zero.

V14 changes the training question:

```text
phase 1: mild bridge, x=0.04-0.06, discover forward motion
phase 2: fitted bridge, x=0.04-0.06, transfer the discovered gait
phase 3: fitted bridge, x=0.04-0.08, expand only after phase-2 survives
```

The planner default is now V14 so an unqualified staged run does not repeat the
known-bad V13 path. Training is still manual/explicit; the generated plan is a
dry run unless launched with `--run` or through the Colab workflow.

Plan artifact: `outputs/analysis/MOVEMENT_BOOTSTRAP_V14_TRAINING_PLAN.md`.

### V14 A100 Phase-1 Partial

V14 phase 1 was launched on an A100 as an offline phase-1-only run. The run
reached a step-102400 checkpoint/export, then the detached Colab process
disappeared without writing the workflow exit sentinel or artifact bundle.
Partial stdout/stderr and the step-102400 ONNX were recovered manually.

The recovered checkpoint is not useful as a motion anchor:

```text
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
samples: 120
termination: fall_or_nan
mean local vx: 0.0014 m/s
forward_tracking_ratio: 0.0181
reward_mean: -0.1850
max_sent_target_velocity_p95_rad_s: 0.2466
diagnostic/command_progress_failure max: 1.0
```

This is a partial result, not a complete V14 phase-1 verdict. It does show that
the available step-102400 checkpoint is still in the low-motion basin. Do not
use it on the robot or as a restore anchor.

Summary artifact:
`outputs/analysis/MOVEMENT_BOOTSTRAP_V14_A100_PHASE1_PARTIAL_SUMMARY.md`.

### V15 No-Bridge Gait-Discovery Plan

The current default staged recipe is now `movement_bootstrap_v15`.

V14's partial A100 checkpoint showed that even a mild actuator bridge can still
leave fresh PPO in the low-motion basin. V15 makes a more structural split:

```text
phase 1: no actuator bridge, no alive/imitation crutch, higher entropy,
         x=0.06-0.10, gate under vanilla sim
phase 2: mild bridge transfer, x=0.05-0.08, gate under fitted bridge
phase 3: fitted bridge consolidation, x=0.04-0.08, gate under fitted bridge
```

The planner now supports per-phase gate bridge modes so discovery is judged in
the environment it trained in, while transfer/consolidation are still judged
against the measured fitted actuator envelope.

This is still an offline-only training plan. Robot validation remains blocked
until a final candidate passes the `x=0.0` and `x=0.08` sim gates.

Plan artifact: `outputs/analysis/MOVEMENT_BOOTSTRAP_V15_TRAINING_PLAN.md`.

### V15 A100 No-Sentinel Export Handoff

The first V15 A100 phase-1 launch did not produce a candidate result. It reached
only `STEP: 0`, saved/exported a step-0 ONNX, then the detached Colab workflow
disappeared without writing the `.exit` sentinel or artifact bundle.

Recovered evidence shows the log stops immediately after TensorFlow ONNX export:

```text
status: HOLD_REMOTE_NO_SENTINEL_EXPORT_HANDOFF
step: 0 only
later checkpoints: none
python traceback: none
```

This is infrastructure evidence, not a V15 policy verdict. The follow-up fix is
to keep TensorFlow ONNX export CPU-only by default and skip only the step-0
export in staged training (`--export-min-step 1`), while preserving later
candidate exports.

Summary artifact:
`outputs/analysis/MOVEMENT_BOOTSTRAP_V15_A100_NO_SENTINEL_SUMMARY.md`.

### V15B A100 Post-Step0 Hold

After the export-handoff fix, V15 phase 1 was relaunched as `open-duck-a100-v15b`.
The run confirmed the new export guard was active:

```text
STEP: 0 reward: -191.49404907226562 reward_std: 169.26931762695312
Skipping checkpoint/export at step 0; export_min_step=1
```

It still disappeared afterward without writing a workflow exit sentinel or
artifact bundle. No ONNX/checkpoint beyond the start manifest was produced.

This means the step-0 ONNX export was not the full cause. The current hold is
now the A100/JAX training path after the initial eval callback, with no Python
traceback. Treat this as an offline training-infrastructure issue. The next
reasonable check is a smaller A100 smoke/phase-1 run with reduced env and batch
size before spending another full phase.

Summary artifact:
`outputs/analysis/MOVEMENT_BOOTSTRAP_V15B_A100_NO_SENTINEL_SUMMARY.md`.

### V15C A100 Reduced PPO Hold

V15 phase 1 was relaunched again as `open-duck-a100-v15c` with a reduced PPO
configuration:

```text
timesteps_scale: 0.25
ppo_num_envs: 64
ppo_batch_size: 64
ppo_num_minibatches: 2
ppo_num_updates_per_batch: 2
export_min_step: 1
```

The remote Colab session became idle without a workflow exit sentinel, final
manifest, artifact bundle, ONNX, or checkpoint. The captured log reached the
reduced runner command but did not show a `STEP: 0` reward line. The stale local
poller and remote session were stopped manually after the session reported
`IDLE`.

This broadens the current hold: the A100/Colab/JAX training path is failing even
for a reduced V15 phase-1 smoke. Treat this as cloud training infrastructure,
not a V15 policy-quality result. Do not spend another full A100 recipe run until
a tiny training smoke can produce a normal sentinel/final manifest.

The workflow now has a smaller `training-smoke` mode intended for that exact
infrastructure check. It runs only the tiny PPO smoke path, skips the policy
contract audit/baseline eval, and defaults to skipping step-0 ONNX export so the
test isolates training process survival and final-manifest behavior.

Summary artifact:
`outputs/analysis/MOVEMENT_BOOTSTRAP_V15C_A100_REDUCED_NO_SENTINEL_SUMMARY.md`.

### Minimal A100 Training Smoke Hold

The new `training-smoke` workflow was run on a fresh A100 session:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-a100-smoke \
  --workflow training-smoke \
  --run \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

The pinned stack initialized correctly (`jax/jaxlib 0.7.2`, GPU visible,
`device_put_replicated` present), then the tiny PPO smoke disappeared without a
workflow exit sentinel, final manifest, artifact bundle, ONNX, or checkpoint.
The hardened poller detected `HOLD_REMOTE_NO_SENTINEL` with Colab reporting
`IDLE`.

This isolates the current cloud hold below the recipe level. The issue is now
in or immediately after the minimal A100 GPU PPO training path, not in V15,
step-0 export, large PPO batch sizing, contract audit, or baseline eval. Do not
spend more A100 time on curriculum recipes until a minimal training smoke can
exit normally.

Summary artifact:
`outputs/analysis/A100_TRAINING_SMOKE_NO_SENTINEL_SUMMARY.md`.

### Minimal L4 Training Smoke Hold

The same `training-smoke` workflow was run on a fresh L4 Colab session. The
pinned stack again initialized correctly (`jax/jaxlib 0.7.2`, GPU visible,
`device_put_replicated` present), then the tiny PPO smoke disappeared without a
workflow exit sentinel, final manifest, artifact bundle, ONNX, or checkpoint.
The hardened poller recorded `HOLD_REMOTE_NO_SENTINEL`.

This means the cloud training-smoke failure is not A100-specific. The current
debugging target is now the Colab remote execution/capture path or a generic GPU
PPO smoke failure. The next infrastructure fix should support foreground remote
execution for tiny smokes so the console captures the driver exit status
directly instead of relying on a detached `setsid` job.

That foreground mode is now the next offline check before any more staged
curriculum runs.

Summary artifact:
`outputs/analysis/L4_TRAINING_SMOKE_NO_SENTINEL_SUMMARY.md`.

### L4 Foreground Training Smoke Hold

The L4 `training-smoke` was repeated with `--foreground-remote` so the remote
driver ran directly inside `colab console` rather than through a detached
`setsid` shell. It still reached the tiny PPO smoke command, then the session
became idle without writing the foreground exit sentinel or artifact bundle.

This rules out the detached wrapper as the sole cause. The current split is now
between a Colab GPU PPO/Brax runtime/session failure and a runner-level failure
that Colab drops before stdout/stderr can be packaged. Next check is the same
tiny smoke locally on CPU.

Summary artifact:
`outputs/analysis/L4_FOREGROUND_TRAINING_SMOKE_NO_SENTINEL_SUMMARY.md`.

### Local CPU Training Smoke Pass

The same tiny PPO smoke was run locally on CPU. The first local attempt exposed
a platform-selection bug: `JAX_PLATFORM_NAME=cpu` was not enough because JAX
still tried to initialize the installed ROCm plugin and failed with
`No visible GPU devices`. The smoke launcher now sets both `JAX_PLATFORM_NAME`
and `JAX_PLATFORMS`.

After that fix, local CPU passed:

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 54.36
STEP: 80 reward: 11.251152038574219 reward_std: 4.502880573272705
```

This proves the runner itself is valid outside Colab. The next cloud check is
to rerun the minimal GPU smoke with the patched launcher so the remote runtime
also has explicit `JAX_PLATFORMS=gpu`.

Summary artifact:
`outputs/analysis/LOCAL_CPU_TRAINING_SMOKE_SUMMARY.md`.

### L4 Platform Mapping Hold

The next foreground L4 smoke recovered a real exit code and stdout/stderr. It
failed because the first platform fix mapped logical `gpu` to
`JAX_PLATFORMS=gpu`, which is not valid for CUDA JAX:

```text
Backend 'rocm' is not in the list of known backends: ['cpu', 'tpu', 'cuda'].
```

The launcher now has an explicit `--jax-platforms` override. CPU runs default
to `cpu`; GPU runs leave it unset unless specified; the Colab CUDA workflow now
passes `cuda`; and staged phases pass that through to their smoke commands. The
remote artifact bundler was also fixed to recreate `OUT` after repo extraction
so failed runs can package logs.

Next check is foreground L4 `training-smoke` with `JAX_PLATFORMS=cuda`.

Summary artifact:
`outputs/analysis/L4_PLATFORMFIX_TRAINING_SMOKE_SUMMARY.md`.

### L4 CUDA Training Smoke Hold

The foreground L4 smoke was rerun with the corrected CUDA selector:

```text
JAX_PLATFORM_NAME=gpu
JAX_PLATFORMS=cuda
```

The pinned stack initialized and JAX saw `CudaDevice(id=0)`. The run reached the
tiny PPO smoke command, then Colab reported `IDLE` without a workflow exit
sentinel, artifact bundle, smoke stdout/stderr, start manifest, final manifest,
ONNX, or checkpoint. Direct download of the expected smoke output paths failed
because the smoke output directory had not been created.

This leaves a clean matrix:

```text
local CPU training-smoke: PASS
Colab A100 training-smoke: HOLD_REMOTE_NO_SENTINEL
Colab L4 training-smoke: HOLD_REMOTE_NO_SENTINEL
Colab L4 foreground + cuda selector: HOLD_REMOTE_NO_SENTINEL before smoke output dir
```

Interpretation: the Open Duck runner works, but Colab GPU training is currently
not reliable enough for recipe iteration. Keep the robot parked and continue on
a stable backend while treating Colab GPU as a separate runtime issue.

Summary artifact:
`outputs/analysis/L4_CUDA_TRAINING_SMOKE_NO_SENTINEL_SUMMARY.md`.

### Local CPU Candidate Gate Platform Fix

The V15 local CPU smoke produced a tiny phase-1 ONNX, but its first candidate
gate originally failed before evaluation because the closed-loop evaluator only
set `JAX_PLATFORM_NAME=cpu`; JAX still probed the installed ROCm plugin. The
evaluator now also constrains `JAX_PLATFORMS=cpu` when `--jax-platform cpu` is
requested, and staged phase gates can pass an explicit `--phase-gate-jax-platforms`.

Rerunning the existing V15 smoke checkpoint gate completed on CPU:

```text
jax: cpu ['TFRT_CPU_0']
overall_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
mean_local_vx: -0.0083 m/s
track_ratio: -0.1033
worker_returncode: 0
```

Interpretation: local CPU gate plumbing is now usable. The tiny 320-step V15
smoke candidate is still only a plumbing artifact and is not a robot candidate.

Summary artifact:
`outputs/analysis/LOCAL_V15_CPU_GATE_AFTER_JAX_PLATFORMS_FIX_SUMMARY.md`.

### Colab GPU Startup Diagnostic Added

The next Colab step should use the new startup diagnostic workflow instead of
rerunning a full staged recipe:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow training-smoke-diagnostic \
  --run \
  --foreground-remote \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

It records staged evidence for CUDA/JAX device compute, training-stack imports,
smoke dry-run startup, and the tiny PPO smoke. This should narrow the current
`HOLD_REMOTE_NO_SENTINEL` to a concrete startup stage before more cloud GPU
training time is spent.

Local CPU validation of the diagnostic passed all stages, including the actual
tiny PPO smoke. The Colab poller now also tries to recover the remote workflow
output directory as `partial_remote_output` before declaring
`HOLD_REMOTE_NO_SENTINEL` or `HOLD_REMOTE_TIMEOUT`.

Summary artifact:
`outputs/analysis/LOCAL_TRAINING_SMOKE_STARTUP_DIAGNOSTIC_SUMMARY.md`.

Runbook:
`docs/CLOUD_GPU_TRAINING_DEBUG.md`.

### L4 Minimal CUDA Training Smoke Pass

The Colab L4 session completed the smallest real CUDA PPO smoke after the
startup diagnostic was reduced to one environment and eight timesteps:

```text
00_python_jax_device: PASS
01_import_training_stack: PASS
02_smoke_dry_run: PASS
03_smoke_run: PASS
JAX_PLATFORM_NAME=gpu
JAX_PLATFORMS=cuda
status: PASS_SMOKE_RUN
elapsed_s: 361.21
STEP: 10 reward: 7.2996506690979 reward_std: 2.555509090423584
checkpoint: saved at step 10
```

This means Colab L4 CUDA/JAX/Brax/Playground is not globally broken. The
remaining cloud hold is scale-sensitive or long-compile/runtime related: the
larger 8-env / 64-timestep diagnostic disappeared without a final manifest,
while the 1-env / 8-timestep diagnostic completed.

The Colab workflow recovery path now falls back to tarring the remote output
directory before downloading it, because `google-colab-cli` cannot download
directories directly.

Summary artifact:
`outputs/analysis/L4_MINIMAL_CUDA_TRAINING_SMOKE_SUMMARY.md`.

### L4 1-Env / 16-Step CUDA Training Smoke Pass

The next Colab L4 scale point used one environment and sixteen timesteps. After
the Colab helper stopped treating unchanged logs alone as a lost-sentinel
condition, this scale passed:

```text
00_python_jax_device: PASS
01_import_training_stack: PASS
02_smoke_dry_run: PASS
03_smoke_run: PASS
num_timesteps: 16
num_envs: 1
batch_size: 1
status: PASS_SMOKE_RUN
elapsed_s: 423.93
STEP: 20 reward: 7.24683952331543 reward_std: 2.536440372467041
checkpoint: saved at step 20
```

The Colab workflow now exposes `--idle-no-sentinel-polls` so long/no-output GPU
compile windows can be given more slack before the helper declares a lost
sentinel.

Summary artifact:
`outputs/analysis/L4_1ENV16_CUDA_TRAINING_SMOKE_SUMMARY.md`.

### L4 2-Env / 16-Step CUDA Training Smoke Pass

The Colab L4 scale sweep also passed two environments and sixteen timesteps:

```text
00_python_jax_device: PASS
01_import_training_stack: PASS
02_smoke_dry_run: PASS
03_smoke_run: PASS
num_timesteps: 16
num_envs: 2
batch_size: 2
status: PASS_SMOKE_RUN
elapsed_s: 445.78
STEP: 20 reward: 8.948163986206055 reward_std: 3.5841026306152344
checkpoint: saved at step 20
```

This means the Colab L4 CUDA training path is now verified beyond the absolute
minimum smoke. The next scale point is 4 env / 32 timesteps.

Summary artifact:
`outputs/analysis/L4_2ENV16_CUDA_TRAINING_SMOKE_SUMMARY.md`.

### L4 4-Env / 32-Step CUDA Training Smoke Pass

The Colab L4 scale sweep also passed four environments and thirty-two
timesteps:

```text
00_python_jax_device: PASS
01_import_training_stack: PASS
02_smoke_dry_run: PASS
03_smoke_run: PASS
num_timesteps: 32
num_envs: 4
batch_size: 4
status: PASS_SMOKE_RUN
elapsed_s: 437.48
STEP: 40 reward: 11.187263488769531 reward_std: 4.4381818771362305
checkpoint: saved at step 40
```

The original 8-env / 64-step hold should be rerun with the corrected quiet
compile polling before treating it as a real scale limit.

Summary artifact:
`outputs/analysis/L4_4ENV32_CUDA_TRAINING_SMOKE_SUMMARY.md`.

### L4 8-Env / 64-Step CUDA Training Smoke Hold

The original 8-env / 64-step Colab L4 smoke was rerun after the quiet-compile
poller fix:

```text
jax: 0.7.2
jaxlib: 0.7.2
brax: 0.14.2
mujoco: 3.9.0
mujoco-mjx: 3.9.0
playground: 0.0.5
backend: gpu [CudaDevice(id=0)]
smoke-num-timesteps: 64
ppo-num-envs: 8
ppo-batch-size: 8
```

The run reached the actual smoke command, then ended with:

```text
status: HOLD_REMOTE_NO_SENTINEL
idle_no_exit_polls: 18
idle_no_sentinel_polls_limit: 18
workflow exit sentinel: MISSING
artifact bundle: MISSING
local_partial_output_dir: None
```

Read-only side inspection found the expected remote diagnostic/output directory
and exit/artifact files were missing. Current L4 CUDA smoke capacity is therefore
verified through 4 env / 32 timesteps, with 8 env / 64 timesteps still held by
Colab runtime/session loss.

Summary artifact:
`outputs/analysis/L4_8ENV64_CUDA_TRAINING_SMOKE_HOLD_SUMMARY.md`.

### A100 8-Env / 64-Step CUDA Training Smoke Pass

The same 8-env / 64-step smoke that held on L4 completed on A100:

```text
00_python_jax_device: PASS
01_import_training_stack: PASS
02_smoke_dry_run: PASS
03_smoke_run: PASS
num_timesteps: 64
num_envs: 8
batch_size: 8
status: PASS_SMOKE_RUN
elapsed_s: 362.05
STEP: 80 reward: 11.273723602294922 reward_std: 4.483529567718506
checkpoint: saved at step 80
GPU: NVIDIA A100-SXM4-40GB
```

Interpretation: A100 is the better cloud backend for the next substantial
candidate training run. The L4 hold at the same scale is likely a Colab L4
runtime/session capacity issue, not a generic Open Duck training failure.

Summary artifact:
`outputs/analysis/A100_8ENV64_CUDA_TRAINING_SMOKE_SUMMARY.md`.

### A100 V15 Phase-1 Result

After the A100 smoke pass, `movement_bootstrap_v15` phase 1 was run as the next
offline candidate-training gate:

```text
phase: phase1_no_bridge_high_entropy_gait_discovery
num_timesteps: 320000
ppo_num_envs: 256
actuator bridge: disabled
command x range: 0.06 to 0.10
zero_command_probability: 0
```

Training completed and exported a checkpoint/ONNX at step `337920`, but the
automatic vanilla `x=0.08` candidate gate returned:

```text
overall_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
mean_local_vx: 0.0009 m/s
track_ratio: 0.0111
max_sent_target_velocity_p95_rad_s: 0.0988
max_pitch_tracking_p95_rad: 0.0540
max_action_saturation_pct: 0.0000
body_pitch_p95: 0.0818 rad
base_height_min: 0.1534 m
```

Interpretation: A100 is now validated for substantial phase execution, but V15
phase 1 still falls into the standstill basin. The checkpoint is not suitable
for V15 phase 2/3 transfer or robot validation.

An eight-seed local CPU sweep of the recovered V15 phase-1 ONNX confirmed that
the seed-0 gate was not a fluke:

```text
seeds: 0-7
bridge_mode: vanilla
duration: 5 s
falls: 3 / 8
duration_complete low-progress runs: 5 / 8
track_ratio_mean: -0.7433
vx_mean: -0.0595 m/s
samples_mean: 170.125
```

Interpretation: V15 phase 1 is a freeze/reverse/collapse distribution, not a
useful gait-discovery anchor.

The run exposed an artifact hygiene bug: staged phase outputs were not copied
into the exit bundle when the phase gate raised `HOLD_PHASE_FREEZE_OR_LOW_PROGRESS`.
The Colab workflow now copies staged smoke outputs and phase-gate summaries
during `atexit` bundling, including failure exits.

Summary artifact:
`outputs/analysis/A100_V15_PHASE1_HOLD_SUMMARY.md`.

Seed sweep artifact:
`outputs/analysis/V15_PHASE1_SEED_SWEEP_VALID.md`.

### V5 vs V15 Same-Gate Comparison

A four-seed local CPU sweep compared the older V5 recovery checkpoint against
the recovered V15 phase-1 policy under the same vanilla `x=0.08`, 5-second gate:

```text
V5 recovery:
  falls: 2 / 4
  duration_complete: 2 / 4
  track_ratio_mean: 0.6045
  vx_mean: 0.0484 m/s
  body_pitch_p95_mean: 0.4744 rad

V15 phase 1:
  falls: 1 / 4
  duration_complete: 3 / 4
  track_ratio_mean: -0.3265
  vx_mean: -0.0261 m/s
  body_pitch_p95_mean: 0.0534 rad
```

Interpretation: V15 looks calmer because it mostly freezes or drifts backward.
V5 remains the more useful movement anchor despite instability, because it at
least produces forward-motion seeds. The next recipe should not continue V15
phases 2/3; it should either return to the moving-anchor family with better
stabilization or introduce a structurally different movement prior.

Comparison artifact:
`outputs/analysis/V5_VS_V15_SEED_SWEEP.md`.

### Multi-Seed Staged Phase Gates

The staged curriculum gate now supports distribution checks through
`tools/run_candidate_seed_sweep.py`. The Colab staged workflow defaults to a
four-seed phase gate:

```text
staged_phase_gate_seeds: 0-3
max_fall_fraction: 0.0
min_track_ratio_mean: 0.25
min_vx_mean: 0.02 m/s
```

This replaces the old default where a single rollout could promote or reject a
phase. The change is based on the V9/V10/V15 evidence: short or single-seed
rollouts made unstable/frozen candidates look better than they were, while
multi-seed sweeps exposed freeze, reverse, collapse, and lunge regimes.

Single-rollout gates remain available by passing an empty seed list, but future
substantial A100 staged runs should use the multi-seed gate unless there is a
specific reason to run a cheap exploratory check.

### Movement Bootstrap V16 Plan

V16 is the next offline recipe and is now the staged-curriculum default, but it
is not a fresh PPO discovery run. It must restore the recovered V5 trainable
checkpoint:

```text
policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/checkpoint_2026_06_23_205634_368640
```

Reasoning:

```text
V15 fresh/no-bridge discovery: stable but mostly standstill/reverse/collapse
V5 recovery: unstable, but still the only preserved anchor with forward-motion seeds
```

V16 phases:

```text
1. mild-bridge consistency repair from V5
2. fitted-bridge consistency transfer
3. fitted-bridge low-step margin consolidation
```

The intended A100 launch must keep the multi-seed phase gate enabled. A phase
only promotes if its seed distribution has no falls and maintains positive
forward tracking. Robot validation remains blocked.

### A100 V16 Phase-1 No-Sentinel Hold

The first V16 phase-1 A100 launch restored the V5 trainable checkpoint and
reached PPO startup, but did not produce a final manifest, ONNX, exit sentinel,
or artifact bundle.

Confirmed partial output:

```text
Observation size: 101
STEP: 0 reward: -52.476234436035156 reward_std: 93.70592498779297
Skipping checkpoint/export at step 0; export_min_step=1
```

Interpretation: this is an A100/Colab workflow hold, not a V16 recipe verdict.
The session state became ambiguous, so the A100 session was terminated to avoid
overlapping orphaned jobs. No robot work was performed.

Summary artifact:
`outputs/analysis/A100_V16_PHASE1_NO_SENTINEL_SUMMARY.md`.

Follow-up workflow fix: foreground Colab jobs now write a remote PID file, and
the poller checks that PID before treating an idle/no-sentinel session as lost.
This prevents starting a second job over a still-running raw-console process.

### A100 V16 Tiny Restore Hold And Local CPU Restore Pass

A tiny V16 restored run was launched to separate workload size from restore-path
issues:

```text
ppo_num_envs: 4
num_timesteps: 120
phase_gate: disabled
restore: V5 trainable checkpoint
```

It reproduced the same post-step-0 stall/no-sentinel pattern:

```text
Observation size: 101
PPO params: {... num_envs: 4, num_timesteps: 120 ...}
Skipping checkpoint/export at step 0; export_min_step=1
```

Follow-up: the planner now resolves `--initial-restore-checkpoint` to an
absolute path before handing it to the Playground runner. With that fix, the
same tiny restored V16 phase-1 path passes locally on CPU:

```text
status: PASS_STAGED_CURRICULUM_RUN
platform: cpu
num_timesteps: 120
checkpoint: /tmp/open_duck_v16_tiny_cpu_fixed/01_phase1_v5_anchor_mild_bridge_consistency/smoke_20260624T113100Z_cpu/2026_06_24_073135_120
onnx: /tmp/open_duck_v16_tiny_cpu_fixed/01_phase1_v5_anchor_mild_bridge_consistency/smoke_20260624T113100Z_cpu/2026_06_24_073135_120.onnx
```

Interpretation: V16's restored-checkpoint recipe path is not currently the
primary blocker. The remaining hold is A100/Colab/CUDA workflow behavior or
remote session state. Before a full V16 relaunch, run one tiny A100 restored
smoke with the PID-aware poller and timeout-safe PID probe.

Summary artifact:
`outputs/analysis/A100_V16_TINY_RESTORE_HOLD_SUMMARY.md`.

### A100 V16 Tiny Restore Pass / Toy Gate Hold

After the timeout-safe PID probe and absolute restore-path fix, a fresh A100
session reran the tiny restored V16 phase-1 smoke:

```text
recipe: movement_bootstrap_v16
restore: V5 trainable checkpoint
num_timesteps: 120
ppo_num_envs: 4
phase_gate: disabled
```

Result:

```text
training_manifest: PASS_SMOKE_RUN
platform: gpu
candidate_sha256: c81a9fe92bf726725273ce87389a4edd7aff012a59b09fbbf00a4de0dc42b5a9
x=0.0 gate: HOLD_CANDIDATE_FALL_OR_TERMINATION
x=0.08 gate: HOLD_CANDIDATE_FALL_OR_TERMINATION
```

Interpretation: the A100 workflow can now restore, train past step 0, export
ONNX, run sim gates, and download final artifacts. The 120-step candidate is a
toy smoke artifact and is not a policy result. The next offline action is a full
V16 phase-1 A100 run with the multi-seed phase gate enabled.

Summary artifact:
`outputs/analysis/A100_V16_TINY_RESTORE_PASS_GATE_HOLD_SUMMARY.md`.

### A100 V16 Full Phase-1 Seed-Gate Stall

A full V16 phase-1 A100 run was launched after the tiny smoke cleared:

```text
phase_1_timesteps: 120000
restore: V5 trainable checkpoint
phase_gate_seeds: 0-3
phase_gate_command_x: 0.08
phase_gate_bridge: vanilla
```

The remote log shows phase-1 training completed and the workflow entered the
multi-seed gate using the exported phase-1 candidate:

```text
/content/open_duck_staged_curriculum_cli/01_phase1_v5_anchor_mild_bridge_consistency/smoke_20260624T120332Z_gpu/2026_06_24_121150_122880.onnx
```

The seed gate did not emit a result before the Colab session was lost. No final
artifact bundle or seed-gate result was downloaded, so this is not a policy
verdict.

Follow-up tooling patch: `tools/run_candidate_seed_sweep.py` now prints
per-seed start/done markers, kills the full subprocess group on timeout, records
`HOLD_SEED_TIMEOUT`, and writes a partial JSON file after every seed.

Summary artifact:
`outputs/analysis/A100_V16_PHASE1_SEED_GATE_STALL_SUMMARY.md`.

### A100 V16 Phase-1 Multi-Seed Hold

After hardening the seed-sweep gate, V16 phase 1 was rerun on A100. Training
completed and exported ONNX checkpoints at steps `40960`, `81920`, and
`122880`, but the phase gate held:

```text
status: HOLD_PHASE_MULTI_SEED_FALLS
gate: x=0.08, vanilla bridge, seeds 0-3, 5 seconds
runs: 4
falls: 1
duration_complete: 3
track_ratio_mean: -0.1269
mean_local_vx_mean: -0.0102 m/s
```

Per-seed result:

```text
seed 0: low progress, duration complete, track_ratio  0.0748
seed 1: fall at 35 samples, reverse vx, track_ratio -0.6297
seed 2: low progress, duration complete, track_ratio  0.0898
seed 3: low/reverse progress, duration complete, track_ratio -0.0426
```

Interpretation: V16 fixed the infrastructure path but not the behavior. The
V5-anchored mild-bridge continuation still collapses into low/reverse progress
across seeds and is not deployable.

Next offline check: sweep the intermediate V16 ONNX exports at `40960` and
`81920`. If no intermediate checkpoint has a better forward-progress
distribution, stop extending the V5-anchor continuation.

Summary artifact:
`outputs/analysis/A100_V16_PHASE1_MULTI_SEED_HOLD_SUMMARY.md`.

Intermediate checkpoint follow-up:

```text
40960:  falls 1/4, track_ratio_mean -0.0508, vx_mean -0.0041 m/s
81920:  falls 1/4, track_ratio_mean -0.1072, vx_mean -0.0086 m/s
122880: falls 1/4, track_ratio_mean -0.1269, vx_mean -0.0102 m/s
```

Conclusion: the V16 failure is present throughout phase 1. There is no better
intermediate V16 checkpoint to branch from. The next recipe should be a
structural break from the V5-anchor continuation, with hard signed positive
progress from the start.

Planned next recipe: `movement_bootstrap_v17`.

```text
phase 1: no bridge, x=0.04-0.06, hard signed positive progress
phase 2: mild bridge transfer
phase 3: fitted bridge low-command transfer
```

V17 intentionally does not restore from V5. It tests whether a fresh hard-progress
lineage can escape the V5/V16 low-reverse-progress basin.

### A100 V17 Phase-1 Multi-Seed Hold

V17 phase 1 was run on A100 as a structural break from the V5/V16 anchored
continuation:

```text
recipe: movement_bootstrap_v17
restore: none
phase 1: no bridge, x=0.04-0.06, hard signed positive progress
gate: x=0.08, vanilla bridge, seeds 0-3, 5 seconds
```

Training completed and exported ONNX checkpoints at `92160`, `184320`, and
`276480`, but the multi-seed phase gate held:

```text
status: HOLD_PHASE_MULTI_SEED_FALLS
runs: 4
falls: 1
duration_complete: 3
track_ratio_mean: -0.2876
mean_local_vx_mean: -0.0230 m/s
```

Per-seed result:

```text
seed 0: low progress, duration complete, track_ratio  0.0358
seed 1: fall at 33 samples, reverse vx, track_ratio -1.2270
seed 2: low progress, duration complete, track_ratio  0.0560
seed 3: low/reverse progress, duration complete, track_ratio -0.0152
```

Interpretation: V17 escaped the V5 restore dependency but not the low/reverse
progress basin. Hard signed-progress shaping without a bridge in phase 1 still
failed to produce coherent positive forward locomotion across seeds.

Next offline work should inspect V17 phase-1 reward components and sign
conventions before launching another large recipe. In particular, verify why
the reward still permits near-zero or negative local forward velocity despite
the command-progress failure term.

Summary artifact:
`outputs/analysis/A100_V17_PHASE1_MULTI_SEED_HOLD_SUMMARY.md`.

### V17 Phase-1 Reward Override Audit

V17 phase 1 was replayed locally on CPU with the exact
`phase1_hard_signed_progress_discovery` reward overrides from the staged
curriculum plan:

```text
gate: x=0.08, vanilla bridge, seeds 0-3, 5 seconds
runs: 4
falls_or_terminations: 4
duration_complete: 0
track_ratio_mean: -0.2367
mean_local_vx_mean: -0.0189 m/s
```

Per-seed result:

```text
seed 0: terminates at sample 60, command-progress failure boundary
seed 1: reverse/collapse at sample 32 before command-progress failure
seed 2: terminates at sample 60, command-progress failure boundary
seed 3: terminates at sample 60, command-progress failure boundary
```

Interpretation: the reward overrides are active. V17 did not fail because it
was evaluated under the wrong phase reward config. Seeds `0`, `2`, and `3` are
stable enough to reach the progress-gate warmup boundary but fail sustained
command progress; seed `1` reverses and collapses before that gate can act.

Conclusion: do not run V17 phase 2. The next work remains offline reward/sign
auditing: verify the local-forward sign convention in the reward source and
inspect whether the delayed command-progress terminal failure is too sparse for
PPO to escape low/reverse progress.

Summary artifact:
`outputs/analysis/V17_PHASE1_REWARD_OVERRIDE_AUDIT_SUMMARY.md`.

### V17 Reward Sign And Low-Command Audit

The reward source and evaluator were inspected for a local-forward sign
mismatch. No sign mismatch was found:

```text
command-window progress: local_vx * sign(command_x)
forward progress reward: local_vel[0] * sign(command_x)
forward shortfall cost: local_vel[0] * sign(command_x)
wrong-direction cost: local_vel[0] * sign(command_x)
candidate evaluator: get_local_linvel(data)[0] / command_x
```

The command-progress failure is active but delayed and one-tick. In V17 phase 1
it fires after `60` steps if cumulative progress ratio is below `0.40`; the
`-260` scale is multiplied by `dt=0.02`, so the terminating tick contributes
about `-5.2` reward before clipping.

The same reward-overridden seed sweep was run at `x=0.04`, the low end of V17's
training command range:

```text
runs: 4
falls_or_terminations: 4
duration_complete: 0
track_ratio_mean: -0.6911
mean_local_vx_mean: -0.0276 m/s
```

Conclusion: V17 did not just fail an over-hard `x=0.08` phase gate. It failed to
learn coherent forward motion even at the easiest command it trained on, under
the intended reward config and a consistent local-forward sign convention.

Next offline target: a simpler low-command discovery recipe, graded at the same
low command it trains on, before adding bridge transfer or `x=0.08` again.

Summary artifacts:

```text
outputs/analysis/V17_REWARD_SIGN_AND_LOW_COMMAND_AUDIT.md
outputs/analysis/V17_PHASE1_REWARD_OVERRIDE_SEED_SWEEP_X004.md
```

### V18 Low-Command Discovery Recipe

The next offline recipe is `movement_bootstrap_v18`. It is a direct response to
the V17 low-command audit:

```text
phase 1: x=0.035-0.045, no bridge, no restore
phase gate: x=0.04, vanilla bridge, multi-seed
goal: prove any coherent low-command forward motion before x=0.08
```

V18 intentionally does not restore from V5/V7/V9/V17 and does not begin with
the actuator bridge. It tests only the discovery question that V17 failed:
whether dense per-step signed progress and immediate wrong-direction pressure
can produce low-command forward motion at the same command used for training.

Do not interpret V18 at `x=0.08` until it first passes `x=0.04` across seeds.
Robot validation remains blocked.

Plan artifacts:

```text
outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V18.md
outputs/analysis/staged_curriculum_training_plan_v18.json
```

### V18 A100 Phase-1 Result

V18 phase 1 was run on the A100 as a low-command discovery test. It trained only
phase 1 and gated the exported policy at the same command range it trained on:

```text
recipe: movement_bootstrap_v18
gate command: x=0.04
bridge: vanilla
seeds: 0-3
duration: 5 s
```

Gate result:

```text
HOLD_PHASE_MULTI_SEED_FALLS
```

Per-seed outcome:

```text
seed 0: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, vx 0.0007 m/s, track ratio 0.0165
seed 1: HOLD_CANDIDATE_FALL_OR_TERMINATION, vx -0.0977 m/s, track ratio -2.4426
seed 2: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, vx 0.0023 m/s, track ratio 0.0575
seed 3: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, vx -0.0047 m/s, track ratio -0.1171
```

Distribution:

```text
runs: 4
falls: 1
duration_complete: 3
track_ratio_mean: -0.6214
vx_mean: -0.0249 m/s
```

Conclusion: V18 did not discover coherent forward locomotion even at `x=0.04`
with the actuator bridge disabled. Do not run V18 phase 2, do not test V18 at
`x=0.08`, and do not move to robot validation. The next work is offline
objective/task diagnosis: why the policy still prefers low/reverse progress
despite dense signed progress and wrong-direction pressure.

Reward-diagnostic caveat: the A100 seed-gate command for this run did not pass
the V18 phase reward overrides into the evaluator, so raw per-term reward
diagnostics in the seed artifacts reflect default eval rewards. The hold remains
valid because it is based on independent velocity/progress/fall metrics.
Future phase gates should pass phase-local reward overrides before using reward
term summaries diagnostically.

A corrected CPU replay was then run for V18 phase 1 with the intended reward
overrides active for seeds `0-1` at `x=0.04`. Both seeds terminated:

```text
seed 0: 50 samples, vx 0.0034 m/s, track ratio 0.0845, command-progress failure
seed 1: 33 samples, vx -0.0954 m/s, track ratio -2.3845, reverse/collapse
```

This strengthens the V18 hold. The reward terms are active, but the learned
policy still fails low-command motion under the intended V18 objective.

The analytic reward-signal check confirms that the intended V18 low-command
reward prefers forward motion over standing before command-progress termination:

```text
x command: 0.04
standstill reward: -1.3686
required-speed reward at vx=0.026: 1.6494
command-speed reward at vx=0.040: 2.2800
```

Conclusion: do not keep tuning reward weights in the same cold-start family.
The next decisive experiment is an imitation/reference-gait seed test. If a
seeded gait refines into stable low-command forward motion, the blocker was
cold-start discovery. If a working seed degrades into standstill/reverse, the
reward/task landscape is actively hostile and must be debugged from that
reference behavior.

### V19 Reference-Imitation Seed Plan

The upstream Open Duck reference-motion artifact is available and has been
audited:

```text
reference_path:
  ../Open_Duck_Playground/playground/open_duck_mini_v2/data/polynomial_coefficients.pkl
nearest x=0.04 reference key:
  0.074_-0.037_-0.074
period:
  0.54 s / 27 steps at 50 Hz
```

The reference file contains the 14 runtime action joints plus antenna
dimensions. The active Playground imitation reward compares the leg joint
pose/velocity, base velocity, base angular velocity, and foot contacts; the
head/neck dimensions are present in the reference but excluded from the
leg-imitation error term.

The reference seed has an important command mismatch:

```text
requested command: x=0.04, y=0.0, yaw=0.0
nearest reference command: x=0.074, y=-0.037, yaw=-0.074
sampled reference mean linvel_x: 0.0772 m/s
sampled reference mean linvel_y: -0.0417 m/s
sampled reference p95_abs linvel_y: 0.2804 m/s
```

So V19 tested a nearby/faster/side-biased reference-motion reward, not a
perfectly matched straight `x=0.04` gait reference.

V19 is now the planned decisive split:

```text
recipe: movement_bootstrap_v19
phase: phase1_reference_imitation_seed_x004
dynamics: vanilla
actuator bridge: disabled
train command range: x=0.035-0.045
gate command: x=0.04
gate seeds: 0-7
imitation_scale: 4.0
alive_scale: 0.0
```

Decision rule:

```text
PASS:
  V19 refines the reference gait into coherent low-command forward motion
  across seeds. Cold-start discovery was the blocker.

HOLD:
  V19 degrades into standstill, reverse, collapse, or command-progress failure.
  The reward/task landscape is hostile even to the reference gait, and the next
  work should debug the reference path rather than launch more reward variants.
```

Summary artifacts:

```text
outputs/analysis/A100_V18_PHASE1_LOW_COMMAND_HOLD_SUMMARY.md
outputs/analysis/V18_PHASE1_LOW_COMMAND_SEED_GATE.md
outputs/analysis/v18_phase1_low_command_seed_gate.json
outputs/analysis/V18_PHASE1_REWARD_OVERRIDE_REPLAY_SUMMARY.md
outputs/analysis/LOW_COMMAND_REWARD_SIGNAL_V18.md
outputs/analysis/REFERENCE_MOTION_SEED_AUDIT.md
outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V19.md
docs/LOW_COMMAND_DISCOVERY_DECISION.md
```

### V19 A100 Partial Result

V19 phase 1 trained on A100 and reached the x=0.04 multi-seed phase gate using
vanilla dynamics and the V19 reward overrides. The Colab session was lost before
final artifact bundling/download, so seeds 6-7 and the final ONNX were not
recovered. The six completed seed results were enough to reject the candidate as
a pass:

| seed | samples | vx mean m/s | track ratio | result |
|---:|---:|---:|---:|---|
| 0 | 70 | -0.0010 | -0.0239 | fall/termination |
| 1 | 34 | -0.0898 | -2.2442 | reverse/collapse |
| 2 | 70 | 0.0077 | 0.1931 | low progress/fall |
| 3 | 70 | -0.0161 | -0.4032 | reverse/fall |
| 4 | 149 | 0.0080 | 0.1999 | low progress/fall |
| 5 | 46 | -0.3257 | -8.1420 | hard reverse/collapse |

Interpretation:

```text
V19 does not support PASS_SEEDED_GAIT_REFINES.
The reference-imitation reward did not produce coherent low-command forward
motion in the observed seeds.
```

The next offline question is now sharper:

```text
Does the current environment/reward preserve and reward the upstream reference
trajectory when it is followed, or does the task landscape destroy it?
```

That investigation must account for the reference-command mismatch above before
concluding that all imitation/bootstrap approaches are exhausted.

An interpolation audit found a cleaner possible reference candidate:

```text
source keys:
  0.0_-0.037_-0.074
  0.0_0.037_-0.074
  0.074_-0.037_-0.074
  0.074_0.037_-0.074
composite mean linvel_x: 0.0426 m/s
composite mean linvel_y: -0.0021 m/s
```

Interpretation:

```text
Do not rerun V19 unchanged.
The next useful offline step is to synthesize/score an interpolated straight
x=0.04 reference, then decide whether V20 should train against that reference.
```

A synthesized training-only reference override has been built and validated:

```text
override: outputs/analysis/reference_motion_x004_override.pkl
replaced key: 0.074_-0.037_-0.074
validated command lookup: x=0.04, y=0.0, yaw=0.0
mean linvel_x: 0.0426 m/s
mean linvel_y: -0.0021 m/s
```

This artifact is not a robot/runtime file. The next implementation step is to
make the Colab workflow apply it explicitly for a V20 training run and record
its hash in the run manifest.

That workflow support now exists:

```text
recipe: movement_bootstrap_v20
wrapper flag: --reference-motion-override
override: outputs/analysis/reference_motion_x004_override.pkl
manifest tracking:
  - source sha256
  - destination sha256
  - backup sha256
  - restored destination sha256
```

V20 is the next offline A100 candidate. It repeats the reference-imitation split
with the synthesized straight `x=0.04` reference override instead of the raw
side-biased nearest reference. It must still be judged by the x=0.04 vanilla
multi-seed phase gate:

```text
PASS:
  coherent positive forward motion across seeds

HOLD:
  standstill, reverse, collapse, low progress, or command-progress failure
```

Do not run x=0.08, fitted bridge, or robot validation from V20 unless that
low-command vanilla gate passes.

V20 has now run and held:

```text
training: A100, JAX 0.7.2, vanilla dynamics
reference override: applied and restored with sha256 manifest
candidate: 2026_06_25_033305_337920.onnx
gate: x=0.04, vanilla, CPU trace fallback, seeds 0-7
runs: 8
early terminations: 8
duration_complete: 0
mean vx: -0.0539 m/s
mean track ratio: -1.3468
sample range: 33-152 ticks
mean lateral p95_abs velocity: 0.3793 m/s
```

Interpretation:

```text
V20 corrected the V19 reference-command mismatch, but the matched reference
still did not lock into coherent low-command forward motion. The failure is
still low/reverse progress across seeds. Lateral motion is a tracked
contributor, not a sufficient standalone explanation.
```

This closes the current reward-weight/reference-mismatch loop. The next work is
to debug the imitation pathway directly:

```text
1. policy/reference phase alignment
2. forced reference-following reward score
3. early termination versus reference lock
4. behavior-cloning/supervised pretraining before PPO
```

The first reference-lock diagnostic now passes analytically:

```text
status: PASS_REFERENCE_SIGNAL_COHERENT
matched reference mean vx: 0.0426 m/s
progress ratio over 70 ticks: 1.0512
command-progress failure floor: 0.2000
ideal imitation scaled reward: 24.0
pre-terminal unclipped reward sum mean: 50.8050
lateral p95_abs velocity: 0.2350 m/s
```

Interpretation:

```text
The matched reference kinematics are coherent for x=0.04 as a reward/progress
signal. PPO failed to acquire/preserve that reference, but the next playback
diagnostic shows the raw reference targets are not yet a stable action-contract
input. Do not jump directly to behavior cloning before resolving that
conversion/phase/contact issue.
```

Do not deploy V19. Do not run x=0.08. Do not run robot validation.

### V20 Reference-Target Rollout

An offline mechanism diagnostic replaced the ONNX policy with actions derived
from the matched reference joint targets. It still used the runtime-style
contract:

```text
target = home + action * action_scale
max_motor_velocity rate limit active
no qpos teleporting to the reference
```

Result at `x=0.04`, vanilla dynamics, seeds `0-7`:

```text
status: HOLD_REFERENCE_TARGET_TERMINATES
runs: 8
early terminations: 8
duration_complete: 0
mean vx: -0.0105 m/s
mean track ratio: -0.2614
mean lateral p95_abs velocity: 0.3918 m/s
mean action saturation: 6.4967%
mean target clip p95: 0.0314 rad
mean joint tracking p95: 0.1876 rad
mean reference contact mismatch: 69.50%
```

Pitch-chain stress:

```text
left_hip_pitch: 23.1496% action saturation, 3.9927 rad/s sent velocity p95
left_knee: 15.2756% action saturation, 5.2400 rad/s sent velocity p95
left_ankle: 12.1260% action saturation, 3.9546 rad/s sent velocity p95
right_hip_pitch: 18.7402% action saturation, 5.1082 rad/s sent velocity p95
right_knee: 15.7480% action saturation, 5.2400 rad/s sent velocity p95
right_ankle: 5.9843% action saturation, 5.1066 rad/s sent velocity p95
```

Interpretation:

```text
The V20 matched reference passes analytic progress/reward checks, but direct
reference-derived actions do not produce stable simulated motion through the
current action-scale and target-rate contract. The next branch is not another
reward-weight PPO run. Inspect reference-to-action mapping, reference phase and
reset alignment, lateral/contact timing, and target velocity before BC or PPO.
```

Artifact:
`outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20.md`.

### V20 Reference Action Envelope

The matched reference was audited against the deployed action contract without
running a simulation:

```text
action = (reference_target - home) / action_scale
action_scale = 0.25
target velocity budget = 5.24 rad/s
```

Result:

```text
status: HOLD_REFERENCE_EXCEEDS_ACTION_ENVELOPE
closest phases to home have 0 saturated joints
left_knee target velocity p95/max: 8.0846 / 8.6417 rad/s
right_knee target velocity p95/max: 9.8963 / 13.2122 rad/s
right_hip_pitch target velocity p95/max: 5.4889 / 6.0116 rad/s
right_ankle target velocity p95/max: 4.8676 / 7.6140 rad/s
right_knee max_abs_action: 2.2704
right_hip_pitch max_abs_action: 1.9062
```

Interpretation:

```text
The command-matched reference is not a deployable action target as-is. It has a
valid low-command mean velocity, but its raw joint trajectory exceeds both the
policy action envelope and the target-rate budget. The next work is an
envelope-aware reference projection/filter or realized-target dataset, not BC
against raw polynomial joint positions.
```

Artifact:
`outputs/analysis/REFERENCE_ACTION_ENVELOPE_V20.md`.

### V20 Projected Reference Rollout

An envelope-aware projection scaled each joint's reference cycle to fit the
action/rate budget before replaying the same reference-derived target path.

Result:

```text
status: HOLD_REFERENCE_TARGET_TERMINATES
runs: 8
early terminations: 8
duration_complete: 0
mean vx: -0.0100 m/s
mean track ratio: -0.2495
mean lateral p95_abs velocity: 0.4017 m/s
mean action saturation: 1.1454%
mean target clip p95: 0.0000 rad
mean joint tracking p95: 0.1440 rad
mean reference contact mismatch: 68.85%
```

Interpretation:

```text
Projection reduced saturation and tracking error, but it did not produce
stable forward motion. The current blocker is not just target velocity. Inspect
reference phase/reset alignment, contact timing, lateral sway, and reference
compatibility with the current Joystick task before BC or another PPO run.
```

Artifact:
`outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_PROJECTED.md`.

### V20 Projected Phase-Offset Check

The projected reference was replayed starting at phases closest to the home
pose:

```text
phase 1:  HOLD, samples mean 83.0000, track ratio -0.2495, contact mismatch 68.85%
phase 5:  HOLD, samples mean 81.6250, track ratio -0.4917, contact mismatch 68.15%
phase 19: HOLD, samples mean 69.3750, track ratio -1.2155, contact mismatch 68.54%
```

Interpretation:

```text
Reference reset phase is not the sufficient fix. Even projected and started
near home, the polynomial reference does not generate stable forward motion in
the current Joystick task, and reference/actual contact mismatch stays near
68-70%. Next: inspect contact/lateral/reference compatibility or build targets
from realized stable rollouts.
```

Artifacts:

```text
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_PROJECTED_PHASE5.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_PROJECTED_PHASE19.md
```

### V20 Reference Contact Compatibility

Trace-level contact analysis compares the polynomial reference contact schedule
with realized simulated contacts:

```text
raw reference:        68.03% mismatch, actual double support 73.86%, reference double support 35.43%
projected phase 1:   67.77% mismatch, actual double support 75.90%, reference double support 35.54%
projected phase 5:   67.23% mismatch, actual double support 74.89%, reference double support 37.52%
projected phase 19:  67.57% mismatch, actual double support 74.41%, reference double support 38.38%
```

Interpretation:

```text
The simulated body mostly remains in double support while the reference expects
alternating single support. This explains why envelope projection and phase
offsets did not recover the gait. Left/right swap only reduces mismatch to
about 65-66%, and polarity inversion is worse, so this is not just contact-bit
encoding. Do not train BC against raw polynomial joint positions; use
contact-aware reference adaptation or generated realized targets from stable
simulated behavior.
```

Artifact:
`outputs/analysis/REFERENCE_CONTACT_COMPATIBILITY_V20.md`.

Additional artifact:

```text
outputs/analysis/A100_V19_REFERENCE_SEED_PARTIAL_HOLD_SUMMARY.md
outputs/analysis/a100_v19_reference_seed_partial_hold_summary.json
outputs/analysis/REFERENCE_GRID_INTERPOLATION.md
outputs/analysis/REFERENCE_MOTION_OVERRIDE.md
outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V20.md
outputs/analysis/V20_MANUAL_SEED_GATE_CPU_TRACE_FULL.md
outputs/analysis/V20_MATCHED_REFERENCE_TRACE_SUMMARY.md
outputs/analysis/REFERENCE_LOCK_SIGNAL_V20.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20.md
outputs/analysis/REFERENCE_ACTION_ENVELOPE_V20.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_PROJECTED.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_PROJECTED_PHASE5.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_PROJECTED_PHASE19.md
outputs/analysis/REFERENCE_CONTACT_COMPATIBILITY_V20.md
```

### Realized Target Window Mine

Existing simulated rollout traces were mined for short windows that already
show realized forward motion under the current Joystick task and sim contact
dynamics.

```text
tool: tools/mine_realized_target_windows.py
status: PASS_REALIZED_WINDOWS_AVAILABLE
window_samples: 25
candidate windows: 17
best mean vx: 0.1071 m/s
best min base height: 0.1500 m
best pitch p95: 0.3954 rad
best action saturation: 0.0%
best sent target velocity p95: 1.3416 rad/s
best tracking p95: 0.0907 rad
```

Interpretation:

```text
The raw V20 polynomial reference remains a poor direct BC/action target, but
the actual sim traces contain short realized forward-motion snippets. These
are useful as motion hints or candidate dataset seeds only. They are not stable
full-horizon walking evidence, and several are pre-fall windows, so termination
margin and post-window outcome must be kept with any future dataset.
```

Next offline step:

```text
curate realized-target windows with stricter survival/contact filters before
any supervised seed or new PPO run
```

Additional artifacts:

```text
outputs/analysis/REALIZED_TARGET_WINDOW_MINE.md
outputs/analysis/realized_target_window_mine.json
```

### Realized Target Window Curation

The mined windows were filtered with stricter dataset-readiness criteria before
allowing any supervised seed or BC interpretation.

```text
tool: tools/curate_realized_target_windows.py
status: HOLD_INSUFFICIENT_CURATED_WINDOWS
required curated windows: 8
curated seed windows: 1
review-only motion hints: 15
rejected dataset seeds: 1
```

Only one short window currently passes the conservative seed-material gate. Most
otherwise useful snippets fail because of high lateral velocity, high body
pitch, short margin before termination, or a dominant double-support contact
pattern.

Decision:

```text
Do not launch BC/PPO from the current realized-window manifest. It is useful
for diagnosing what motion exists, but not sufficient as a stable low-command
target dataset.
```

Next offline step:

```text
generate or mine more stable realized low-command windows with stricter
survival, lateral, pitch, and contact-diversity filters
```

Additional artifacts:

```text
outputs/analysis/REALIZED_TARGET_WINDOW_CURATION.md
outputs/analysis/realized_target_window_curation.json
```

### Broad Realized-Window Archive Sweep

The realized-window miner and curation gate were rerun across the broader set of
compatible JSONL traces already in `outputs/analysis`.

```text
status: HOLD_INSUFFICIENT_CURATED_WINDOWS
compatible mined windows: 94
curated seed windows: 1
review-only motion hints: 37
rejected dataset seeds: 56
```

Conclusion:

```text
There is not enough clean seed data hiding in the existing trace archive. The
archive contains useful motion hints and failure evidence, but only one window
passes the conservative seed-material filter.
```

Next offline step:

```text
generate new low-command realized target traces deliberately, or adapt the
reference/contact path until it produces stable realized contacts, then rerun
the same curation gate
```

Additional artifacts:

```text
outputs/analysis/REALIZED_TARGET_WINDOW_MINE_BROAD.md
outputs/analysis/realized_target_window_mine_broad.json
outputs/analysis/REALIZED_TARGET_WINDOW_CURATION_BROAD.md
outputs/analysis/realized_target_window_curation_broad.json
```

### Contact-Gated Reference Projection

A simple contact-aware target adaptation was tested offline:

```text
mode: contact_gated_projected
rule: damp a leg's projected reference target when the reference expects that
      foot to swing but the simulated foot is still loaded
contact_gate_swing_scale: 0.35
command: x=0.04
seeds: 0-7
```

Result:

```text
status: HOLD_REFERENCE_TARGET_TERMINATES
falls: 7/8
duration complete: 1/8
mean vx: 0.0012 m/s
mean track ratio: 0.0288
mean lateral p95_abs velocity: 0.3960 m/s
mean contact mismatch: 69.4217%
curated seed windows: 0
```

Contact comparison:

```text
raw reference mismatch:               68.03%
cycle projected mismatch:             67.77%
projected phase 5 mismatch:           67.23%
projected phase 19 mismatch:          67.57%
contact-gated projected mismatch:     66.35%
contact-gated actual double support:  84.95%
```

Conclusion:

```text
Simple contact-gated swing damping is not enough. It slightly reduces contact
mismatch but mostly keeps the sim in double support and still fails the target
rollout. The next target-generation approach must be more stateful than this
one-step damping rule.
```

Additional artifacts:

```text
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_CONTACT_GATED_PROJECTED.md
outputs/analysis/reference_motion_rollout_v20_contact_gated_projected.json
outputs/analysis/REFERENCE_CONTACT_COMPATIBILITY_V20_WITH_CONTACT_GATED.md
outputs/analysis/reference_contact_compatibility_v20_with_contact_gated.json
outputs/analysis/REALIZED_WINDOW_CONTACT_GATED_REFERENCE_MINE.md
outputs/analysis/realized_window_contact_gated_reference_mine.json
outputs/analysis/REALIZED_WINDOW_CONTACT_GATED_REFERENCE_CURATION.md
outputs/analysis/realized_window_contact_gated_reference_curation.json
```

### Contact-Synchronized Reference Projection

A stronger stateful adaptation was tested after simple contact gating:

```text
mode: contact_synchronized_projected
rule: retime the projected reference phase toward the current simulated contact
      pattern, using forward phase distance as a tie-break
command: x=0.04
seeds: 0-7
```

Result:

```text
status: HOLD_REFERENCE_TARGET_TERMINATES
falls: 7/8
duration complete: 1/8
mean vx: -0.0152 m/s
mean track ratio: -0.3788
mean lateral p95_abs velocity: 0.3867 m/s
mean joint tracking p95: 0.1059 rad
mean per-seed contact mismatch: 7.7531%
aggregate contact mismatch: 4.36%
curated seed windows: 0
```

Conclusion:

```text
Reference phase/contact retiming is not sufficient. It fixes most contact
mismatch, but does so while losing forward locomotion and still terminating in
7/8 seeds. The next target generator must jointly optimize forward progress,
lateral stability, body pitch/height, and contact transitions.
```

Additional artifacts:

```text
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_CONTACT_SYNCHRONIZED_PROJECTED.md
outputs/analysis/reference_motion_rollout_v20_contact_synchronized_projected.json
outputs/analysis/REFERENCE_CONTACT_COMPATIBILITY_V20_WITH_CONTACT_ADAPTATIONS.md
outputs/analysis/reference_contact_compatibility_v20_with_contact_adaptations.json
outputs/analysis/REALIZED_WINDOW_CONTACT_SYNCHRONIZED_REFERENCE_MINE.md
outputs/analysis/realized_window_contact_synchronized_reference_mine.json
outputs/analysis/REALIZED_WINDOW_CONTACT_SYNCHRONIZED_REFERENCE_CURATION.md
outputs/analysis/realized_window_contact_synchronized_reference_curation.json
```

### Target Generation Plan

The next offline path is now specified in:

```text
docs/TARGET_GENERATION_PLAN.md
```

The project should not launch another reward-only PPO run or BC run from the
current mined snippets. The next implementation target is a deliberate
low-command target generator that jointly preserves:

```text
positive forward velocity
low lateral velocity
safe body pitch and base height
real contact transitions
actuator/action envelope compliance
```

Promotion gate:

```text
PASS_CURATED_DATASET_SEED_READY
```

### First Primitive Target Search

A bounded low-dimensional target primitive search was implemented and run
offline:

```text
tool: tools/search_low_command_target_primitives.py
command: x=0.04
duration: 3 s
seeds: 0
candidates: 12
```

Result:

```text
search status: PASS_TARGET_SEARCH_RAN
best mean vx: 0.0018 m/s
window mine: HOLD_NO_REALIZED_WINDOWS
curated seed windows: 0
```

Conclusion:

```text
The tested anti-phase hip/knee/ankle sine primitives are stable but do not
produce forward locomotion. The next target generator needs explicit forward
displacement pressure or stance/foot-placement asymmetry.
```

Additional artifacts:

```text
outputs/analysis/TARGET_GENERATOR_SEARCH.md
outputs/analysis/target_generator_search.json
outputs/analysis/TARGET_GENERATOR_WINDOW_MINE.md
outputs/analysis/target_generator_window_mine.json
outputs/analysis/TARGET_GENERATOR_WINDOW_CURATION.md
outputs/analysis/target_generator_window_curation.json
```

### Biased Primitive Target Search

The primitive generator was extended with common hip/knee/ankle pitch biases
and a small opposite hip-roll bias probe.

Result:

```text
biased pitch-chain search:
  curated windows: 5
  status: HOLD_INSUFFICIENT_CURATED_WINDOWS

biased multiseed search:
  seeds: 0,1,2,3
  curated windows: 5
  status: HOLD_INSUFFICIENT_CURATED_WINDOWS

roll-bias probe:
  seeds: 0,2
  curated windows: 12
  curated source/mode pairs: 12
  curated source files: 1
  status: HOLD_INSUFFICIENT_CURATED_DIVERSITY
```

Interpretation:

```text
This is the first target-generation pass that produces enough compact curated
windows by count, but it fails the diversity gate because all curated windows
are from seed_000. Seed_002 contributes review-only hints but still fails
lateral/contact criteria. Do not launch BC/PPO from this as if it were a
diverse walking dataset; use it as evidence that forward-biased primitive
targets can create safe low-command motion snippets.
```

Next:

```text
add seed-diversity and lateral/contact scoring to the target generator, then
build a deliberate compact target dataset from windows that are not all from one
seed.
```

### Seed-2 Rescue Search

A targeted seed-2 grid swept stronger opposite hip-roll bias and finer phase
offsets around the best biased primitive family.

Result:

```text
seed: 2
candidates: 50
window mine: PASS_REALIZED_WINDOWS_AVAILABLE
curated windows: 0
review hints: 80
rejected windows: 11
status: HOLD_INSUFFICIENT_CURATED_WINDOWS
```

Conclusion:

```text
Manual roll/phase expansion did not produce seed_002 curated windows. Early
motion windows fail lateral velocity; later lower-lateral windows become
single-contact dominated. The next target-generator step should be an optimizer
or scored search over lateral/contact criteria, not another reward-training run
and not a broader blind hand grid.
```

### Shuffled Broad Primitive Search

The primitive search added deterministic candidate shuffling and sampled a
broader target grid across seeds 0 and 2.

Result:

```text
sampled candidates: 40
grid_seed: 20260625
window mine: PASS_REALIZED_WINDOWS_AVAILABLE
curation status: PASS_CURATED_DATASET_SEED_READY
curated windows: 11
curated source files: 2
curated source/mode pairs: 11
seed distribution: seed_000=10, seed_002=1
```

Conclusion:

```text
This is the first compact target-generation result that passes the stricter
diversity gate. It is still skewed toward seed_000, but it provides a concrete
candidate seed dataset for the next offline step: build a compact target-dataset
manifest and sanity-check it before any supervised/imitation training.
```

### Target Dataset Manifest

The curated windows were converted into a compact manifest that does not copy
raw trace contents:

```text
tool: tools/build_target_dataset_manifest.py
dataset_id: e84d27e27fd73419
status: PASS_TARGET_DATASET_MANIFEST_READY
entries: 11
source files: 2
source/mode pairs: 11
source distribution: seed_000=10, seed_002=1
mean vx: 0.0718 m/s
sent target velocity p95: 0.6138 rad/s
joint tracking p95 max: 0.0709 rad
```

Conclusion:

```text
The project now has a reviewable low-command target seed manifest. It is still
small and seed-skewed, so the next valid action is a no-training manifest sanity
check, then at most a tiny supervised/imitation smoke experiment. Do not jump
straight to a larger PPO run.
```

### Target Dataset Sanity Check

The manifest was checked against the local ignored source traces:

```text
tool: tools/check_target_dataset_manifest.py
dataset_id: e84d27e27fd73419
status: WARN_TARGET_DATASET_SANITY_SOURCE_SKEW
entries checked: 11
entries with errors: 0
bc readiness: HOLD_TARGET_DATASET_BC_OBSERVATIONS_MISSING
bc ready entries: 0
source files: 2
source distribution: seed_000=10, seed_002=1
max source fraction: 0.9091
```

Conclusion:

```text
The compact target manifest is internally consistent with the local source
traces, but it is not behavior-cloning ready because the trace records do not
include the 101-element policy observation vector. The next valid offline step
is to record `obs[101]` in target-generation traces, rebuild the compact
manifest, and rerun the sanity check until BC readiness passes.
```

### Observation-Ready Target Dataset

The primitive generator was updated to include `observation[101]`, then the
same shuffled broad search was rerun and remanifested.

Result:

```text
dataset_id: 6c43c18e8f2b72ec
curation status: PASS_CURATED_DATASET_SEED_READY
manifest status: PASS_TARGET_DATASET_MANIFEST_READY
sanity status: WARN_TARGET_DATASET_SANITY_SOURCE_SKEW
bc readiness: PASS_TARGET_DATASET_BC_READY
entries: 11
source files: 2
source distribution: seed_000=10, seed_002=1
```

Conclusion:

```text
The project now has a technically BC-ready low-command target seed manifest.
It is still tiny and source-skewed, so the next offline experiment must be a
tiny supervised/imitation smoke run only, followed by sim evaluation for
low-command forward motion. Do not jump directly to larger PPO.
```

### V5/V7 Low-Command Trace Collection

A no-training CPU trace collection replayed the old moving-lineage policies at
the low command where target data is needed:

```text
command: x=0.04
dynamics: vanilla
policies: v5_phase1, v7_anchor
seeds: 0-3
duration: 5 s
trace output: enabled
```

Candidate result:

```text
v5_phase1: 3/4 low-forward-progress holds, 1/4 fall-or-termination
v7_anchor: 3/4 low-forward-progress holds, 1/4 fall-or-termination
```

Target-window result:

```text
window mine: HOLD_NO_REALIZED_WINDOWS
curated seed windows: 0
```

Conclusion:

```text
The old moving-lineage policies do not generate useful low-command target
windows when replayed at x=0.04. The target-data path needs a new generation
strategy rather than more harvesting from V5/V7 at low command.
```

Additional artifacts:

```text
outputs/analysis/REALIZED_WINDOW_COLLECTION_X004_V5_V7_CPU.md
outputs/analysis/realized_window_collection_x004_v5_v7_cpu.json
outputs/analysis/REALIZED_WINDOW_COLLECTION_X004_V5_V7_MINE.md
outputs/analysis/realized_window_collection_x004_v5_v7_mine.json
outputs/analysis/REALIZED_WINDOW_COLLECTION_X004_V5_V7_CURATION.md
outputs/analysis/realized_window_collection_x004_v5_v7_curation.json
```

### Target Dataset BC Smoke

A tiny offline behavior-cloning smoke was run from the observation-ready target
manifest. The first pass was a linear ridge fit over curated
`obs[101] -> action[14]` samples followed by short CPU closed-loop replay at
`x=0.04`. A second KNN replay tested whether the linear model was simply
extrapolating badly from the tiny dataset.

Result:

```text
tool: tools/run_target_dataset_bc_smoke.py
dataset_id: 6c43c18e8f2b72ec
samples: 275
source files: 2
source distribution: seed_000=10 windows, seed_002=1 window
sample/parameter ratio: 0.1926
supervised fit: near-exact on train samples
closed-loop status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
seed_000 replay: vx=-0.0023 m/s, ratio=-0.0565, duration complete
seed_002 replay: vx=+0.0014 m/s, ratio=+0.0340, duration complete
rollout action_abs_mean: about 0.0001
knn closed-loop status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
knn seed_000 replay: vx=+0.0139 m/s, ratio=+0.3463, duration complete
knn seed_002 replay: vx=+0.0072 m/s, ratio=+0.1798, duration complete
knn action_abs_mean: 0.0904-0.1209
```

Conclusion:

```text
The compact target dataset is BC-ready by schema, but a simple one-shot linear
BC policy overfits short curated windows and collapses to near-zero actions in
closed-loop replay. KNN does produce nonzero actions and a little forward
motion, but still does not reach useful low-command tracking. This is a useful
hold: do not scale this directly into PPO or a larger supervised run. The next
target-data step should improve temporal coverage/diversity or use a
sequence-aware imitation design that preserves the curated target motion through
closed-loop replay.
```

### Longer Target Window Remine

The observation-ready shuffled broad traces were remined for 50-sample windows
to test whether the current trace set contains enough temporal coverage for a
better supervised seed.

Result:

```text
tool: tools/mine_realized_target_windows.py
trace set: target_generator_shuffled_broad_obs_traces
window length: 50 samples
mine status: PASS_REALIZED_WINDOWS_AVAILABLE
curation status: HOLD_INSUFFICIENT_CURATED_WINDOWS
mined windows: 5
curated seed windows: 0
review motion hints: 5
source: seed_002 only
failure reasons: high_lateral_velocity and/or single_contact_pattern_dominates
```

Conclusion:

```text
The current trace set does not contain longer seed-quality forward-motion
windows. The next target-generation change should directly reduce lateral
motion and single-contact dominance over longer horizons instead of trying to
train from the existing short snippets.
```

### Targeted Lateral/Contact Primitive Search

A targeted CPU-only primitive search narrowed the grid around lower hip-roll
bias, lower lateral motion, and the primitive families that produced 50-sample
review hints.

Result:

```text
tool: tools/search_low_command_target_primitives.py
command: x=0.04
duration: 4 s
seeds: 0,2
candidates: 48
search status: PASS_TARGET_SEARCH_RAN
25-sample curation: HOLD_INSUFFICIENT_CURATED_DIVERSITY
25-sample curated windows: 25
50-sample curation: HOLD_INSUFFICIENT_CURATED_DIVERSITY
50-sample curated windows: 8
curated source files: 1
```

Conclusion:

```text
This is a meaningful target-generation improvement: 50-sample seed-quality
windows now exist. The remaining blocker is seed/source diversity, not target
rate, tracking, or lack of any longer forward snippets. Do not train from this
yet; the next search should explicitly make the seed_002 review hints pass by
reducing lateral velocity and single-contact dominance.
```

### Seed 2 Balance Search

A second bounded CPU-only search used finer phase offsets and smaller hip-roll
bias around the seed 2 review hints.

Result:

```text
tool: tools/search_low_command_target_primitives.py
command: x=0.04
duration: 4 s
seeds: 0,2
candidates: 80
search status: PASS_TARGET_SEARCH_RAN
25-sample curation: HOLD_INSUFFICIENT_CURATED_DIVERSITY
25-sample curated windows: 45
50-sample curation: HOLD_INSUFFICIENT_CURATED_DIVERSITY
50-sample curated windows: 23
curated source files: 1
curated source: seed_000
seed_002 status: review-only, mostly high_lateral_velocity or single_contact_pattern_dominates
```

Conclusion:

```text
The generator can now produce many short and longer seed-quality windows, but
the cross-seed diversity blocker is robust. Seed 2 repeatedly gets close and
then fails lateral/contact criteria. The next useful target-generation work
should stop broad random sweeps and add a seed-robust scoring/objective term
for lateral velocity and contact alternation.
```

### Target Seed Robustness Audit

A compact seed-robustness audit grouped the latest 50-sample curation outputs by
primitive mode and source seed.

Result:

```text
tool: tools/analyze_target_seed_robustness.py
status: HOLD_SEED2_LATERAL_CONTACT
robust modes across seed_000 and seed_002: 0
seed0-curated / seed2-review near misses: 12
seed2 reason counts:
  single_contact_pattern_dominates: 64
  high_lateral_velocity: 40
```

Conclusion:

```text
The seed-diversity blocker is now specific: seed2 near misses either need
lateral p95 reduced from roughly 0.16-0.18 toward <=0.12 m/s, or contact
dominance reduced from 100% toward <=95%. This should be the next target
objective, not another generic grid expansion.
```

Next target-generator spec:

```text
docs/TARGET_OBJECTIVE_GENERATOR_SPEC.md
```

### Target Objective Score

An objective-driven scorer was added to rank existing target traces by worst
seed rather than aggregate velocity.

Result:

```text
tool: tools/score_target_candidates_objective.py
latest seed2-balance trace set: HOLD_NO_SEED_ROBUST_TARGETS
robust 50-sample modes: 0
best worst-seed mode:
  primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927
  seed0: pass, vx=0.0565 m/s
  seed2: vx=0.0515 m/s, vy95=0.0507 m/s, contact_dominance=98%
  seed2 failure: single_contact_pattern_dominates
```

Conclusion:

```text
The best current candidate already clears seed2 forward velocity and lateral
velocity. The remaining near-pass blocker is contact dominance: reduce the best
seed2 contact dominance from 98% to <=95% without losing seed0. This is a more
precise target than the earlier broad lateral/contact diagnosis.
```
