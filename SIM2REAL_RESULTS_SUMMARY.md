# Sim-To-Real Results Summary

Last updated: 2026-06-28

## Executive Summary

Current recommendation: **hold further grounded tests from this candidate as-is**.

The corrected candidate
`policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx`
cleared corrected-bridge sim gates and stand/suspended hardware transfer at
`x=0.0` and `x=0.08`. A first bounded grounded telemetry test at `x=0.08`
completed its 5 second runtime and turned off normally, but the operator
reported the office-chair plastic mat surface was likely too slippery and
telemetry showed elevated tracking p95 around `0.106 rad`. A repeated bounded
run on medium carpet also completed normally and improved pitch-chain tracking
p95 to about `0.071 rad` with no saturation, no write errors, and no timing
spikes. The operator reported that the robot appeared to step on the carpet but
did not lift its feet enough to walk forward, so the current hold is
visual/insufficient-foot-clearance despite acceptable actuator tracking.

Latest artifacts:

```text
outputs/analysis/CORRECTED_CANDIDATE_STAND_TRANSFER_DECISION.md
outputs/analysis/CORRECTED_CANDIDATE_FIRST_GROUNDED_TEST_DECISION.md
outputs/analysis/CORRECTED_CANDIDATE_SECOND_SURFACE_GROUNDED_TEST_DECISION.md
outputs/analysis/CORRECTED_CANDIDATE_HW_X008_GROUNDED_FIRST_ANALYSIS.md
outputs/analysis/CORRECTED_CANDIDATE_HW_X008_GROUNDED_SECOND_SURFACE_ANALYSIS.md
outputs/analysis/CORRECTED_CANDIDATE_HW_X008_GROUNDED_FIRST_TARGET_VELOCITY.md
outputs/analysis/CORRECTED_CANDIDATE_HW_X008_GROUNDED_SECOND_SURFACE_TARGET_VELOCITY.md
```

First grounded telemetry summary:

```text
samples: 249
remote exit: 0
terminal: Max runtime reached -> TURNING OFF
max pitch-chain sent velocity p95: 1.83 rad/s
max pitch-chain tracking p95: 0.106 rad
action saturation: 0%
rate limit active: 0%
write errors: 0
read checksum increments: 12
```

Second surface grounded telemetry summary:

```text
samples: 249
remote exit: 0
terminal: Max runtime reached -> TURNING OFF
max pitch-chain sent velocity p95: 1.21 rad/s
max pitch-chain tracking p95: 0.071 rad
action saturation: 0%
rate limit active: 0%
write errors: 0
read checksum increments: 6
surface: medium carpet
operator visual result: stepping attempt, but insufficient foot lift to walk
forward
```

Do not extend duration or repeat grounded tests from this candidate as-is until
offline review explains why trackable joint commands produced stepping without
enough foot clearance/advance.

Phase 2 offline robustness work now confirms that the carpet observation maps
to a terrain/clearance weakness, not an actuator-envelope failure. The promoted
Phase 1 candidate remains trackable, and Stage A tolerates mild/moderate push
evals, but `z=0.002` rough-terrain screens show a low-clearance shuffle. C3
raised single support only slightly, C4 over-drove and fell, C5a retreated into
double support, and C6 with stronger transition pressure still regressed to
very low forward progress. C7 added frequent checkpoint export and
gate-selected terrain screening; it found a useful early checkpoint, but not a
terrain candidate:

```text
latest decision: outputs/analysis/PHASE2_STAGE_C7_GATE_SELECTION_DECISION.md
status: HOLD_STAGE_C7_GATE_SELECTION_PARTIAL
c7_35120 terrain z=0.002 8-seed screen:
  passes: 5/8
  falls: 0/8
  mean track ratio: 0.2671
  max pitch-chain tracking p95: 0.1918 rad
  corrected velocity excess: 0.0000 rad/s
  mean min swing peak: 0.0105 m
  mean single support: 11.4%
  mean double support: 88.45%
```

Do not promote the current C-stage terrain policies. The next offline branch
should keep gate-selected checkpointing but change the target manifold: use
higher-clearance stepping demonstrations or a hard step-clearance/step-advance
constraint rather than another small scalar PPO reward tweak.

A C7 pass/fail trace comparison sharpened this: a passing seed had `18.8%`
single support and both feet swinging, while a low-progress seed had only
`4.0%` single support, `96.0%` double support, zero left-foot swing segments,
and two tiny right-foot swing segments. A default-off
`forward_swing_balance` hook is now plumbed for the next offline terrain run to
test whether one-sided double-support collapse can be reduced. It is not a
candidate result.

C8 tested that hook at `forward_swing_balance_scale=-0.05`. It completed
offline training, but all trained checkpoints held low progress on the focused
terrain screen. The best trained checkpoint, `c8_35120`, had track ratio
`0.1819`, `6.8%` single support, and `0.0084 m` min swing peak, worse than the
C7 `35120` transient. Decision: do not increase swing-balance scalar pressure;
the next terrain branch needs a higher-clearance/alternating-step target source
or hard step-advance constraint.

The evaluator now reports passive terrain swing-excursion metrics:
`min_swing_segments` and `min_rel_x_range_p95`. Rechecking the C7 pass/fail
trace showed seed 2 passing with `min_swing_segments=3` and
`min_rel_x_range_p95=0.0059 m`, while seed 4 held with
`min_swing_segments=0` and `min_rel_x_range_p95=0.0000 m`. Future terrain gates
should reject policies that pass tracking by leaving one foot effectively
planted.

The seed-sweep tool now has default-off hard terrain swing thresholds:
`--min-swing-segments-per-foot`, `--min-swing-rel-x-range-p95-m`, and
`--min-swing-peak-lift-m`. When enabled, a nominal pass can be downgraded to
`HOLD_CANDIDATE_TERRAIN_SWING`; this was validated on C7 seed 2 with an
intentionally strict lift threshold.

A compact action-gain diagnostic then tested whether the C7 terrain weakness
was just insufficient action amplitude. It was not. Gain `1.05` preserved seed
2 but left seed 4 planted with `0` min swing segments, `0.0000 m` min
relative-x swing range, `0.0016 m` min swing peak, and `99.2%` double support.
Gain `1.10` degraded both seeds to low-progress holds. No corrected-envelope
excess occurred, so the next terrain branch should change stance/swing
structure rather than add global output gain.

To target that structure directly, the Playground and RDK training wrapper now
expose a default-off `forward_swing_advance` cost. It penalizes touchdown when
the swing foot did not advance forward relative to the body/IMU frame during a
forward-command swing. A tiny CPU smoke passed on the `z=0.002` rough-terrain
setup with the hook enabled. This is not a candidate; it is plumbing for the
next offline C-stage terrain branch.

C9 then tested that hook from the C7 `35120` checkpoint with
`forward_swing_advance_scale=-0.01`, target `0.005 m`, and Huber delta
`0.002`. Training completed and stayed in-envelope, but all trained checkpoints
held low progress on the two-seed terrain screen. The pass-like seed regressed
and the planted-foot seed stayed at `0` min swing segments. Do not promote C9;
the next terrain step needs a higher-clearance alternating-step target source
or hard step-advance constraint, not stronger scalar pressure.

June 27 corrected-knee update: the left knee soft offset was corrected from
`-1.488 rad` to `0.0371 rad`, and a supported/on-stand sine-only actuator gate
passed at `0.25`, `0.5`, and `1.0 Hz` with `0.03 rad` amplitude. The corrected
left knee no longer appears as a low-speed outlier: left/right knee raw
tracking p95 are both about `0.0078 rad`. This clears the low-speed
corrected-knee sanity check, but it does **not** approve walking. The sine-only
fit hit the velocity lower grid bound and is not a replacement for corrected
dynamic policy-waveform evidence.

The corrected suspended `x=0.08` policy replay was then collected on stand.
It still holds for dynamic tracking: pitch-chain target velocity p95 is
`3.14-5.22 rad/s`, pitch tracking p95 is `0.125-0.171 rad` after startup
filtering, and the fitted delay remains `3 ticks`. The corrected dynamic fit
keeps effective velocity limits around `2.0-3.25 rad/s`. The knee correction
improved calibration but did not make `BEST_WALK_ONNX_2` trackable at `x=0.08`.
Grounded replay remains blocked.

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

### Contact-Break Target Search

A focused CPU-only search explored small contact-break perturbations around the
best near-pass family:

```text
tool: tools/search_low_command_target_primitives.py
command: x=0.04
duration: 4 s
seeds: 0,2
candidates: 96
search status: PASS_TARGET_SEARCH_RAN
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust 50-sample modes: 0
```

Best objective-scored candidate:

```text
mode: primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927
seed0: pass, vx=0.0531 m/s
seed2: vx=0.0453 m/s, vy95=0.1028 m/s, contact_dominance=98%
seed2 failure: single_contact_pattern_dominates
```

Curation result:

```text
50-sample curation: HOLD_INSUFFICIENT_CURATED_DIVERSITY
50-sample curated windows: 70
50-sample curated modes: 38
curated source files: 1
curated source: seed_000
25-sample curated windows: 82
```

Conclusion:

```text
The contact-break micro-grid increased seed0 target-window coverage but did not
move the cross-seed blocker. Seed2 still fails the best near-pass at 98%
contact dominance, and most seed2 failures remain 98-100% single-contact
dominance. The current sine primitive family is likely structurally
double-support/contact-dominated on seed2. Do not spend the next iteration on
another nearby grid; add a generator with an explicit contact-lift or
contact-transition objective.
```

### Lift-Pulse Target Search

The primitive generator was extended with default-off swing-lift pulse controls:

```text
tool: tools/search_low_command_target_primitives.py
new flags: --lift-duties, --lift-scales
default behavior: unchanged sine primitive
```

A bounded CPU search tested narrow lift pulses:

```text
command: x=0.04
duration: 4 s
seeds: 0,2
candidates: 96
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust 50-sample modes: 0
```

Best objective-scored lift-pulse candidate:

```text
mode: primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls0p35
seed0: pass, vx=0.0508 m/s
seed2: vx=0.0519 m/s, vy95=0.0937 m/s, contact_dominance=98%
seed2 contact pattern: 98% double contact, 2% single contact
seed2 failure: single_contact_pattern_dominates
```

Curation result:

```text
50-sample curation: HOLD_INSUFFICIENT_CURATED_DIVERSITY
50-sample curated windows: 59
50-sample curated modes: 46
curated source files: 1
curated source: seed_000
25-sample curated windows: 87
```

Conclusion:

```text
The lift pulse lowered target rates and preserved forward/lateral metrics on
some seed2 near misses, but it did not create enough contact alternation.
Seed2 failed single-contact-pattern dominance on every scored mode. The next
generator must change the contact state itself, not just the shape of the knee
lift waveform. Treat this as evidence for an explicit foot-clearance/contact
reward or a different contact-timing primitive.
```

### Foot-Clearance Probe

A smaller CPU probe reran stronger/narrower lift pulses after the generator was
updated to log foot-site height:

```text
tool: tools/search_low_command_target_primitives.py
new trace field: foot_site_z_m
command: x=0.04
duration: 4 s
seeds: 0,2
candidates: 48
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust 50-sample modes: 0
score gate included: min_contact_transitions=3
```

Best objective-scored probe candidate:

```text
mode: primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65
seed0: pass, vx=0.0475 m/s
seed2: vx=0.0565 m/s, vy95=0.1166 m/s, contact_dominance=98%
seed2 contact transitions: 2 / 50 samples
seed2 foot_site_z_p95: 0.0159 m
seed2 failures: high_body_pitch, short_done_margin, single_contact_pattern_dominates, too_few_contact_transitions
```

Curation result:

```text
50-sample curation: HOLD_INSUFFICIENT_CURATED_DIVERSITY
50-sample curated windows: 23
50-sample curated modes: 19
curated source files: 1
curated source: seed_000
25-sample curated windows: 42
```

Conclusion:

```text
This probe closes the joint-lift hypothesis for the current primitive family:
larger/narrower knee lift does not produce enough real foot clearance or
contact-state diversity on seed2. The next target generator should operate on
measured foot-site clearance/contact timing, or use a different reference/IK
primitive, rather than adding more knee-lift amplitude.
```

### Dynamic Hip-Roll Target Source

The target primitive generator was extended with default-off dynamic hip-roll
controls:

```text
new flags: --hip-roll-amps, --hip-roll-phase-offsets
default behavior: unchanged when hip-roll amplitude is 0
```

Broad dynamic-roll search result:

```text
tool: tools/search_low_command_target_primitives.py
command: x=0.04
duration: 4 s
seeds: 0,2
candidates: 72
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust same-mode modes: 0
50-sample curation: PASS_CURATED_DATASET_SEED_READY
50-sample curated windows: 42
curated source files: 2
curated modes: 36
```

Best same-mode near pass:

```text
mode: primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65

seed_000:
  mean vx: 0.0413 m/s
  vy p95: 0.1234 m/s
  contact dominance: 92%
  contact transitions: 3
  failure: high_lateral_velocity

seed_002:
  mean vx: 0.0417 m/s
  vy p95: 0.1110 m/s
  contact dominance: 94%
  contact transitions: 4
  failures: none
```

Focused refinement around the near-pass did not improve the target source:

```text
refine objective score: HOLD_NO_SEED_ROBUST_TARGETS
refine 50-sample curation: HOLD_INSUFFICIENT_CURATED_WINDOWS
refine 50-sample curated windows: 3
refine 25-sample curation: PASS_CURATED_DATASET_SEED_READY
refine 25-sample curated windows: 207
```

Conclusion:

```text
Dynamic hip-roll is the strongest current generated target-source family and
the first to produce 50-sample curated windows from both seed_000 and seed_002.
It is still not training permission under the strict same-mode gate. The next
offline target search should stay broad in the dynamic-roll family and reduce
seed_000 lateral velocity by a small amount while preserving seed_000 forward
motion and seed_002 contact transitions.
```

Updated audit:

```text
outputs/analysis/TARGET_SOURCE_AUDIT.md
status: HOLD_NO_TARGET_SOURCE_READY
training_permission: false
```

### Dynamic Hip-Roll Lateral-Fix Pass

The next bounded CPU search stayed in the dynamic-roll family and directly
targeted the seed_000 lateral miss.

Result:

```text
tool: tools/search_low_command_target_primitives.py
command: x=0.04
duration: 4 s
seeds: 0,2
candidates: 160
objective score: PASS_SEED_ROBUST_TARGETS
robust objective modes: 2
50-sample curation: PASS_CURATED_DATASET_SEED_READY
50-sample curated windows: 70
curated source files: 2
curated modes: 63
seed robustness audit: PASS_SEED_ROBUST_TARGETS
robust curated modes: 3
```

Best objective-scored robust mode:

```text
mode: primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55

seed_000:
  mean vx: 0.0416 m/s
  vy p95: 0.0716 m/s
  contact dominance: 90%
  contact transitions: 3
  failures: none

seed_002:
  mean vx: 0.0437 m/s
  vy p95: 0.0736 m/s
  contact dominance: 94%
  contact transitions: 4
  failures: none
```

Updated audit:

```text
outputs/analysis/TARGET_SOURCE_AUDIT.md
status: PASS_TARGET_SOURCE_READY
offline_imitation_smoke_permission: true
full_training_permission: false
robot_validation_permission: false
```

Conclusion:

```text
The target-source layer is now unblocked. The next safe milestone is a small
offline imitation/BC smoke using the dynamic-roll lateral-fix curated windows,
followed by closed-loop replay at x=0.04. Robot validation remains blocked.
```

### Dynamic-Roll Lateral-Fix BC Smoke

Two one-step behavior-cloning smokes were run from the lateral-fix target
windows:

```text
full manifest:
  dataset_id: 0ff1f1c3750dbfb1
  entries: 70
  samples: 3500
  source skew: seed_000=60, seed_002=10

robust-mode-only manifest:
  dataset_id: 47153f26ab48ef14
  entries: 9
  samples: 450
  source skew warning: false
```

Closed-loop replay results:

```text
full manifest linear:
  status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
  seed_000 vx: 0.0009 m/s
  seed_002 vx: 0.0037 m/s

full manifest KNN:
  status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
  seed_000 vx: 0.0064 m/s
  seed_002 vx: 0.0084 m/s

robust-mode KNN:
  status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
  seed_000 vx: 0.0070 m/s
  seed_002 vx: 0.0097 m/s

robust-mode linear:
  status: HOLD_BC_REPLAY_TERMINATED
  seed_000: terminated at 73 samples, vx=-0.2415 m/s
  seed_002 vx: -0.0041 m/s
```

Conclusion:

```text
The dynamic-roll lateral-fix targets are valid source evidence, but direct
one-step obs[101] -> action[14] cloning does not preserve the gait in
closed-loop replay. The next offline learner should be sequence-aware or
rollout-preserving, with phase/time continuity treated as part of the target.
Full PPO and robot validation remain blocked.
```

### Dynamic-Roll Lateral-Fix Sequence Replay Smoke

A sequence-preserving replay smoke was added after one-step BC failed. It uses
the robust lateral-fix target manifest, replays each trace's startup prefix, and
then loops the curated 50-tick target window in closed-loop CPU sim.

Artifacts:

```text
tools/run_target_sequence_replay_smoke.py
outputs/analysis/TARGET_SEQUENCE_REPLAY_SMOKE_1P2S.md
outputs/analysis/target_sequence_replay_smoke_1p2s.json
outputs/analysis/TARGET_SEQUENCE_REPLAY_SMOKE.md
outputs/analysis/target_sequence_replay_smoke.json
```

Results:

```text
1.2 s sequence replay:
  status: HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE
  aggregate seed_000 vx: 0.0309 m/s
  aggregate seed_002 vx: 0.0363 m/s
  aggregate seed_000 vy95: 0.1183 m/s
  aggregate seed_002 vy95: 0.1466 m/s
  aggregate seed_000 pitch95: 0.2967 rad
  aggregate seed_002 pitch95: 0.2521 rad
  aggregate sent target velocity p95: 0.3668 rad/s

3.0 s sequence replay:
  status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  aggregate seed_000 vx: 0.0117 m/s
  aggregate seed_002 vx: 0.0138 m/s
  aggregate seed_000 vy95: 0.0645 m/s
  aggregate seed_002 vy95: 0.0499 m/s
  aggregate sent target velocity p95: 0.3658 rad/s

3.0 s aggregate replay with periodic seam correction:
  status: HOLD_SEQUENCE_REPLAY_TERMINATED
  seed_000: terminated at 85 ticks, vx=0.1812 m/s, pitch95=1.1645 rad
  seed_002: completed, vx=0.0194 m/s, pitch95=0.3589 rad
```

Conclusion:

```text
The robust target tables contain a short-horizon forward-motion sequence, but
they are not yet a stable reusable gait. Timing preservation improves over
one-step BC, yet the short horizon still misses lateral/pitch gates and the
looped 3 s replay loses forward progress. A simple linear seam correction is
not sufficient and causes a seed0 lunge/fall. Do not launch PPO or robot
validation from these tables as-is. The next offline step should explicitly
solve phase continuation/contact timing in closed loop before any larger
training run.
```

Next planning artifact:

```text
docs/PHASE_CONTINUATION_ADAPTER_PLAN.md
```

### Phase Continuation Adapter Smoke

Default-off phase/contact adapters were implemented and tested on the aggregate
robust target table:

```text
contact_hold:
  status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  seed_000 / seed_002 vx: 0.0119 / 0.0138 m/s
  seed_000 / seed_002 contact mismatch: 2.76% / 0.00%

contact_match:
  status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  seed_000 / seed_002 vx: 0.0117 / 0.0138 m/s
  seed_000 / seed_002 contact mismatch: 2.76% / 0.00%

state_match:
  status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  seed_000 / seed_002 vx: 0.0117 / 0.0138 m/s
  seed_000 / seed_002 contact mismatch: 2.76% / 0.00%
```

Conclusion:

```text
The aggregate target table is not failing primarily because the contact phase
selector cannot find the right foot-contact state; contact mismatch is already
low. Contact/phase adapters do not recover forward progress. The current short
target tables should remain evidence, not PPO/BC labels. The next offline work
should either generate a longer self-consistent low-command target trajectory or
use the short fragment as a soft prior inside a closed-loop objective.
```

### Sustained Target Generation Probe

The existing dynamic-roll lateral-fix traces and a new bounded sustained-motion
primitive search were checked for longer target windows.

Existing lateral-fix trace set:

```text
100-sample objective: HOLD_NO_SEED_ROBUST_TARGETS, robust_mode_count=0
100-sample curation: HOLD_INSUFFICIENT_CURATED_WINDOWS, curated=0
150-sample objective: HOLD_NO_SEED_ROBUST_TARGETS, robust_mode_count=0
150-sample curation: HOLD_INSUFFICIENT_CURATED_WINDOWS, curated=0
```

New sustained probe:

```text
candidates: 180
seeds: 0,2
duration: 4.0 s
100-sample objective: HOLD_NO_SEED_ROBUST_TARGETS, robust_mode_count=0
100-sample curation: HOLD_INSUFFICIENT_CURATED_WINDOWS, curated=0
150-sample objective: HOLD_NO_SEED_ROBUST_TARGETS, robust_mode_count=0
150-sample curation: HOLD_INSUFFICIENT_CURATED_WINDOWS, curated=0
```

Top failure reasons:

```text
100-sample sustained probe:
  low_forward_velocity: 304
  low_base_height: 162
  single_contact_pattern_dominates: 110
  high_body_pitch: 65

150-sample sustained probe:
  low_forward_velocity: 301
  single_contact_pattern_dominates: 256
  low_base_height: 146
  high_body_pitch: 34
```

Conclusion:

```text
The current primitive target family is exhausted as direct target-label source
material. It can produce short in-envelope motion fragments, but not a robust
100-150 sample low-command gait. Do not launch PPO/BC from these targets. The
next offline branch should either change the generator structure or use the
short fragments as soft priors in a closed-loop learner/objective.
```

### Soft-Prior Closed-Loop Learner Plan

The next branch is constrained by:

```text
docs/SOFT_PRIOR_CLOSED_LOOP_LEARNER_PLAN.md
```

Decision:

```text
The target tables are no longer direct action labels.
They may only be used as weak gait-shape priors inside closed-loop sim.
```

Before any new BC/PPO/A100 training run, the project needs:

```text
PASS_SOFT_PRIOR_SMOKE
```

Hold conditions remain:

```text
freeze
lunge
lateral instability
single-contact lock
target-velocity envelope violation
```

Robot validation remains blocked.

The first compact fragment-prior config is ready:

```text
tool: tools/build_soft_prior_fragment_config.py
status: PASS_SOFT_PRIOR_CONFIG_READY
entries: 9
source_files: 2
source_mode_pairs: 6
window_len: 50
max pitch-chain target velocity p95: 2.4428 rad/s
```

Artifacts:

```text
outputs/analysis/SOFT_PRIOR_FRAGMENT_CONFIG.md
outputs/analysis/soft_prior_fragment_config.json
```

Next offline target: implement a default-off `PASS_SOFT_PRIOR_SMOKE` evaluator.

The first prior-only smoke now holds:

```text
1.2 s: HOLD_SOFT_PRIOR_LATERAL_UNSTABLE
  seed0 vx=0.0325 m/s
  seed2 vx=0.0414 m/s

3.0 s: HOLD_SOFT_PRIOR_FREEZE
  seed0 vx=0.0115 m/s
  seed2 vx=0.0143 m/s
```

Artifacts:

```text
outputs/analysis/SOFT_PRIOR_SMOKE_1P2S.md
outputs/analysis/soft_prior_smoke_1p2s.json
outputs/analysis/SOFT_PRIOR_SMOKE.md
outputs/analysis/soft_prior_smoke.json
```

Conclusion:

```text
The prior can produce short forward motion, but it is not sufficient as a
standalone controller or hard target. Use it only as a weak closed-loop
auxiliary term.
```

Next cross-repo patch spec:

```text
docs/SOFT_PRIOR_TRAINING_PATCH_SPEC.md
```

Patch helper:

```text
tools/prepare_training_soft_prior_patch.py
```

Review artifact:

```text
outputs/analysis/SOFT_PRIOR_TRAINING_PATCH.diff
```

The helper is read-only by default and validated against the current sibling
Playground checkout with `PASS_PATCH_PREPARED`.

The default-off soft-prior Playground patch has now been applied and pushed:

```text
repo: RobVanProd/Open_Duck_Playground
branch: codex/forward-progress-reward
pr: https://github.com/RobVanProd/Open_Duck_Playground/pull/4
commit: 11ebae1 training: add default-off soft prior reward
```

Verification:

```text
outputs/analysis/SOFT_PRIOR_PLAYGROUND_PATCH_VERIFY.md
```

The patched runner exposes the soft-prior flags and loads the compact prior
without training while preserving the `101` observation / `14` action contract.
No robot tests, SSH, deployment, runtime behavior changes, policy changes, or
training runs were performed for this patch application.

### V21 Weak Soft-Prior Learner Prepared

The next bounded offline training recipe is now prepared:

```text
recipe: movement_bootstrap_v21
doc: docs/SOFT_PRIOR_LEARNER_V21_PLAN.md
plan_md: outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V21.md
plan_json: outputs/analysis/staged_curriculum_training_plan_v21.json
```

Purpose:

```text
Use the short curated pitch-chain fragments only as a weak closed-loop
auxiliary prior while PPO still earns real forward progress, posture, contact,
and survival reward.
```

V21 is explicit-only and does not change the current `movement_bootstrap_v20`
default in the Colab workflow. The next allowed gate is a multi-seed x=0.04
sim result. Robot validation, x=0.08, deployment, and policy changes remain
blocked.

A tiny local CPU smoke verified the patched soft-prior training path:

```text
outputs/analysis/SOFT_PRIOR_CPU_SMOKE.md
status: PASS_SOFT_PRIOR_CPU_SMOKE
```

This was a 16-timestep CPU-forced smoke only. It did not produce a deployable
candidate and did not touch the robot.

V21 launch readiness is now captured:

```text
tool: tools/check_v21_launch_readiness.py
artifact: outputs/analysis/V21_LAUNCH_READINESS.md
json: outputs/analysis/v21_launch_readiness.json
status: HOLD_COLAB_SESSION_MISSING
```

The preflight confirms the local V21 plan, compact soft-prior config,
Playground patch, and PR checks are ready. The only current launch blocker is
that `google-colab-cli` reports no active `open-duck-l4` session.

A tiny planner-level CPU smoke now verifies the full staged planner path for
V21, not just the lower-level wrapper:

```text
artifact: outputs/analysis/V21_PLANNER_CPU_SMOKE.md
status: PASS_V21_PLANNER_CPU_SMOKE
```

The planner invoked phase 1 with `--enable-soft-prior`, the wrapper resolved
the compact prior to an absolute path before entering the sibling Playground
checkout, and the Playground runner completed a 22-timestep CPU smoke. The
generated checkpoint/ONNX stayed under `/tmp` and is not a candidate.

The next required result remains unchanged: a real CUDA/Colab V21 run followed
by an `x=0.04` multi-seed sim gate. Do not run `x=0.08`, fitted-bridge
expansion, grounded replay, deployment, or robot validation from this smoke.

Manual browser-Colab fallback is now available when `google-colab-cli` cannot
see a live session:

```bash
python3 tools/print_cuda_colab_cell.py \
  --staged-curriculum-v21 \
  --rdk-branch codex/colab-cli-cuda-workflow \
  --playground-branch codex/forward-progress-reward \
  --handoff-dir /home/lsd/robots/cuda_colab_handoff_v21
```

This generates a one-code-cell V21 staged-curriculum notebook outside the repo
for a manually authenticated Colab session. It does not approve robot testing.

The CUDA artifact importer now recognizes staged-curriculum bundles directly.
For V21 it reports `READY_FOR_STAGED_GATE_REVIEW`, the specific staged phase
gate `HOLD_*` status, `INFO_STAGED_RUN_NO_PHASE_GATE`, or `HOLD_STAGED_NO_ONNX`
instead of falling through to the old candidate-package-only review path.

Local ROCm was rechecked after the firmware/BIOS update:

```text
tool: tools/check_local_rocm_status.py
artifact: outputs/analysis/LOCAL_ROCM_STATUS_20260625.md
json: outputs/analysis/local_rocm_status_20260625.json
status: HOLD_LOCAL_ROCM_KFD
```

`rocm-smi` sees AMD devices, but `rocminfo` fails with `/dev/kfd` `Invalid
argument`, JAX reports no visible ROCm devices, and kernel logs show a recent
amdgpu reset failure. This is below Open Duck code. Do not use local ROCm for
training until `rocminfo` and a minimal JAX device probe pass. CUDA/Colab
remains the practical V21 path.

V21 was then launched on a Colab L4 session after the CLI path became
available. The first launch exposed a packaging bug: the Colab tarball did not
include the tracked compact soft-prior config. That was fixed by adding
`outputs/analysis/soft_prior_fragment_config.json` and its markdown summary to
the Colab upload allowlist.

The corrected V21 L4 run trained phase 1 and reached the required x=0.04
vanilla multi-seed gate:

```text
artifact: outputs/analysis/V21_L4_RESULT_SUMMARY.md
status: HOLD_PHASE_MULTI_SEED_FALLS
recipe: movement_bootstrap_v21
phase: phase1_soft_prior_low_command_probe
seeds: 0-3
falls: 4/4
duration_complete: 0/4
samples_mean: 61.0
mean_local_vx: -0.0242 m/s
track_ratio_mean: -0.6058
```

The soft-prior path is wired and trainable, but this weak soft-prior recipe did
not solve low-command discovery. Phase 2 is blocked. No robot validation,
deployment, x=0.08 expansion, or fitted-bridge progression is approved from
this result.

This V21 failure is not an actuator-envelope violation: the failed gate showed
`0%` action saturation and sent pitch-chain target velocity p95 below
`0.67 rad/s`. The remaining blocker is low-command behavior
discovery/stability, not target velocity.

CPU trace replays of the final V21 phase-1 ONNX for seeds 0-3 sharpened that
diagnosis:

```text
artifact: outputs/analysis/V21_TRACE_SET_SUMMARY.md
status: HOLD_TRACE_SET_LOW_COMMAND_FAILURES
failure_surfaces:
  LOW_PROGRESS_TERMINATION: 3
  REVERSE_HEIGHT_COLLAPSE: 1
track_ratio_mean: -0.6216
mean_local_vx: -0.0249 m/s
action_saturation_pct_mean: 0.0
soft_prior_abs_error_mean: 0.2609
```

V21 therefore did not discover a coherent low-command forward behavior. The next
offline work should address behavior discovery or imitation/reference locking
directly. The exported policy remained far from the soft-prior pitch-chain
actions, so simply keeping a weak soft-prior cost is not enough. Do not continue
actuator-envelope tuning, and do not authorize robot validation from this result.

### V22 Strong Step-Prior Lock Diagnostic Prepared

V22 is now prepared as an explicit-only follow-up to the V21 trace result:

```text
recipe: movement_bootstrap_v22
doc: docs/SOFT_PRIOR_LOCKING_V22_PLAN.md
plan_md: outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V22.md
plan_json: outputs/analysis/staged_curriculum_training_plan_v22.json
default recipe changed: no
```

V22 keeps the task deliberately narrow: vanilla dynamics, `x=0.035-0.045`, no
bridge, no `x=0.08`, and a stronger step-phased prior lock. The purpose is not
to produce a robot candidate. It tests whether PPO can be held near the curated
low-command pitch-chain gait basin at all.

Required post-run gates:

```text
behavior gate:
  coherent positive x=0.04 motion across seeds
  no reverse seed
  no low-progress termination distribution
  no height-collapse seed

prior-lock gate:
  trace soft_prior_abs_error_mean materially below V21's 0.2609
  <0.12 preferred
  <0.18 useful but still a hold for robot validation
```

If V22 does not materially reduce prior distance, the next branch should move
away from soft reward shaping toward explicit supervised pretraining, behavior
cloning, or a stronger imitation mechanism. Robot motion remains blocked.

### V22 A100 Partial Run

The first A100 V22 launch was not a valid full V22 verdict. It reached an
intermediate checkpoint/ONNX export, then the remote driver disappeared without
an exit sentinel or artifact bundle. The partial checkpoint was recovered and
evaluated only as diagnostic evidence:

```text
partial_policy: 2026_06_25_102301_61440.onnx
checkpoint_step: 61440
bundle_sha256: 7d6a918fcbc7730666a880b5f31a8f497c1aba15006c9e042a278c132499ce79
seed_sweep: outputs/analysis/V22_PARTIAL_SEED_SWEEP.md
trace_summary: outputs/analysis/V22_PARTIAL_TRACE_SET_SUMMARY.md
status: HOLD_TRACE_SET_LOW_COMMAND_FAILURES
falls_or_terminations: 4/4
track_ratio_mean: -0.6618
mean_local_vx: -0.0265 m/s
soft_prior_abs_error_mean: 0.2711
```

The partial checkpoint did not show evidence that the stronger prior was
locking the exported policy into the curated gait basin by step 61,440. Its
prior distance was slightly worse than V21's `0.2609`, with the same broad
failure surfaces:

```text
LOW_PROGRESS_TERMINATION: 3
REVERSE_HEIGHT_COLLAPSE: 1
```

This is not enough to reject V22 as a full recipe, but it is enough to preserve
the failure evidence and avoid treating the partial checkpoint as a candidate.
The remote output also revealed a tooling issue: retries in the same Colab
session shared `/content/open_duck_staged_curriculum_cli`, which mixed partial
outputs. The Colab workflow was patched to use a unique staged output directory
per run before any further V22 launch.

A clean rerun on a fresh A100 session with the unique remote output root and
lazy TensorFlow export patch did not produce a V22 verdict:

```text
artifact: outputs/analysis/V22_A100_CLEAN_FAILED_RUN.md
status: HOLD_A100_BACKEND_NO_SENTINEL
checkpoint produced: no
onnx produced: no
first PPO progress line: no
bundle_sha256: 1508c95113d7bd0f82af4298527b5eb7911261d317fd2348c427afc5ad56479d
```

The clean failed run reached environment construction and PPO configuration,
then disappeared before the first checkpoint or progress line. Treat this as a
cloud/backend failure, not a policy result. The next clean V22 attempt should
use either the previously reliable L4 path, a shorter diagnostic first, or
stronger automatic no-sentinel recovery.

### Contact Weight-Transfer Discriminator

The contact-mismatch hypothesis was re-read against the existing target-source
and replay artifacts before launching another training run:

```text
artifact: outputs/analysis/CONTACT_WEIGHT_TRANSFER_DISCRIMINATOR.md
status: HOLD_CONTACT_NOT_BINARY_MISMATCH_ONLY
```

The raw polynomial reference path still has a real contact incompatibility:

```text
raw/projected reference contact mismatch: about 67-68%
actual double support: about 74-76%
reference double support: about 35-38%
```

But the later dynamic-roll lateral-fix path already shows low binary contact
mismatch in closed-loop sequence replay:

```text
contact_hold/contact_match/state_match replay mismatch:
  seed_000: 2.76%
  seed_002: 0.00%

contact_match replay vx:
  seed_000: 0.0117 m/s
  seed_002: 0.0138 m/s
```

So the current best short fragment path is not failing because the phase adapter
cannot find the requested binary foot-contact state. Binary contact matching is
already mostly achieved, but forward progress remains low and pitch stays
near/over gate. The sharper blocker is sustained weight transfer: the current
short fragments contain useful in-envelope evidence, but they do not yet provide
a reusable 100-150 tick target or closed-loop objective that makes the body keep
moving forward while transferring support.

Next branch:

```text
do not launch another prior-scale-only V22-style run
build or run a bounded PASS_WEIGHT_TRANSFER_TARGET gate first
optimize for sustained support transitions + forward progress + pitch/height
only then launch PPO/BC from that target
```

### Weight-Transfer Target Gate

The bounded weight-transfer gate was checked against existing 100/150-tick
dynamic-roll lateral-fix objective-score artifacts:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_TARGET_GATE.md
status: HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
```

Result:

```text
100-tick dynamic-roll lateral-fix:
  robust_mode_count: 0
  main failures: low_forward_velocity 312, single_contact_pattern_dominates 148

150-tick dynamic-roll lateral-fix:
  robust_mode_count: 0
  main failures: low_forward_velocity 312, single_contact_pattern_dominates 295

explicit weight-transfer rescore:
  100-tick double_support_dominates: 310
  100-tick too_little_single_support: 294
  150-tick double_support_dominates: 312
  150-tick too_little_single_support: 312
```

The short-window target search still contains useful evidence, but the longer
gate confirms those windows do not yet compose into a sustained low-command
weight-transfer target. The next offline task is generator/objective work, not
another V22-style prior-lock training run.

The scorer now has explicit default-off support-shape criteria
(`--max-double-support-pct`, `--min-single-support-pct`, and
`--min-each-single-support-pct`) so future target searches can gate on support
transfer directly.

A bounded CPU-only weight-transfer probe then searched 72 support-biased
primitives with larger hip-roll/lift pulses:

```text
artifact: outputs/analysis/TARGET_GENERATOR_WEIGHT_TRANSFER_PROBE.md
score_100: outputs/analysis/TARGET_OBJECTIVE_SCORE_WEIGHT_TRANSFER_PROBE_100.md
score_150: outputs/analysis/TARGET_OBJECTIVE_SCORE_WEIGHT_TRANSFER_PROBE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The probe reduced the binary support-shape problem on its top candidates, but
forward progress collapsed:

```text
100-tick top candidate:
  seed_000 / seed_002 vx: 0.0045 / 0.0043 m/s
  seed_000 / seed_002 single support: 15% / 12%

150-tick top candidate:
  seed_000 / seed_002 vx: 0.0018 / 0.0035 m/s
  seed_000 / seed_002 single support: 14% / 12%
```

This confirms that stronger roll/lift pulses alone are not the missing
generator mechanism. The next target-generation work must couple support
transfer to forward displacement, not merely increase foot unweighting.

The primitive generator was then extended with default-off stance-push
parameters:

```text
--stance-push-amps
--stance-ankle-scales
```

A bounded CPU-only stance-push probe searched 48 candidates:

```text
artifact: outputs/analysis/TARGET_GENERATOR_STANCE_PUSH_PROBE.md
score_100: outputs/analysis/TARGET_OBJECTIVE_SCORE_STANCE_PUSH_PROBE_100.md
score_150: outputs/analysis/TARGET_OBJECTIVE_SCORE_STANCE_PUSH_PROBE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The top candidates still fail low-command forward progress:

```text
100-tick top candidate:
  seed_000 / seed_002 vx: 0.0089 / 0.0108 m/s
  seed_000 / seed_002 single support: 12% / 8%

150-tick top candidate:
  seed_000 / seed_002 vx: 0.0028 / 0.0061 m/s
  seed_000 / seed_002 single support: 10% / 8.67%
```

Open-loop stance push improves the top 100-tick velocity only slightly and still
falls far short of the `0.04 m/s` gate. The next generator should be
closed-loop or phase-aware: stance push-off, body lean, and contact timing must
react to body velocity/pitch/contact state rather than be only fixed sinusoids.

A velocity-feedback stance-push term was added and tested next:

```text
tool flags:
  --velocity-push-gains
  --velocity-push-limit

artifact: outputs/analysis/TARGET_GENERATOR_VELOCITY_FEEDBACK_PROBE.md
score_100: outputs/analysis/TARGET_OBJECTIVE_SCORE_VELOCITY_FEEDBACK_PROBE_100.md
score_150: outputs/analysis/TARGET_OBJECTIVE_SCORE_VELOCITY_FEEDBACK_PROBE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

It also failed:

```text
100-tick top candidate:
  seed_000 / seed_002 vx: 0.0070 / 0.0061 m/s

150-tick top candidate:
  seed_000 / seed_002 vx: 0.0031 / 0.0058 m/s
```

Conclusion: feeding `command_x - local_vx` into the same primitive stance-push
template does not produce sustained forward locomotion. The next generator must
change structure, not only add another scalar feedback term to the sinusoid.

### Closed-Loop Weight-Transfer Teacher Plan

The next branch is now specified here:

```text
docs/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_PLAN.md
```

This locks the current decision:

```text
do not launch another V22-style prior-scale run
do not extend the open-loop sinusoid grid with more scalar terms
do not train from the current short fragments
```

The next offline experiment should build a state-feedback teacher probe that
uses sim state directly:

```text
local_vx / local_vy
body pitch and base height
left/right foot contacts
support-side dwell
swing-side clearance
stance push and pitch damping
```

The required first result is either:

```text
PASS_WEIGHT_TRANSFER_TEACHER_PROBE
```

or a useful hold that identifies the next limiting mechanism:

```text
HOLD_FORWARD_STILL_LOW
HOLD_SUPPORT_TRANSFER_FAILED
HOLD_PITCH_OR_HEIGHT_UNSTABLE
HOLD_LATERAL_UNSTABLE
HOLD_ACTUATOR_ENVELOPE
```

Robot validation, deployment, PPO/BC, and `x=0.08` remain blocked.

The first implementation of that probe was added and run locally on CPU:

```text
tool: tools/probe_closed_loop_weight_transfer_teacher.py
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Key result:

```text
top aggregate rollout mean vx: 0.0232 m/s
best scored 100-tick seed2 vx: 0.0050 m/s
best scored 150-tick seed2 vx: 0.0047 m/s
100/150 robust modes: 0
dominant failures: low_forward_velocity and high_lateral_velocity
```

This is useful negative evidence. A state-feedback teacher can increase raw
forward motion and contact transitions compared with the open-loop primitive
probes, but the first version pays for that with lateral motion and still does
not produce a sustained seed-robust target. The next teacher revision should
separate lateral load shift from forward push and add explicit local-y/CoM
centering before any learner or A100 run.

That revision was implemented as v2 with body-y centering and lateral-speed
push gating:

```text
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

V2 result:

```text
top aggregate rollout mean vx: 0.0305 m/s
100/150 robust modes: 0
best scored 100-tick vx: -0.0006 / 0.0002 m/s
best scored 150-tick vx: 0.0003 / 0.0011 m/s
```

The tradeoff is now clearer: candidates that move toward the target forward
speed fail lateral velocity; candidates that satisfy lateral velocity lose
forward displacement. The next generator should move beyond hip-roll/stance
push feedback and add explicit foot-placement or CoM/step-geometry planning.

V3 added that first explicit step-geometry layer:

```text
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

```text
top aggregate rollout mean vx: 0.0337 m/s
100/150 robust modes: 0
top scored 100-tick vx: 0.0104 / 0.0155 m/s
top scored 100-tick vy95: 0.1371 / 0.1341 m/s
```

V3 is closer in raw forward velocity, but still not a target source. It shows
that foot-placement terms alone do not decouple forward motion from lateral
impulse. The next useful generator should be a staged balance-then-step planner
or offline optimizer, not another random sweep of the same teacher terms.

The staged balance-then-step branch was tested next:

```text
tool: tools/probe_staged_weight_transfer_planner.py
artifact: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_PROBE.md
score_100: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_SCORE_100.md
score_150: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The best 100-tick candidate stayed within the lateral gate
(`vy95 = 0.1149 / 0.1197 m/s`) and preserved some single support
(`11% / 15%`), but forward velocity collapsed to `0.0015 / 0.0034 m/s`. This
confirms the tradeoff: aggressive teacher terms create forward impulse with too
much lateral motion, while staged gates control lateral motion by suppressing
forward displacement. The next target-source path should be short-horizon
trajectory optimization or a richer body-state planner.

The optimizer branch is specified in:

```text
docs/WEIGHT_TRANSFER_OPTIMIZER_PLAN.md
```

The purpose is to stop expanding hand-shaped random grids and instead search
the short-horizon tradeoff directly with the simulator in the loop. Training
remains blocked until an optimized target source passes seed-robust 100/150
tick gates.

A first tiny optimizer implementation/run was added:

```text
tool: tools/optimize_weight_transfer_target_sequence.py
artifact: outputs/analysis/WEIGHT_TRANSFER_OPTIMIZER.md
status: HOLD_OPTIMIZER_NO_ROBUST_TARGET
```

It validates the optimizer plumbing but not a target source. The global best
candidate still had near-zero forward velocity (`-0.0029 / 0.0022 m/s`) while
staying close to the lateral gate (`vy95 = 0.1096 / 0.1113 m/s`). This confirms
that the first optimizer parameterization is still trapped in the conservative
balance basin.

A gate-mode extension then let the optimizer sample hard, soft, and ungated
step phases:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_OPTIMIZER_GATE_MODE.md
status: HOLD_OPTIMIZER_NO_ROBUST_TARGET
```

This also held. The global best soft-gated candidate had seed0/seed2 forward
velocity of `-0.0036 / 0.0043 m/s` with lateral velocity still near gate. This
shows that relaxing the step gate alone does not escape the conservative basin.

The scorer was then extended with optional local-frame displacement terms and a
small displacement-weighted optimizer probe was run:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_OPTIMIZER_DISPLACEMENT.md
status: HOLD_OPTIMIZER_NO_ROBUST_TARGET
```

All sampled candidates failed the forward-displacement gate. After correcting
the metric to integrated local `vx`, the best candidate had seed0/seed2
displacement of `-0.0070 / 0.0030 m`, so the current compact
planner/optimizer parameterization is not producing an actionable target
source.

The closed-loop teacher was then extended with minimum forward scale and
feed-forward push:

```text
tool flags:
  --min-forward-scales
  --feedforward-pushes

artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_FORWARD_INTENT.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_FORWARD_INTENT_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_FORWARD_INTENT_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

This did produce local-frame forward displacement: the top 100-tick scored
window reached `0.0518 / 0.0420 m` on seeds `0 / 2`, and the top 150-tick
window reached `0.0757 / 0.0648 m`. But both windows failed lateral velocity
badly (`vy95` around `0.19-0.26 m/s`). This is the cleanest statement of the
current target-source blocker: forward displacement exists, but remains coupled
to lateral impulse.

### Lateral-Refined Forward-Intent Teacher

A focused CPU-only lateral-refine search tested whether stronger lateral/body-y
feedback and push gating could preserve the forward-intent branch while
bringing lateral velocity back inside gate:

```text
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

```text
100-tick robust modes: 0
150-tick robust modes: 0

top scored 100-tick seed0 / seed2:
  vx: 0.0131 / 0.0186 m/s
  local dx: 0.0261 / 0.0371 m
  vy95: 0.1270 / 0.1093 m/s

top scored 150-tick seed0 / seed2:
  vx: 0.0137 / 0.0124 m/s
  local dx: 0.0411 / 0.0372 m
  vy95: 0.1562 / 0.1650 m/s
```

The highest-displacement individual windows still exceeded the lateral gate:

```text
100 ticks: dx 0.0850 m, vy95 0.3083 m/s
150 ticks: dx 0.0912 m, vy95 0.2634 m/s
```

This confirms the target-source Pareto surface:

```text
enough forward displacement -> lateral impulse too high
lateral/contact gates -> too little forward displacement / too much double support
```

Do not launch another nearby teacher-grid or prior-scale run as the next main
step. The next useful offline branch must change the contact/weight-transfer
objective or controller structure so single-support alternation, lateral
momentum control, and forward displacement are optimized together over
100-150 ticks. Robot motion and training remain blocked until a target source
passes that gate.

Compact handoff docs for the current state:

```text
docs/SIM2REAL_FINDINGS_DIGEST.md
docs/WEIGHT_TRANSFER_OBJECTIVE_BRIEF.md
```

### Support-State Weight-Transfer Probe

The teacher tool now supports a default-off contact-reactive mode:

```text
tool: tools/probe_closed_loop_weight_transfer_teacher.py
flag: --support-state-modes
mode 1: use actual single-foot contact as stance side, phase fallback in double/no support
```

A bounded CPU probe tested mode `1` over seeds `0,2`:

```text
artifact: outputs/analysis/SUPPORT_STATE_WEIGHT_TRANSFER_PROBE.md
score_100: outputs/analysis/SUPPORT_STATE_WEIGHT_TRANSFER_PROBE_SCORE_100.md
score_150: outputs/analysis/SUPPORT_STATE_WEIGHT_TRANSFER_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Top scored windows:

```text
100 ticks:
  vx: 0.0137 / 0.0115 m/s
  local dx: 0.0273 / 0.0230 m
  vy95: 0.1479 / 0.1483 m/s
  contact transitions: 16 / 20

150 ticks:
  vx: 0.0102 / 0.0103 m/s
  local dx: 0.0306 / 0.0309 m
  vy95: 0.1548 / 0.1635 m/s
  contact transitions: 19 / 25
```

This confirms that reacting to actual single-foot support improves contact
alternation but does not solve the weight-transfer target. The next controller
needs explicit center-of-mass/lateral momentum and stance-foot loading logic,
not just contact-state stance selection.

### Support-Loaded Push Probe

The teacher tool now also supports a default-off stance-loading hook:

```text
flag: --single-support-push-scales
scale 0: historical stance push
scale 1: only push while actual single support is loaded
```

A bounded CPU probe tested scales `0`, `0.5`, and `1.0`:

```text
artifact: outputs/analysis/SUPPORT_LOADED_WEIGHT_TRANSFER_PROBE.md
score_100: outputs/analysis/SUPPORT_LOADED_WEIGHT_TRANSFER_PROBE_SCORE_100.md
score_150: outputs/analysis/SUPPORT_LOADED_WEIGHT_TRANSFER_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Best scored windows:

```text
100 ticks:
  scale: 0.5
  vx: 0.0115 / 0.0129 m/s
  local dx: 0.0230 / 0.0258 m
  vy95: 0.1424 / 0.1543 m/s

150 ticks:
  scale: 0.5
  vx: 0.0103 / 0.0121 m/s
  local dx: 0.0309 / 0.0362 m
  vy95: 0.1586 / 0.1635 m/s
```

Support-loaded push slightly improves support dwell, but it still misses the
forward displacement gate and fails lateral velocity. The controller must
actively place/regulate the body over the stance foot rather than only wait for
single support before pushing.

The next implementation plan is:

```text
docs/COM_WEIGHT_TRANSFER_CONTROLLER_PLAN.md
```

### CoM Weight-Transfer Controller Probe

The first CoM-style controller probe was implemented:

```text
tool: tools/probe_com_weight_transfer_controller.py
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_PROBE.md
score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_PROBE_SCORE_100.md
score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

It uses available proxy state (`base_y`, `local_vy`, contact state, pitch, and
height) and logs controller phases:

```text
LOAD_STANCE
UNWEIGHT_SWING
PUSH_FORWARD
```

Strict gate result:

```text
push_allowed_mean: about 0.67%
top 100-tick local dx: 0.0074 / 0.0132 m
top 100-tick vy95: 0.0591 / 0.0937 m/s
dominant hold: LOAD_STANCE rarely reaches PUSH_FORWARD
```

A relaxed-gate run widened base-y and lateral-velocity gates:

```text
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_RELAXED_PROBE.md
score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_RELAXED_PROBE_SCORE_100.md
score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_RELAXED_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Relaxed result:

```text
push_allowed_mean: about 2.67%
top 100-tick local dx: 0.0088 / 0.0121 m
top 100-tick vy95: 0.0621 / 0.0768 m/s
dominant hold: low forward displacement and double-support dominance
```

This is useful negative evidence. The first CoM proxy controller controls
lateral velocity better than the forward-intent teachers, but does so by being
too conservative.

The follow-up stance-foot-relative controller regulated:

```text
lateral_control_y = base_y - stance_foot_site_y
```

Stance-relative result:

```text
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_PROBE.md
score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_PROBE_SCORE_100.md
score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
top 100-tick local dx: 0.0145 / 0.0129 m
top 100-tick vy95: 0.0568 / 0.0585 m/s
top 100-tick double support: 89% / 87%
```

Aggressive stance-relative push improved the short-window displacement but
still did not pass:

```text
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_AGGRESSIVE_PROBE.md
score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_AGGRESSIVE_PROBE_SCORE_100.md
score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_AGGRESSIVE_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
top 100-tick local dx: 0.0254 / 0.0209 m
top 100-tick vy95: 0.0926 / 0.0960 m/s
top 100-tick double support: 79% / 79%
```

A reverse-push sign check was negative:

```text
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_REVERSE_PUSH_PROBE.md
score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_REVERSE_PUSH_PROBE_SCORE_100.md
score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_REVERSE_PUSH_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
top 100-tick local dx: 0.0209 / 0.0218 m
```

A sagittal stance-foot-relative push-off probe also held:

```text
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SAGITTAL_PROBE.md
score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SAGITTAL_PROBE_SCORE_100.md
score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SAGITTAL_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
top 100-tick local dx: 0.0209 / 0.0208 m
top 100-tick vy95: 0.0913 / 0.0865 m/s
top 150-tick local dx: 0.0012 / 0.0134 m
```

This is now sharper negative evidence. Stance-foot-relative lateral control
reduces the earlier lateral/contact failure and can produce cleaner
single-support windows, but the generated forward impulse is still too small
and not sustained over 150 ticks. The tested sagittal body-over-stance-foot and
ankle push-off terms do not close the gap. The next offline step should be a
different higher-level controller/reference design rather than another nearby
lateral gate, prior-scale, or push-sign sweep.

### Contact-Timed Reference Snippet Plan

The next structural target-source branch is now specified in:

```text
docs/CONTACT_TIMED_REFERENCE_SNIPPETS_PLAN.md
```

Goal:

```text
preserve useful dynamic-roll contact timing from 50-tick curated fragments,
but regenerate longer envelope-aware target snippets and score them over
100-150 ticks.
```

This is the correct next offline branch because:

```text
dynamic-roll lateral-fix:
  best 50-tick contact/motion evidence
  not sustained

CoM/stance-relative controller:
  better contact/lateral discipline
  insufficient forward impulse
```

The plan blocks:

```text
new scalar CoM sweeps
training from 50-tick fragments
robot validation
actuator-envelope relaxation
```

until a contact-timed source passes seed-robust 100/150 tick gates.

The first-pass contact-timed audit has now run:

```text
artifact: outputs/analysis/CONTACT_TIMED_REFERENCE_SNIPPETS.md
status: HOLD_SOURCE_FRAGMENTS_DOUBLE_SUPPORT
entries: 9
pass_entries: 0
single_support_pct_mean: 7.33%
double_support_pct_mean: 92.67%
```

The replay/score follow-up also held:

```text
replay: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_REPLAY.md
score_100: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_100.md
score_150: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

This resolves the immediate ambiguity: the robust 50-tick dynamic-roll fragments
are not hidden clean single-support gaits that the policy fails to execute.
They are mostly double-support fragments. The next target-source branch must
explicitly generate single-support / weight-transfer timing before another
BC/PPO run is justified.

A bounded single-support-biased open-loop primitive probe also held:

```text
artifact: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE.md
score_100: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE_SCORE_100.md
score_150: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
best 100-tick windows:
  seed0 vx: ~0.022 m/s
  seed2 vx: ~0.027 m/s
  double support: 95-96%

best 150-tick windows:
  seed0 vx: ~0.016 m/s
  seed2 vx: ~0.019 m/s
  double support: 96.7-97.3%
```

So the missing piece is not just stronger lift pulses, roll assist, or stance
push in the existing open-loop primitive family. The next source needs a
state-aware support-transfer controller/objective that explicitly makes the
body commit weight to one stance leg before asking for swing and forward push.

A first support-readiness-gated CoM controller variant was tested by making
swing lift/reach wait until stance load and swing-clear gates were true:

```text
tool flag: --gate-swing-on-ready
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_PROBE.md
score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_SCORE_100.md
score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

This increased support-transfer discipline but froze the controller:

```text
top 100-tick scored windows:
  seed0 vx: -0.0019 m/s
  seed2 vx: 0.0009 m/s
  single support: 20-26%
  double support: 73-78%

top 150-tick scored windows:
  seed0 vx: -0.0053 m/s
  seed2 vx: 0.0002 m/s
  single support: ~20.7%
  double support: 77.3-78.7%
```

So a hard "only swing when ready" gate is not sufficient by itself. The next
controller must actively drive the body into readiness and then push; otherwise
the safe outcome is standstill/reverse drift.

Stateful support-phase variants were then tested:

```text
strict stateful:
  artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_PROBE.md
  score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_SCORE_100.md
  score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_SCORE_150.md
  status: HOLD_NO_SEED_ROBUST_TARGETS

timeout stateful:
  artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_PROBE.md
  score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_SCORE_100.md
  score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_SCORE_150.md
  status: HOLD_NO_SEED_ROBUST_TARGETS
```

Strict stateful mode sometimes reached readiness and transitioned, but not
robustly across seeds, and still produced essentially no forward progress:

```text
top strict aggregate:
  mean_vx: about -0.0007 m/s
  best seed vx: about 0.0013 m/s
  push_allowed_mean: about 0.33%
```

Timeout fallback increased phase transitions, but also failed to create useful
forward progress:

```text
top timeout aggregate:
  mean_vx: about -0.0010 m/s
  best seed vx: about 0.0012 m/s
  push_allowed_mean: about 1.33%
```

This closes the "timer flip was the only blocker" hypothesis. The controller
can hold/advance support state, but its pitch-chain stance push is not creating
propulsion. The next source needs a different propulsion/contact model, likely
explicit ankle/foot placement or a richer teacher/trajectory optimizer, not
more phase-state plumbing around the same stance push.

The current target-source branch is now explicitly held:

```text
decision: HOLD_TARGET_SOURCE_BRANCH_EXHAUSTED
doc: docs/TARGET_SOURCE_EXIT_DECISION.md
```

This is a branch decision, not a claim that walking is impossible. It means the
tested target families are no longer the highest-information next step:

```text
dynamic-roll fragments:
  short snippets exist, but they are mostly double support

open-loop lift / roll / stance-push primitives:
  remain double-support dominated and low displacement

CoM / stance-relative controllers:
  improve lateral/contact discipline, but forward displacement collapses

support-readiness and stateful phase gates:
  create more contact discipline, but freeze or drift backward
```

Do not spend the next run on another nearby scalar gate, stance-push sign,
phase-state wrapper, prior-scale change, or passive readiness gate around the
same primitive. The next offline branch should be structurally different:

```text
1. horizon-based teacher / optimizer over stance side, body placement,
   foot placement, and push,
2. explicit contact/weight-transfer objective in the learning environment, or
3. closed-loop reference generator that reacts to pitch, height, lateral
   velocity, and foot contacts.
```

A first finite-horizon random-shoot sequence optimizer was added and tested:

```text
tool: tools/optimize_contact_weight_transfer_sequence.py
artifact: outputs/analysis/CONTACT_WEIGHT_TRANSFER_SEQUENCE_OPTIMIZER.md
status: HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET
```

The tool is a structural instrument: it generates smooth target action tables,
replays them through the existing closed-loop sim path, and scores realized
contact/forward behavior. The first bounded CPU pass over six candidates also
held:

```text
robust modes: 0
best seed0 vx: 0.0020 m/s
best seed2 vx: 0.0036 m/s
dominant failures:
  low_forward_velocity
  double_support_dominates
  too_little_single_support
  single_support_not_balanced
```

This confirms the new replay/score instrument works, but it does not yet solve
the target-source problem. The next high-information branch is either a richer
horizon teacher/optimizer with explicit foot placement and support transition
state, or the contact/weight-transfer learning objective directly in the
Playground environment.

The first default-off learning-objective hook is now wired through the RDK
planner as a plan-only recipe:

```text
recipe: movement_bootstrap_v23
artifact: outputs/analysis/MOVEMENT_BOOTSTRAP_V23_SUPPORT_OBJECTIVE_PLAN.md
status: plan-only / not trained
new runner flags:
  --forward-single-support-scale
  --forward-double-support-scale
```

V23 is the explicit contact/weight-transfer branch. It removes soft-prior target
chasing and tests whether single-support reward plus double-support dwell cost
can create low-command x=0.04 weight transfer under vanilla dynamics. It does
not authorize x=0.08, fitted bridge, robot validation, deployment, or runtime
changes.

The first V23 L4 run completed training but failed the required seed gate before
the Colab runtime disappeared:

```text
artifact: outputs/analysis/V23_L4_PARTIAL_RUN_SUMMARY.md
status: HOLD_V23_SUPPORT_OBJECTIVE_FAILED_GATE
training: PASS_SMOKE_RUN
final checkpoint/ONNX step: 184320
gate command: x=0.04, vanilla bridge
observed gate seeds:
  seeds 0-5: HOLD_CANDIDATE_FALL_OR_TERMINATION
  seed 6: started, no final status captured
  seed 7: not started
remote status: HOLD_REMOTE_NO_SENTINEL
```

Because the configured pass gate allowed no failed seeds, the first six failed
seeds are already enough to hold V23 even though the full eight-seed distribution
was not captured. Do not rerun V23 unchanged. The next branch needs a more
structural support/propulsion mechanism or a targeted fall-trace analysis of the
V23 seed-0 failure.

A second L4 artifact-recovery run preserved the final V23 package and confirms
the hold:

```text
artifact: outputs/analysis/V23_L4_ARTIFACT_RECOVERY_SUMMARY.md
status: HOLD_V23_ARTIFACT_RECOVERED_GATE_FAILED
candidate sha256: d8a92162cfee07cb4c6f2643c5206a182882fd46c0098f93a1c65c03e99c86c7
package exit status: 1

x=0.0 gate:
  vanilla/fitted/stress all terminated with fall_or_nan
  samples: 71 / 55 / 66
  min base height: 0.0405 m
  max pitch tracking p95: 0.1632 rad

x=0.08 gate:
  vanilla/fitted/stress all terminated with fall_or_nan
  samples: 125 / 98 / 140
  local mean vx: -0.1429 / -0.1717 / -0.1232 m/s
  track ratio: -1.7863 / -2.1467 / -1.5405
  max sent target velocity p95: 0.6026 rad/s
  action saturation: 0%
```

This is a stronger negative result than the interrupted seed sweep alone. V23
does not fail because it exceeds the actuator envelope or saturates actions; it
fails because the explicit single-support / double-support reward hook does not
create stable support mechanics. The candidate is not promoted to a tracked
policy. Robot validation remains blocked.

A targeted CPU trace at the intended low-command gate isolates the V23 failure
mechanism:

```text
artifact: outputs/analysis/V23_SEED0_X004_TRACE_SUMMARY.md
status: HOLD_DOUBLE_SUPPORT_STANDSTILL
command: x=0.04
seed: 0
bridge: vanilla
samples: 750 / duration_complete
mean local vx: -0.0002 m/s
track ratio: -0.0051
contact states:
  01: 5 ticks / 0.67%
  11: 745 ticks / 99.33%
contact transitions: 3
longest run: double support from tick 9 through 749
```

So the support reward branch did not create weight transfer; it produced stable
double-support standstill. The next branch should force support-state transition
and propulsion together, or use a closed-loop teacher/optimizer that explicitly
chooses stance side, foot placement, body placement, and push timing.

The next explicit-only recipe is now planned:

```text
recipe: movement_bootstrap_v24
artifact: outputs/analysis/MOVEMENT_BOOTSTRAP_V24_TRANSITION_PROPULSION_PLAN.md
status: DRY_RUN / not trained
new hooks:
  forward_contact_transition
  forward_double_support_dwell
```

V24 is a structural follow-up to the V23 standstill trace. It rewards a landing
transition only when it coincides with body-frame forward progress and penalizes
prolonged forward-command double-support dwell after a short grace window. The
recipe remains offline, explicit-only, and low-command `x=0.04`; it does not
authorize robot validation or any runtime behavior change.

The first V24 L4 run completed training but failed the recovered seed gate:

```text
artifact: outputs/analysis/V24_L4_PARTIAL_RUN_SUMMARY.md
status: HOLD_V24_TRANSITION_PROPULSION_FAILED_GATE
training: PASS_SMOKE_RUN
final ONNX sha256: 84bc62cffb5972711769dc4be73c7bcfc1986795d8482cc6c0b2a976d27cbf58
gate: x=0.04, vanilla bridge
recovered seeds: 0-5
result: 6/6 HOLD_CANDIDATE_FALL_OR_TERMINATION
remote: HOLD_REMOTE_NO_SENTINEL before seeds 6-7 completed
```

The gate failure is decisive despite the incomplete 0-7 distribution because
the configured pass condition allowed no failed seeds. Recovered seeds showed
near-zero or negative local forward velocity, low target velocities, and 0%
action saturation. V24 therefore did not fail because of actuator envelope or
saturation pressure.

A follow-up reward-term activation audit found that the recovered eval reward
summaries did not expose several configured nonzero contact terms:

```text
artifact: outputs/analysis/V24_REWARD_TERM_ACTIVATION_AUDIT.md
status: HOLD_REWARD_TERMS_MISSING
missing: forward_contact_transition, forward_double_support,
         forward_double_support_dwell, forward_single_support
```

Treat the V24 behavior as a failed candidate gate, but do not claim the
transition/dwell terms were observed in the recovered eval without a trace that
contains those metrics. Before another long PPO run, fix or explain reward-term
observability for newly configured contact objectives.

The eval override allow-list issue is now fixed:

```text
artifact: outputs/analysis/V24_REWARD_OVERRIDE_ALLOWLIST_FIX.md
status: PASS_LOCAL_REWARD_TERMS_OBSERVED_AFTER_ALLOWLIST_FIX
```

The closed-loop eval runner had not been applying the V23/V24 support-contact
reward overrides even though the phase JSON recorded them. A local CPU smoke
after the patch observed the previously missing terms. Future support-contact
training must run this reward activation smoke before a long cloud job:

```text
docs/SUPPORT_REWARD_PREFLIGHT.md
```

A corrected local seed-0 V24 trace was then run with the patched eval path:

```text
artifact: outputs/analysis/V24_CORRECTED_SEED0_TRACE.md
reward audit: outputs/analysis/V24_CORRECTED_SEED0_REWARD_AUDIT.md
status: LOW_PROGRESS_TERMINATION
samples: 70
mean local vx: -0.0008 m/s
track ratio: -0.0194
contact states:
  double support: 65 / 70 ticks
  right-only support: 5 / 70 ticks
```

The corrected eval confirms the support-contact rewards are now observable, but
the V24 policy still does not perform useful support transfer or propulsion. It
terminates for low progress while remaining mostly in double support.

The next offline branch is captured in:

```text
docs/NEXT_OFFLINE_BRANCH_AFTER_V24.md
```

It explicitly blocks rerunning V24 unchanged or making another nearby scalar
contact-reward tweak. The next valid branch should be either a richer
closed-loop teacher/optimizer or a demonstration/imitation path with verified
contact/envelope compatibility.

The support reward preflight helper has been validated on the V24 plan:

```text
tool: tools/run_support_reward_preflight.py
artifact: outputs/analysis/SUPPORT_REWARD_PREFLIGHT_V24.md
status: WARN_REWARD_TERMS_ZERO
```

## Contact Transfer Blocker Audit

The cheap contact-trace split after V24 is now recorded:

```text
tool: tools/analyze_contact_transfer_blocker.py
artifact: outputs/analysis/CONTACT_TRANSFER_BLOCKER_AUDIT.md
status: HOLD_TARGET_SOURCE_DOUBLE_SUPPORT
```

The current dynamic-roll/lateral-fix target snippets do not yet prove coherent
single-support stepping:

```text
50-tick robust-mode snippets:
  double support mean/p95: 92.67% / 94.00%
  single support mean/p95: 7.33% / 11.20%
  weight-transfer-pass windows: 0

100-tick curation:
  curated windows: 0

150-tick curation:
  curated windows: 0
```

This resolves the immediate branch split. The best available snippets mostly
move forward while staying in double support, so they are not valid stepping
demonstrations for BC/PPO yet. The next offline branch should build or optimize
a target source that explicitly produces seed-robust support alternation before
training resumes:

```text
docs/WEIGHT_TRANSFER_TARGET_PLAN.md
```

A bounded finite-horizon sequence optimizer smoke was also run locally in
CPU-only mode:

```text
tool: tools/optimize_contact_weight_transfer_sequence.py
artifact: outputs/analysis/CONTACT_WEIGHT_TRANSFER_SEQUENCE_OPTIMIZER_SMOKE.md
status: HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET
seeds: 0,2
candidates: 4
window: 100 ticks
```

Best candidate still failed by support transfer and progress:

```text
seed_000: mean vx -0.0035 m/s, double support 93%, single support 7%
seed_002: mean vx  0.0038 m/s, double support 90%, single support 10%
```

This confirms that an unconditioned smooth action-table random shoot is not
enough. The next target source must encode a more structured weight-shift and
stance-transition mechanism rather than just sampling finite-horizon joint
targets.

## Deployable Warm-Start Status

The source-VX selector branch superseded the earlier morphology-wall concern:
in-envelope forward motion exists offline under the fitted actuator bridge, but
the passing selector is not deployable. The deployable path is a PPO-shaped
swish BC warm-start followed by PPO only after step-0 closed-loop stability is
cleared.

Current step-0 status:

```text
artifact: outputs/analysis/PPO_BC_SWISH_SEED5_RECOVERY_DECISION.md
status: HOLD_SEED5_RECOVERY_TRACE_RELABEL_INSUFFICIENT
```

The PPO checkpoint/ONNX export plumbing has exact action fidelity, but the
candidate still has a seed-5 reverse/fall basin. A one-trace relabel improved
local dataset coverage without removing that failure. Do not start PPO, deploy,
or run robot validation from this checkpoint.

Follow-up source-VX relabeling fixed that specific seed-5 basin:

```text
artifact: outputs/analysis/PPO_BC_SWISH_SEED5_SOURCE_VX_RECOVERY_DECISION.md
status: HOLD_COMMAND_CONDITIONING_REQUIRED
x=0.08: 8 / 8 duration-complete, mean vx 0.0416 m/s
x=0.0:  8 / 8 duration-complete, mean vx 0.0415 m/s
```

This is the first deployable-shape warm-start that keeps all eight seeds alive
and moving at x=0.08 through the fitted bridge, but it is not command-conditioned
because it also walks at zero command. The next blocker is zero-command
conditioning, not seed-5 stability.

The first command-conditioned BC attempt added six stable zero-action
x=0.0 standstill traces:

```text
artifact: outputs/analysis/PPO_BC_SWISH_COMMAND_CONDITIONED_DECISION.md
status: HOLD_X0_HARD_SEED_STANDSTILL_STABILITY
x=0.08: 8 / 8 duration-complete, mean vx 0.0413 m/s
x=0.0:  6 / 8 duration-complete, seeds 3 and 5 fall
```

This preserves the x=0.08 moving gait and fixes zero-command drift on easy
seeds, but it exposes the next blocker: hard-seed x=0.0 standstill stability.

A follow-up global action-scale diagnostic tested whether a partial source-VX
recovery action could stabilize the hard x=0.0 seeds:

```text
artifact: outputs/analysis/PPO_BC_SWISH_SOURCE_VX_SCALE_0P75_DECISION.md
status: HOLD_X008_FORWARD_PROGRESS_REGRESSION
scaled policy: outputs/analysis/ppo_bc_swish_seed5_source_vx_recovery_step0_scale_0p75.onnx
```

Result:

```text
x=0.0:  8 / 8 duration-complete, mean vx 0.0003 m/s
x=0.08: 8 / 8 duration-complete, mean vx 0.0004 m/s, track ratio 0.0046
```

This fixes hard-seed zero-command stability but collapses the walking command
to standstill. It is not a robot candidate and not a PPO launch point. The next
deployable-policy step needs command-conditioned behavior: keep the
scale-0.75-like stabilizer near zero command while preserving the full
source-VX recovery action for x=0.08.

That command-conditioned behavior was then tested directly with an ONNX wrapper:

```text
tool: tools/wrap_policy_command_scale.py
artifact: outputs/analysis/PPO_BC_SWISH_COMMAND_SCALE_DECISION.md
status: HOLD_COMMAND_SCALE_TRACKING_LIMIT
```

The wrapper scales the source-VX recovery action from `0.75` at `obs[6]=0` to
`1.0` at `obs[6]=0.08`. It passed the full x=0.0 fitted gate and restored the
x=0.08 moving behavior:

```text
x=0.0:  8 / 8 duration-complete, mean vx 0.0003 m/s
x=0.08: 8 / 8 duration-complete, mean vx 0.0416 m/s, track ratio 0.5201
```

The x=0.08 result still holds on tracking:

```text
mean max pitch target velocity p95: 3.8218 rad/s
mean max pitch tracking p95: 0.2662 rad
```

High-scale boundary probes (`0.90` through `0.975`) did not clear the tracking
gate. The current deployable-policy blocker is no longer command semantics; it
is reducing the x=0.08 action shape/timing so the fitted actuator bridge can
track it while preserving forward progress.

The wrapper was then extended with optional previous-target smoothing using
`obs[83:97]`. A two-seed x=0.08 screen also held on tracking:

```text
alpha 0.90: 2 / 2 duration-complete, mean vx 0.0388 m/s, tracking p95 0.2653 rad
alpha 0.80: 2 / 2 duration-complete, mean vx 0.0318 m/s, tracking p95 0.2592 rad
```

So the remaining issue is not solved by scalar attenuation or a one-tick target
blend. It needs a better x=0.08 action shape/timing policy, likely through
re-rate-labeled teacher data or PPO fine-tuning with the fitted bridge active.

The next deployable-shape BC run used better sources:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_DECISION.md
status: HOLD_FITTED_TRACKING_AFTER_TARGET_RATE_FIX
```

It replaced the old zero-action x=0 traces with full-observation traces from
the x=0-passing scale-0.75 stabilizing policy, then rate-limited the source-VX
x=0.08 walking labels across the full pitch chain at `2.25 rad/s`.

Result:

```text
x=0.0 fitted bridge:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0004 m/s
  mean max tracking p95: 0.0730 rad
  worst max tracking p95: 0.0837 rad

x=0.08 fitted bridge:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0341 m/s
  mean track ratio: 0.4267
  mean max pitch target velocity p95: 2.1371 rad/s
  mean max tracking p95: 0.1963 rad
```

This is the cleanest separation so far: x=0.0 hard-seed stability is mostly
solved, and x=0.08 target-rate margin is solved, but fitted actuator tracking
is still not solved. More one-step BC smoothing is unlikely to be enough. The
next high-value offline step is PPO fine-tuning or another closed-loop training
pass from this warm start with the fitted bridge active and tracking/target-rate
feedback in the objective.

The same BC fit was promoted into a Brax/PPO step-0 checkpoint:

```text
artifact: outputs/analysis/PPO_BC_SWISH_CMD_PITCH_RL_2P25_STEP0_EXPORT_FIDELITY.md
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
checkpoint: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
```

The step-0 ONNX preserves the warm-start behavior:

```text
x=0.0 fitted bridge:
  falls: 0 / 8
  duration complete: 8 / 8
  mean max tracking p95: 0.0740 rad
  worst max tracking p95: 0.0861 rad

x=0.08 fitted bridge:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0347 m/s
  mean track ratio: 0.4343
  mean max pitch target velocity p95: 2.1196 rad/s
  mean max tracking p95: 0.1958 rad
```

This checkpoint is the current best offline warm start for a fitted-bridge PPO
fine-tune. It is not robot-ready.

A tiny CPU restore smoke verified the checkpoint can enter the Playground PPO
runner with the fitted actuator bridge active:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_RESTORE_SMOKE.md
status: PASS_RESTORE_SMOKE_WITH_ABSOLUTE_CHECKPOINT_PATH
```

The first attempt failed because the restore path was relative to the RDK repo
while `runner.py` resolved it from the Playground context. The absolute path
variant passed and completed one tiny update. This is only a training-plumbing
result; it does not create a robot candidate.

The first full A100 PPO fine-tune from that checkpoint completed but held:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_FINETUNE_V1_RESULT.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
x=0.0: PASS_CANDIDATE_SIM_GATE
x=0.08: mean fitted vx 0.0010 m/s, track ratio 0.0118
```

The fine-tuned policy preserved x=0 stability and actuator-safe target rates,
but it collapsed the x=0.08 walking behavior into near-standstill. This is not
a robot candidate. The next fine-tune should preserve forward motion explicitly
during early PPO updates instead of relying on the current reward mix alone.

A second, more conservative A100 preservation fine-tune also held:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_FINETUNE_PRESERVE_V1_RESULT.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
training: PASS_SMOKE_RUN, 92160 exported PPO timesteps

x=0.0:
  status: PASS_CANDIDATE_SIM_GATE
  max pitch tracking p95: 0.0613 rad

x=0.08:
  status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
  mean fitted vx: 0.0004 m/s
  fitted command tracking ratio: 0.0045
  max sent target velocity p95: 0.4493 rad/s
  max pitch tracking p95: 0.0763 rad
```

This run used lower learning rate, smaller PPO clip, lower target-rate/tracking
penalties, and one PPO update per batch. It still erased the warm-start forward
motion. The current blocker is therefore behavior preservation during
fine-tuning, not target-rate envelope margin or basic x=0 stability. The next
offline implementation should add a state-conditioned teacher-action or
behavior-prior term before launching another A100 training run.

That behavior-prior implementation was added and tested:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_FINETUNE_BEHAVIOR_PRIOR_V1_RESULT.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
training: PASS_SMOKE_RUN, 92160 exported PPO timesteps
```

The A100 run completed training, but the Colab workflow disappeared during the
post-training gate before writing an exit sentinel. The final ONNX was recovered
and evaluated locally on CPU:

```text
x=0.0:
  status: PASS_CANDIDATE_SIM_GATE
  max pitch tracking p95: 0.0618 rad

x=0.08:
  status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
  fitted mean vx: 0.0001 m/s
  fitted command tracking ratio: 0.0015
  max sent target velocity p95: 0.4586 rad/s
  max pitch tracking p95: 0.0772 rad
```

The weak state-conditioned MLP behavior prior did not preserve forward walking.
It produced another stable, low-rate standstill. The next step should pivot away
from scalar PPO and weak-prior sweeps toward a larger selector-generated
on-distribution dataset plus BC/PPO warm start, or a stronger behavior objective
that anchors the actual closed-loop walking manifold.

A reviewed support-transition recovery fine-tune plan now exists:

```text
doc: docs/SUPPORT_TRANSITION_RECOVERY_FINETUNE_PLAN.md
dry-run manifest: outputs/analysis/support_transition_recovery_finetune/dry_run_manifest.json
status: DRY_RUN_REVIEW_READY
anchor: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
```

This is not another scalar PPO sweep. The planned smoke keeps the fitted
actuator bridge active, restores the command-conditioned pitch-rate-limited
warm start, and adds explicit support/contact transition pressure. It has not
been executed. Grade it against the step-0 baselines, not reward alone.

The tiny CPU smoke was then run:

```text
decision: outputs/analysis/SUPPORT_TRANSITION_RECOVERY_FINETUNE_SMOKE_RESULT.md
status: HOLD_X0_HARD_SEED_FAILURE_NOT_FIXED
training: PASS_SMOKE_RUN, step 1040, reward 38.2625
x=0.0 fitted bridge: falls on seeds 1 and 7
baseline control: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_FLAT_X0_FITTED_15S.md
```

This validates restore/export plumbing but rejects the reward mix. The original
step-0 warm start also fails the same stricter `flat_terrain`, 15-second x=0
gate on seeds 1 and 7, so the smoke did not create a new failure; it also did
not fix the exposed hard-seed failure. Do not scale this exact recipe to A100
and do not run its x=0.08 gate.

The x=0 hard-seed failure was then isolated to the model variant:

```text
decision: outputs/analysis/CMD_PITCH_RL_2P25_MODEL_VARIANT_X0_HARD_SEED_DECISION.md
status: HOLD_MODEL_VARIANT_GATE_MISMATCH
flat_terrain, 10 s, seeds 1 and 7: both fall
flat_terrain_backlash, 15 s, seeds 1 and 7: both pass
```

This means the current warm start is stable at x=0 on the backlash model but
not on the non-backlash flat model. Future candidate status must name the task
variant explicitly, and the next PPO or robot discussion must choose the
canonical offline promotion model intentionally.

Canonical-model recommendation:

```text
doc: docs/CANONICAL_SIM_MODEL_GATE_DECISION.md
status: RECOMMEND_CANONICAL_FLAT_TERRAIN_BACKLASH
```

Use `flat_terrain_backlash` for canonical offline promotion gates in this branch
and treat `flat_terrain` as a named stress/ablation gate unless the team
explicitly changes the canonical model.

The existing source-VX DAgger-2 deployable ONNX candidates were then validated
under a stricter 15-second fitted-bridge x=0.08 seed sweep:

```text
artifact: outputs/analysis/DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION_X008_FITTED_15S.md
command: x=0.08
duration: 15 s
bridge: fitted
seeds: 0-7
```

Neither candidate passed:

```text
dagger2:
  pass: 0 / 8
  falls: 2 / 8
  mean vx: 0.0199 m/s
  mean track ratio: 0.2487

dagger2_rate:
  pass: 0 / 8
  falls: 2 / 8
  mean vx: 0.0148 m/s
  mean track ratio: 0.1847
```

This downgrades the earlier 10-second smoke-pass DAgger candidates from
"possible warm start" to "partial distillation only." The selector still proves
that in-envelope walking exists, but the current deployable MLPs do not preserve
it over the full validation horizon. The next offline step should expand the
selector rollout dataset and repeat DAgger/BC against the 15-second fitted gate,
not run robot validation and not continue scalar PPO sweeps.

The later DAgger-3 candidates were also checked with the same 15-second fitted
x=0.08 gate:

```text
artifact: outputs/analysis/DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION_DAGGER3_X008_FITTED_15S.md
dagger3_128:
  pass: 0 / 8
  falls: 2 / 8
  mean vx: 0.0218 m/s
  mean track ratio: 0.2729

dagger3_512:
  pass: 0 / 8
  falls: 3 / 8
  mean vx: -0.0070 m/s
  mean track ratio: -0.0873
```

DAgger-3 did not change the decision. The 128-wide model moves somewhat better
than DAgger-2 but still fails tracking and hard-seed stability. The larger model
is worse. Current deployable MLP distillation remains partial, not a warm start
ready for robot-side validation.

A bounded source-VX selector expansion to seeds 8-15 also held:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_EXPANSION_SEEDS8_15_FITTED_10S.md
status: HOLD_BC_REPLAY_TERMINATED
complete moving traces: 3 / 8
failed/reverse/collapse traces: 5 / 8
```

The complete traces were seeds 8, 10, and 11, with vx around
`0.0315-0.0336 m/s`, track ratio around `0.3941-0.4204`, and target velocity
p95 around `2.27-2.29 rad/s`. Seeds 9, 12, 13, 14, and 15 terminated or moved
the wrong way. The selector is therefore a proof of existence and a source of
curated traces, not a robust teacher over arbitrary seeds.

`tools/filter_bc_manifest.py` now filters and merges BC manifests by rollout
quality. It produced:

```text
artifact: outputs/analysis/FILTERED_SOURCE_VX_SELECTOR_DAGGER4_MANIFEST.md
status: PASS_FILTERED_BC_MANIFEST_READY
kept entries: 19 / 33
samples: 9500
```

A filtered DAgger-4 128x128 rate-regularized MLP trained from that manifest
still held:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER4_FILTERED_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
duration complete: 6 / 8
terminated: seeds 1 and 7
seed 0 vx: 0.0009 m/s
best seed vx: 0.0318 m/s
```

The cleaner manifest helps isolate the remaining issue: the current deployable
BC student does not generalize the narrow selector walking manifold across
seeds. Future work should gather more curated complete traces or add a closed-
loop stabilization phase; do not treat failed selector rollouts as positive BC
labels.

Another selector expansion over seeds 16-31 found 11 complete traces and 8
additional filter-kept positive windows. The merged filtered manifest reached:

```text
artifact: outputs/analysis/FILTERED_SOURCE_VX_SELECTOR_DAGGER5_MANIFEST.md
kept entries: 27
samples: 13500
```

The resulting DAgger-5 128x128 rate-regularized MLP still failed the 10-second
smoke:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER5_FILTERED_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
duration complete: 5 / 8
terminated: seeds 1, 5, 7
seed 5 vx: -0.1500 m/s
best seed vx: 0.0308 m/s
```

This marks the current BC-only limit. Curating more positive selector windows
improves coverage but does not teach recovery from hard seeds. The next branch
should add recovery labels or closed-loop stabilization/fine-tuning, not another
plain positive-window BC fit.

That recovery-label branch has now been run once. DAgger-5 was replayed with
full observations and relabeled by the source-VX selector teacher:

```text
artifact: outputs/analysis/DAGGER5_RECOVERY_TEACHER_RELABEL.md
status: PASS_BC_TRACE_RELABEL_READY
traces: 8
samples_out: 3064
truncated terminal traces: 2
```

The resulting DAgger-6 recovery manifest combined the DAgger-5 positive
windows with the relabeled hard-state data upweighted 2x:

```text
artifact: outputs/analysis/FILTERED_SOURCE_VX_SELECTOR_DAGGER6_RECOVERY_MANIFEST.md
kept entries: 43
samples: 19628
```

The DAgger-6 128x128 rate-regularized MLP improved the previous hard-seed
distribution but still held:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER6_RECOVERY_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
duration complete: 6 / 8
terminated: seeds 1 and 7
seed 5 recovered from the DAgger-5 reverse/fall mode
```

Recovery labels helped, but BC-only distillation remains insufficient for the
earliest collapse seeds. The next offline step should target seed-1/seed-7
early-collapse recovery specifically or move to closed-loop fine-tuning from
the best BC student. Robot motion remains paused.

That targeted seed-1/seed-7 recovery pass has also been tested. The two
remaining DAgger-6 collapse seeds were replayed with full observations,
relabelled by the source-VX teacher, and upweighted 50x in a DAgger-7 manifest:

```text
artifact: outputs/analysis/FILTERED_SOURCE_VX_SELECTOR_DAGGER7_TARGETED_RECOVERY_MANIFEST.md
kept entries: 143
samples: 22778
```

The resulting DAgger-7 MLP still held:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER7_TARGETED_RECOVERY_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
duration complete: 6 / 8
terminated: seeds 1 and 7
```

Static early-collapse BC labels, even heavily upweighted, are not enough. The
remaining offline blocker is now closed-loop recovery/stabilization, not more
positive-window BC or more weight on the same first-collapse labels.

The hard-seed failures were then analyzed against the DAgger-7 manifest:

```text
artifact: outputs/analysis/DAGGER7_HARD_SEED_FAILURE_DECISION.md
seed 1: HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY
seed 7: HOLD_SEED_FAILURE_ACTION_MISMATCH
```

Seed 1 is not primarily a coverage/label-weight problem: it has nearby manifest
support and modest action mismatch, then collapses through growing positive
lateral velocity in left single support. Seed 7 still has a local action-fit
problem near right single support. The next deployable-policy branch should be
split accordingly: closed-loop lateral/height stabilization for seed 1 and a
more precise right-support recovery fit for seed 7. Do not run another uniform
static-label DAgger pass as the next experiment.

DAgger-8 tested whether local observation-noise consistency regularization could
make the deployable 128x128 MLP robust enough without changing the dataset or
teacher:

```text
artifact: outputs/analysis/DAGGER8_OBS_CONSISTENCY_DECISION.md
gate: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER8_OBS_CONSISTENCY_MLP128_RATE_REG_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
duration complete: 6 / 8
terminated: seeds 1 and 7
```

The pass seeds complete with low, in-envelope forward motion and 0% action
saturation, but seeds 1 and 7 still collapse around the first support
transition with large lateral velocity. This makes broad "more robust BC"
insufficient as a next step. The remaining offline blocker is a split hard-seed
recovery problem: seed 1 needs closed-loop lateral/height stabilization; seed 7
needs a better right-support pitch-chain action fit or recovery mapping.

A hard-seed-only screen across additional MLP initializations closed the cheap
static-BC stochasticity branch:

```text
artifact: outputs/analysis/DAGGER8_OBS_CONSISTENCY_INIT_SCREEN.md
mlp seeds: 9, 10, 11
rollout seeds: 1, 7
status: HOLD_STATIC_BC_INIT_SCREEN
all hard-seed rollouts terminated around 32-33 samples
```

The next useful offline branch should be explicit closed-loop support-transition
recovery or PPO/fine-tuning from the best BC student with the fitted actuator
bridge active. More MLP random seeds, observation-consistency tweaks, or uniform
static-label DAgger weighting are not the right next step.

The same DAgger-7 manifest was then fit into the PPO actor's deterministic
`tanh(loc)` contract:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER7_TARGETED_RECOVERY_STUDENT.md
status: PASS_PPO_LOC_BC_FIT_SMOKE
train p95 abs error: 0.043166
target-rate p95: 2.379108 rad/s
```

Its fitted-bridge x=0.08 gate still held:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER7_TARGETED_RECOVERY_X008_FITTED_10S.md
duration complete: 6 / 8
falls: seeds 1 and 7
mean track ratio: 0.3343
mean vx: 0.0267 m/s
```

Do not promote this supervised PPO-loc student directly into PPO checkpoint
fine-tuning unless the next branch explicitly adds closed-loop recovery pressure
for the hard support-transition states.

The DAgger-7 PPO-loc student was then mapped into an actual Brax/PPO step-0
checkpoint/export:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER7_TARGETED_RECOVERY_STEP0_EXPORT_FIDELITY.md
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
exported ONNX: outputs/analysis/ppo_loc_dagger7_targeted_recovery_step0.onnx
p95 action error vs PPO-loc BC ONNX: 0.00000013
```

The exported step-0 policy reproduced the same fitted-bridge x=0.08 hold:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER7_TARGETED_RECOVERY_STEP0_X008_FITTED_10S.md
duration complete: 6 / 8
falls: seeds 1 and 7
mean track ratio: 0.3329
mean vx: 0.0266 m/s
```

This proves the PPO restore/export path is coherent for the DAgger-7 student.
It does not make the checkpoint deployable. Treat it only as a possible
starting checkpoint for a future closed-loop recovery fine-tune.

## Canonical Sim Model Gate

The offline promotion model is now explicitly `flat_terrain_backlash`, not the
plain `flat_terrain` ablation:

```text
decision: docs/CANONICAL_SIM_MODEL_GATE_DECISION.md
status: RECOMMEND_CANONICAL_FLAT_TERRAIN_BACKLASH
```

Reason: the command-conditioned pitch-rate-limited warm start passes the
hard x=0 seeds on `flat_terrain_backlash` but fails the same hard seeds on
plain `flat_terrain`. The backlash model matches the upstream training/audit
path and is the more plausible sim-to-real substrate for a servo/linkage robot.
Plain `flat_terrain` remains useful as a stress check, but its results must not
be silently mixed with canonical promotion gates.

The tiny support-transition recovery smoke was therefore rechecked on the
canonical model:

```text
x=0.0, flat_terrain_backlash, fitted bridge, 15 s, hard seeds 1 and 7:
  duration complete: 2 / 2
  max tracking p95: ~0.055 rad

x=0.08, flat_terrain_backlash, fitted bridge, 15 s, seeds 0-7:
  duration complete: 7 / 8
  fall/termination: seed 3 at 78 samples
  mean vx: -0.0284 m/s
  mean track ratio: -0.3549

matched warm-start baseline, same x=0.08 gate:
  duration complete: 8 / 8
  falls: 0
  mean vx: 0.0348 m/s
  mean track ratio: 0.4344
  hold reason: tracking
```

Conclusion: the support-transition smoke is not rejected for creating a new
canonical x=0 hard-seed failure, but it is still not a robot candidate. It
mostly stands still or drifts backward at x=0.08, still has one unstable seed,
and regresses against the matched warm-start baseline. Do not scale this exact
reward mix to A100.

The next PPO branch tested behavior preservation instead of adding broad
posture/contact terms that make standing cheaper:

```text
doc: docs/BEHAVIOR_PRESERVING_RECOVERY_FINETUNE_PLAN.md
dry-run manifest: outputs/analysis/behavior_preserving_recovery_finetune/dry_run_manifest.json
result: outputs/analysis/BEHAVIOR_PRESERVING_RECOVERY_FINETUNE_SMOKE_RESULT.md
anchor: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
behavior prior: outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate_mlp.npz
status: HOLD_BEHAVIOR_PRIOR_SMOKE_REGRESSES_X008
```

The tiny CPU smoke exported successfully after a relative checkpoint-path hold
was fixed by using the absolute checkpoint path. Its x=0.08 canonical gate still
regressed:

```text
duration complete: 7 / 8
fall/termination: seed 3
mean vx: -0.0221 m/s
mean track ratio: -0.2758
```

Conclusion: even a frozen warm-start behavior prior with mild tracking/rate
pressure can lose motion through PPO. Do not scale this exact recipe to A100.
The next branch should move beyond small scalar PPO adjustments and either
expand the on-policy selector dataset or add targeted closed-loop recovery for
the early failing seeds.

Trace-level comparison then isolated what the behavior-prior smoke changed:

```text
decision: outputs/analysis/BEHAVIOR_PRESERVING_RECOVERY_TRACE_DIVERGENCE_DECISION.md
status: HOLD_SMALL_PPO_REWARD_PRIOR_LOOP
seed 3: early reverse/pitch collapse, local_vx diverges by 0.30 s
seeds 1/7: double-support standstill, ~98% double support vs ~65-67% baseline
```

This confirms the failure is not a late actuator-envelope event. The tiny PPO
updates are changing the closed-loop gait selection within the first second:
either reverse/pitch collapse or double-support freezing. The next branch should
build targeted recovery data around seeds 1, 3, and 7, and reject any candidate
that improves tracking by reducing x=0.08 velocity or single-support time.

The first targeted recovery-prior pass then built a supervised PPO-compatible
student from the warm-start baseline's successful hard-seed x=0.08 traces:

```text
decision: outputs/analysis/BASELINE_HARD_SEED_RECOVERY_PRIOR_DECISION.md
status: PASS_DIAGNOSTIC_PRIOR_HOLD_DIRECT_POLICY
dataset: seeds 1, 3, 7; command_x=0.08; 2250 samples
fit: p95 action error 0.014711, target-rate p95 1.716564 rad/s
```

Closed-loop canonical backlash gates showed this data source is useful but not
directly deployable:

```text
x=0.08 hard seeds 1/3/7: 3/3 complete, no falls, mean vx 0.0314
x=0.08 full seeds 0-7: 8/8 complete, no falls, mean vx 0.0243
x=0.0 full seeds 0-7: 8/8 complete, no falls, mean vx 0.0244
```

The x=0.0 forward drift is the key hold. The labels are a useful recovery-prior
data point, but the direct student is not command-conditioned enough to be a
candidate policy. The next dataset should combine stable x=0.0 standstill
traces, hard-seed x=0.08 recovery traces, and broader x=0.08 moving traces.

That combined dataset was tested next:

```text
decision: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DECISION.md
status: HOLD_X0_SEED5_STILL_FAILS
manifest: 19 entries, 10250 samples
BC fit: p95 action error 0.024773, target-rate p95 1.736061 rad/s
```

Canonical fitted-bridge 10-second gates:

```text
x=0.0: 7/8 complete, seed 5 falls at 73 samples, mean vx -0.0275
x=0.08: 8/8 complete, no falls, mean vx 0.0346, track ratio 0.4329
```

This improves over the earlier command-conditioned BC by preserving x=0.08
movement and clearing x=0 seed 3, but it still fails x=0 seed 5. Do not promote
this ONNX to robot validation. The next offline target is the x=0 seed-5
failure specifically, while preserving the x=0.08 recovery behavior.

The x=0 seed-5 failure was then compared against the same seed at x=0.08:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_SEED5_X0_VS_X008_TRACE_COMPARE.md
x=0 seed 5: falls at 73 samples, vx_mean -0.2176, abs_pitch_p95 1.2413, base_height_min 0.0464
x=0.08 seed 5: completes 10 s, vx_mean 0.0371, abs_pitch_p95 0.1283, base_height_min 0.1462
first local_vx divergence: tick 7 / 0.14 s
first body_pitch divergence: tick 20 / 0.40 s
```

This makes the next offline target narrower: fix the early x=0 seed-5
reverse/pitch-collapse behavior without weakening the x=0.08 branch that now
survives all eight seeds.

Follow-up seed-5 analysis against the current manifest and BC model classified
the failure as closed-loop instability, not simple missing coverage:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_SEED5_X0_FAILURE_ANALYSIS.md
status: HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY
nearest manifest distance p95: 1.8015
nearest action L1 p95: 0.0820
```

Passing x=0 seed traces were then captured for seeds 0 and 3:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_X0_PASS_TRACE_GATE.md
seed 0: PASS, body_pitch_p95 0.0239, tracking_p95 0.0754
seed 3: PASS, body_pitch_p95 0.0331, tracking_p95 0.0724
```

Compared with passing x=0 seeds, seed 5 diverges from the first samples and
spends less time in quiet double support before reverse/pitch collapse. The
next corrective branch should stabilize this zero-command hard seed locally,
not globally damp the policy or add more generic x=0.08 motion labels.

A bounded weighting experiment tested whether simply emphasizing the stable
x=0 seed-5 source trace fixes that hard seed:

```text
decision: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_WEIGHTED_SEED5_X0_DECISION.md
status: HOLD_WEIGHTED_SEED5_X0_STILL_FAILS
weighted x=0 seed-5 source trace: 8x
x=0 fitted gate: 7/8 complete, seed 5 falls at 57 samples
```

This is a negative result. The unweighted candidate fell at 73 samples, so
simple supervised reweighting made the hard seed worse. The next branch should
use corrective on-policy relabeling or an explicit zero-command stabilizer, not
larger weights on the same labels.

Corrective on-policy relabeling was then tested directly:

```text
decision: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DAGGER_SEED5_X0_DECISION.md
status: HOLD_X008_TRACKING_BUT_X0_SEED5_FIXED
relabel: 72 failing x=0 seed-5 visited states, truncated before terminal row
```

Canonical fitted-bridge 10-second gates:

```text
x=0.0:
  duration complete: 8 / 8
  falls: 0
  seed 5: PASS, vx_mean 0.0053, tracking_p95 0.0763

x=0.08:
  duration complete: 8 / 8
  falls: 0
  mean vx: 0.0344
  mean track ratio: 0.4294
  pitch-chain target velocity p95: 2.1043-2.1639 rad/s
  tracking p95: 0.1875-0.1985 rad
```

This is the best result in the command-conditioned hard-seed line so far: the
zero-command hard-seed collapse is fixed and the forward branch remains stable
and in-envelope. It is still **not** a robot candidate because `x=0.08`
tracking error remains too high. The next offline target is fitted-bridge
tracking improvement without breaking the newly fixed zero-command stability.

A first tracking-tightening variant lowered the BC target-rate limit from
`2.25` to `1.75 rad/s` and increased target-rate penalty scale from `0.2` to
`0.6`:

```text
decision: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_DAGGER_SEED5_X0_RATE175_DECISION.md
status: HOLD_RATE_TIGHTENING_BREAKS_X0_SEED5
supervised target-rate p95: 1.5732 rad/s
x=0 fitted gate: seed 5 falls at 59 samples
```

This is a negative result. Global target-rate tightening reduces the supervised
rate metric but breaks the zero-command hard-seed fix. The next tracking branch
must preserve the DAgger seed-5 correction explicitly.

Smoothing only the `x=0.08` pitch-chain labels was then tested:

```text
decision: outputs/analysis/COMMAND_CONDITIONED_DAGGER_SEED5_X0_PITCH_RATE_1P75_DECISION.md
status: HOLD_PITCH_RATE_LABEL_SMOOTHING_KILLS_PROGRESS
x=0 fitted gate: 8/8 complete, seed 5 fixed
x=0.08 fitted gate: 8/8 complete, mean track ratio 0.1171
pitch-chain target velocity p95: 1.4886-1.6901 rad/s
tracking p95: 0.1472-0.1834 rad
```

This preserves zero-command stability and improves the tracking/target-rate
direction, but removes too much forward motion. The next branch should not
lower moving-label rates further; it needs tracking feedback or PPO fine-tuning
from the DAgger seed-5 checkpoint while preserving propulsion.

## Physical Start-Pose Calibration Check

The real robot home/start pose has been checked against both telemetry and a
repo-rendered physical reference. It should no longer be treated as the leading
explanation for the walking failure unless new evidence appears.

Canonical procedure:
`docs/PHYSICAL_START_POSE_CALIBRATION_GATE.md`.

What is already supported:

```text
- runtime HWI.init_pos matches the sim home keyframe
- live RDK-X5 duck_config offsets were captured
- home_pose_log_test showed stable gyro, +Z dominant accel, and small joint
  tracking errors at the compensated home pose
- repo zero/home pose references were rendered from the Open Duck Mini v2 MJCF
- Rob confirmed the commanded home pose visually matches the rendered home pose
```

What is still not proven:

```text
- a fresh physical calibration-to-spec pass was run after the later robot work
- the large left-knee offset was mechanically revalidated
```

This matters because the walking policy is closed-loop around the robot's body
state and joint feedback. A small real mechanical start-pose mismatch can shift
foot contact timing, stance loading, and the first weight transfer. However,
the current evidence says the commanded home pose is visually consistent with
the repo/sim home pose, and the software feedback path tracks home cleanly.
Blind soft-offset recalibration is therefore more likely to add operator error
than solve the current gait problem.

Current status:

```text
PASS_PHYSICAL_HOME_POSE_VISUAL_CHECK
PASS_HOME_POSE_TELEMETRY_HOLD
HOLD_ZERO_RECALIBRATION_NOT_NEEDED_WITHOUT_VISIBLE_MISMATCH
```

Follow-up offline source/config audit:

```text
tool: tools/verify_home_pose_contract.py
artifact: outputs/analysis/HOME_POSE_CONTRACT_AUDIT.md
status: PASS_HOME_POSE_CONTRACT
max_abs_runtime_minus_sim_home_rad: 0.0000
max_abs_runtime_zero_rad: 0.0000
max_abs_raw_bypass_minus_normal_home_rad: 1.4880
```

This proves the repo-level contract: runtime `HWI.init_pos` exactly matches the
Playground `home` keyframe `ctrl` vector, and runtime zero is all zeros. It also
proves why "raw sim-home" is not a safe shortcut: raw-bypass home ignores
`duck_config.json` offsets, and for the current live offsets would differ from
the normal compensated raw home target by up to `1.4880 rad` at `left_knee`.

The remaining unproven item is physical, not source-level: whether the real
robot's mechanical zero was freshly aligned to the repo-defined zero/home after
later motor work. That requires either the interactive `find_soft_offsets.py`
procedure or the read-only raw-position audit while the robot is independently
placed in the repo-defined home geometry.

## PPO Warm-Start From DAgger Seed-5 Candidate

The current best BC/DAgger candidate was converted into a PPO-compatible
step-0 checkpoint:

```text
decision: outputs/analysis/PPO_BC_COMMAND_CONDITIONED_DAGGER_SEED5_X0_WARMSTART_DECISION.md
status: PASS_WARMSTART_INFRASTRUCTURE_READY_BUT_POLICY_STILL_HOLDS_X008_TRACKING
checkpoint: outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0_checkpoint
onnx: outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0.onnx
```

The step-0 export reproduces the BC ONNX:

```text
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
samples checked: 2048
p95 abs action error: 1.19e-7
max abs action error: 3.58e-7
```

Step-0 fitted-bridge gates confirm this is behavior-preserving:

```text
x=0.0:
  status: PASS_CANDIDATE_SIM_GATE
  max pitch tracking p95: 0.0691 rad

x=0.08:
  status: HOLD_CANDIDATE_TRACKING
  mean vx: 0.0213 m/s
  track ratio: 0.2663
  max pitch tracking p95: 0.1872 rad
  max sent target velocity p95: 1.9571 rad/s
```

The first PPO restore smoke failed because the restore checkpoint path was
relative to the Playground runner working directory. The wrapper now resolves
relative restore checkpoints and relative output roots against the RDK repo.
A path-fixed tiny CPU restore smoke passed:

```text
status: PASS_SMOKE_RUN
num timesteps: 16
saved checkpoint: step 20
```

Interpretation: PPO warm-start infrastructure is ready for a real offline
fine-tuning run. The policy itself is still not robot-ready; the next branch
must improve `x=0.08` fitted-bridge pitch tracking while preserving the fixed
`x=0.0` hard-seed behavior.

## A100 PPO Warm-Start Fine-Tune Result

The first A100 PPO fine-tune from the DAgger seed-5 x0 step-0 checkpoint ran
successfully on CUDA/JAX, but the exported policy regressed:

```text
decision: outputs/analysis/PPO_BC_COMMAND_CONDITIONED_DAGGER_SEED5_X0_A100_FINETUNE_DECISION.md
status: HOLD_PPO_WARMSTART_FINETUNE_REGRESSED
platform: A100 / CUDA / JAX 0.7.2
robot touched: false
deploy performed: false
```

Training reward increased through step `92160`, but local fitted-bridge gates
rejected the exported ONNX:

```text
x=0.08 seed 0:
  status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
  mean vx: 0.0011 m/s
  track ratio: 0.0138
  max pitch tracking p95: 0.0794 rad

x=0.0 seed 5:
  status: HOLD_CANDIDATE_FALL_OR_TERMINATION
  samples: 37
  base height min: 0.0501 m
  action saturation: 100%
```

The Colab per-seed gates in the artifact bundle all timed out during the
default 90 second sim preflight, so the decision is based on local CPU
re-gates with a longer preflight. Do not continue this exact PPO recipe:
reward-only checkpoint selection is not aligned with the candidate gates.

## Behavior-Prior PPO A100 Fine-Tune Result

A conservative behavior-prior PPO fine-tune was run after the PPO-only
regression:

```text
decision: outputs/analysis/PPO_BEHAVIOR_PRIOR_A100_FINETUNE_DECISION.md
status: HOLD_BEHAVIOR_PRIOR_PPO_REJECTED_BY_CHECKPOINT_SWEEP
behavior prior scale: -0.2
PPO learning rate: 0.00005
PPO clip epsilon: 0.1
platform: A100 / CUDA / JAX 0.7.2
```

Training completed and exported one checkpoint at step `40960`, but the compact
promotion sweep rejected it:

```text
x=0.0:
  status: HOLD_CANDIDATE_ACTION_SATURATION
  max pitch tracking p95: 0.3685 rad
  action saturation: 100%

x=0.08:
  status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
  mean vx: 0.0109 m/s
  track ratio: 0.1362
  max pitch tracking p95: 0.2109 rad
```

Interpretation: a simple behavior-prior/trust-region term was not enough to
make PPO fine-tuning preserve the DAgger candidate. The next learning change
should not be another scalar PPO recipe. It should use gate-aligned selection,
explicit saturation constraints, or DAgger/rollout correction before more GPU
training.

## Colab Candidate Checkpoint Sweep Selection

The Colab CUDA workflow now supports gate-aligned checkpoint selection after a
candidate PPO run:

```text
artifact: outputs/analysis/COLAB_CANDIDATE_CHECKPOINT_SWEEP_SELECTION.md
status: PASS_GATE_ALIGNED_SELECTION_PLUMBING_READY
default compact sweep: x=0.0 and x=0.08, fitted bridge, 1.0 s
```

This addresses the failure pattern seen in the PPO-only and behavior-prior
A100 runs: training reward increased, but the exported/latest ONNX regressed
the actual candidate gates. After training, the workflow can now run
`tools/sweep_candidate_checkpoints.py` over every exported ONNX checkpoint,
select a checkpoint with `PASS_PROMOTE_CANDIDATE_CHECKPOINT` when one exists,
and run the normal final x=0.0/x=0.08 gates on that selected checkpoint instead
of blindly gating the latest reward checkpoint.

This is infrastructure only. It does not make any existing PPO checkpoint a
robot candidate, and it does not authorize robot motion. Robot validation
remains blocked until an offline candidate passes the standard gates.

## x=0.08 Relabel Weight-3 Diagnostic

A bounded DAgger diagnostic tested whether adding relabeled x=0.08 visited
states to the current best command-conditioned student would improve the
remaining fitted-bridge tracking hold:

```text
decision: outputs/analysis/COMMAND_CONDITIONED_X008_RELABEL_WEIGHT3_DECISION.md
status: HOLD_X008_RELABEL_WEIGHT3_REGRESSES_FORWARD_PROGRESS
```

Two x=0.08 fitted-bridge traces from the current best candidate were collected
with full observations:

```text
seed 0: duration complete, tracking hold
seed 5: duration complete, tracking hold
samples: 1000 BC-ready
```

Relabeling those states with the existing blend teacher produced only modest
action differences:

```text
seed 0 action_delta_p95: 0.0394
seed 5 action_delta_p95: 0.0542
```

After merging the traces back into the manifest and upweighting them 3x, the
new supervised student regressed in the compact fitted-bridge sweep:

```text
best x=0.08:
  mean vx 0.0223, track ratio 0.2793

relabel_weight3 x=0.08:
  mean vx -0.0172, track ratio -0.2154
```

Interpretation: another small static DAgger relabel against the same teacher is
not the next useful path. The x=0.08 tracking hold needs a stronger change in
closed-loop dynamics, training feedback, or teacher signal; not more upweighting
of nearly identical labels.

## Actuator-Tracking Behavior-Prior Probe

An A100 candidate-only run tested whether restoring from the PPO-compatible
step-0 checkpoint, keeping the command-conditioned student as a behavior prior,
and adding explicit actuator-tracking pressure would preserve forward progress
while reducing the fitted-bridge tracking hold:

```text
result doc: docs/ACTUATOR_TRACKING_BEHAVIOR_PRIOR_PROBE_RESULT.md
training status: PASS_SMOKE_RUN
step 0 reward: 16.7091
step 40960 reward: 20.6604
robot touched: false
```

The remote Colab checkpoint sweep wedged in a GPU eval worker after training
completed, so the exported ONNX checkpoints were swept locally on CPU with the
same compact fitted-bridge x=0.0/x=0.08 gate:

```text
step 0 x=0.08:
  mean vx: 0.0215 m/s
  track ratio: 0.2692
  max pitch tracking p95: 0.2233 rad
  status: HOLD_CANDIDATE_TRACKING

step 40960 x=0.08:
  mean vx: 0.0083 m/s
  track ratio: 0.1043
  max pitch tracking p95: 0.2182 rad
  status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

No checkpoint was promoted. The step-40960 PPO update improved reward and
reduced target velocity, but it also reduced useful forward motion. This repeats
the known deployability failure: small PPO reward/penalty changes can make the
policy look calmer while moving it back toward the low-progress basin. Robot
validation remains blocked.

A policy-vs-prior comparison on the behavior-prior manifest showed the drift
directly:

```text
step 0 teacher-action p95 error: ~0.0000
step 40960 teacher-action p95 error: 0.1409
```

That means the PPO update moved away from the behavior-prior action map on the
prior's own states. Future PPO work needs a stronger continuity mechanism if the
goal is to preserve the working closed-loop behavior while improving tracking.

Workflow note: post-training compact checkpoint sweeps now default to CPU via
`--candidate-checkpoint-sweep-jax-platform cpu` while training remains on GPU.
This avoids the A100 MJX eval-worker wedge observed during this run.

## Actuator-Tracking Behavior-Prior Weight Blend Diagnostic

An offline ONNX weight-interpolation diagnostic blended the behavior-prior PPO
step-0 export toward the step-40960 export at alphas 0.05, 0.10, 0.20, 0.35,
and 0.50.

```text
result doc: docs/ACTUATOR_TRACKING_BEHAVIOR_PRIOR_WEIGHT_BLEND_RESULT.md
status: HOLD_WEIGHT_BLEND_DOES_NOT_FIX_TRACKING
robot touched: false
```

The best compact fitted-bridge result was alpha 0.05:

```text
x=0.08 mean vx: 0.0253 m/s
x=0.08 track ratio: 0.3158
x=0.08 max pitch tracking p95: 0.2217 rad
x=0.08 max pitch sent velocity p95: 1.8523 rad/s
status: HOLD_CANDIDATE_TRACKING
```

Small blends slightly improved forward progress but did not materially reduce
the tracking hold. Larger blends drifted back toward low progress, matching the
step-40960 failure mode. Robot validation remains blocked.

## Pitch-Chain 4.3 Rate-Limit Curation

The full pitch-chain `4.3 rad/s` curation was tested offline against the strict
fitted-backlash x=0.08 8-seed gate.

```text
result doc: docs/PITCH_CHAIN_RATE_LIMIT_CURATION_RESULT.md
duration_complete: 8/8
falls: 0/8
mean vx: 0.0477 m/s
mean track ratio: 0.5965
max pitch velocity p95: 4.1935-4.2879 rad/s
max tracking p95: 0.2685-0.2794 rad
status: HOLD_CANDIDATE_TRACKING
```

Compared with the earlier right-knee-only `4.3 rad/s` curation, the full
pitch-chain cap did not materially improve the strict gate. Robot validation
remains blocked; this candidate is useful evidence, not a deployable policy.

## Right-Knee Transition Spike Filter

A targeted transition filter tested whether the right-knee spike source could
be removed from the source-vx selector dataset:

```text
result doc: docs/RIGHT_KNEE_TRANSITION_SPIKE_FILTER_RESULT.md
right-knee >3.75 rad/s action ticks: 506 / 3992
within 2 ticks of contact transition: 404 / 506
filtered samples: 3124 / 4000 kept
duration_complete: 8/8
falls: 0/8
mean vx: 0.0449 m/s
mean track ratio: 0.5617
max pitch velocity p95: 4.6244-4.7790 rad/s
max tracking p95: 0.2675-0.2782 rad
status: HOLD_CANDIDATE_TRACKING
```

The filter preserved stability but worsened the target-velocity gate and
reduced forward progress. Robot validation remains blocked. This closes the
simple deletion/filtering branch; the right-knee contact transition needs
dynamics-aware relabeling or gate-aware training, not another post-hoc filter.

## Next Deployable Policy Branch Decision

The current offline decision artifact is:

```text
tool: tools/decide_next_deployable_policy_branch.py
artifact: outputs/analysis/NEXT_DEPLOYABLE_POLICY_BRANCH_DECISION.md
status: PLAN_GATE_AWARE_ROLLOUT_CORRECTION_OR_RECURRENT_STUDENT
```

All current deployable-style candidates preserve some forward motion and stay
upright for 8/8 seeds, but all remain held by the same fitted-bridge tracking
plateau around `0.27 rad`. The closed branches are:

```text
uniform pitch-chain clipping
transition-adjacent sample deletion
post-hoc ONNX weight interpolation
scalar behavior-prior PPO smoke
```

Robot validation remains blocked. The next offline branch should be
gate-aware rollout correction, a recurrent/phase-aware student, or PPO
fine-tuning with stronger behavior preservation and strict gate checks after
short runs.

## Pitch-Chain 4.3 PPO-Shape Rate Student

An offline PPO-shape feed-forward BC student was trained from the pitch-chain
`4.3 rad/s` curated source-vx manifest and evaluated under the strict
fitted-backlash x=0.08 8-seed gate.

```text
result doc: docs/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_RESULT.md
duration_complete: 8/8
falls: 0/8
mean vx: 0.0393 m/s
mean track ratio: 0.4913
max pitch velocity p95: 3.6035-3.7059 rad/s
max tracking p95: 0.2516-0.2561 rad
status: HOLD_CANDIDATE_TRACKING
```

The student brought target velocity into the fitted envelope and slightly
reduced tracking error, but lost forward progress and still missed the tracking
gate by a wide margin. This closes simple feed-forward BC smoothing as a
standalone fix. Robot validation remains blocked.

## Gate-Aware Static Relabel BC

Full-observation traces were collected from the pitch-chain `4.3` PPO-shape rate
student on strict-gate seeds 1 and 4, then relabeled with the source-VX teacher
and merged back into the BC dataset at `12x` weight.

```text
result doc: docs/GATE_AWARE_RELABEL_STATIC_BC_RESULT.md
relabel samples: 1000
seed 1 relabel action_delta_p95: 0.0848
seed 4 relabel action_delta_p95: 0.0968
```

Targeted seed screen after retraining:

```text
seed 1: vx 0.0372, track ratio 0.4652, max pitch velocity p95 3.7264, tracking p95 0.2548
seed 4: vx 0.0380, track ratio 0.4747, max pitch velocity p95 3.6821, tracking p95 0.2536
status: HOLD_CANDIDATE_TRACKING
```

This is not enough improvement to justify robot validation or a full promotion.
Static gate-aware source-VX relabeling is closed as a standalone fix. The
remaining offline branch must change the closed-loop training mechanism, not
only the static labels.

## PPO Warm-Start / Naive Tracking-Correction Smoke

The pitch-chain `4.3` PPO-shape BC student was successfully converted into a
real Brax PPO checkpoint and exported through the normal Playground ONNX path.

```text
result doc: docs/PPO_WARMSTART_TRACKING_CORRECTION_SMOKE_RESULT.md
step-0 status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
step-0 fitted-backlash gate: HOLD_CANDIDATE_TRACKING
duration_complete: 8/8
falls: 0/8
mean vx: 0.0396 m/s
mean track ratio: 0.4944
max pitch velocity p95: 3.6200-3.7078 rad/s
max tracking p95: 0.2522-0.2583 rad
```

That validates the PPO warm-start plumbing. A tiny PPO correction smoke from
the checkpoint also ran successfully, but its targeted seed screen failed by
collapsing forward progress:

```text
screen status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0007, track ratio -0.0082, tracking p95 0.1121
seed 4: vx  0.0031, track ratio  0.0392, tracking p95 0.1078
```

The naive tracking-cost fine-tune is therefore closed as a standalone fix. It
improves calmness/tracking by stopping, not by producing a deployable gait.
Robot validation remains blocked.

A behavior-preservation control removed target-rate and actuator-tracking
penalties, lowered the learning rate, and strengthened the behavior prior. It
also collapsed into low progress:

```text
screen status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0008, track ratio -0.0104, tracking p95 0.1213
seed 4: vx  0.0035, track ratio  0.0433, tracking p95 0.1170
```

So the issue is broader than the explicit tracking penalty. The current PPO
resume/reward setup is not preserving the walking basin; the next offline
training branch needs a true trust-region or behavior-preserving update, not
another scalar penalty sweep.

Low-alpha blends between the validated step-0 ONNX and the behavior-control
step-640 ONNX were also screened:

```text
screen artifact: outputs/analysis/PPO_WARMSTART_BEHAVIOR_CONTROL_WEIGHT_BLENDS_SEED1_SEED4_SCREEN.md
alphas: 0.01, 0.02, 0.05, 0.10
status: HOLD_CANDIDATE_TRACKING
targeted vx mean range: 0.0388-0.0401 m/s
targeted track ratio mean range: 0.4847-0.5010
```

The blend direction preserves baseline motion at low alpha, but it does not
materially improve the fitted-bridge tracking gate. Full PPO update freezes;
small blends are effectively no-ops.

A built-in adaptive-KL PPO schedule was tested as a final small control from
the same warm-start checkpoint:

```text
screen artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_ADAPTIVE_KL_CONTROL_SEED1_SEED4_SCREEN.md
schedule: ADAPTIVE_KL
desired KL: 0.0005
screen status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0006, track ratio -0.0080, tracking p95 0.1052
seed 4: vx  0.0034, track ratio  0.0426, tracking p95 0.1064
```

Adaptive-KL learning-rate control also freezes rather than correcting the
walking policy. The PPO path remains useful as plumbing, but the next offline
branch needs an explicit policy-distribution trust region, gate-aware rollout
correction, or a different behavior-preserving update. Robot validation remains
blocked.

The existing hard command-progress failure termination was also tested from the
same warm-start checkpoint:

```text
screen artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_PROGRESS_FAILURE_CONTROL_SEED1_SEED4_SCREEN.md
command_progress_failure_min_ratio: 0.30
command_progress_failure_warmup_steps: 80
screen status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0007, track ratio -0.0092, tracking p95 0.1199
seed 4: vx  0.0033, track ratio  0.0417, tracking p95 0.1016
```

That also collapsed into near-standstill. The current PPO fine-tune tooling can
resume/export policies, but the available scalar reward, default KL schedule,
and existing progress-termination controls do not preserve the walking basin.
Robot validation remains blocked.

A default-off restore-policy KL hook was added to the Playground PPO loss and
tested at two scales:

```text
loss term: scale * KL(current_policy || restored_policy)
scale 1.0 screen: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_RESTORE_POLICY_KL_CONTROL_SEED1_SEED4_SCREEN.md
scale 100.0 screen: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_RESTORE_POLICY_KL100_CONTROL_SEED1_SEED4_SCREEN.md
both status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
scale 1.0 vx mean: 0.0014, track ratio mean: 0.0173
scale 100.0 vx mean: 0.0013, track ratio mean: 0.0168
```

This confirms that a loss-level anchor can be wired into the PPO path, but these
bounded settings still do not preserve forward motion. Robot validation remains
blocked.

Full-observation seed-1 traces compared the preserved step-0 warm start against
the restore-policy KL100 checkpoint:

```text
comparison artifact: outputs/analysis/PPO_WARMSTART_STEP0_VS_RESTORE_POLICY_KL100_SEED1_TRACE.md
step-0 analysis: outputs/analysis/PPO_WARMSTART_STEP0_SEED1_TRACE_COVERAGE_ANALYSIS.md
KL100 analysis: outputs/analysis/PPO_WARMSTART_RESTORE_POLICY_KL100_SEED1_TRACE_COVERAGE_ANALYSIS.md
```

The step-0 warm start remains close to the source-VX walking manifold:

```text
status: HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY
mean vx: 0.0361 m/s
target velocity p95: 2.2016 rad/s
joint tracking p95: 0.1742 rad
nearest manifest distance mean/p95: 0.2325 / 0.3598
nearest action L1 mean/p95: 0.0277 / 0.0500
contacts: 63.0% double support, 36.8% single support
```

The KL100 checkpoint is no longer on that manifold and freezes in double
support:

```text
status: HOLD_SEED_FAILURE_ACTION_MISMATCH
mean vx: -0.0006 m/s
target velocity p95: 0.7370 rad/s
joint tracking p95: 0.0693 rad
nearest manifest distance mean/p95: 1.3746 / 1.5831
nearest action L1 mean/p95: 0.1574 / 0.2044
contacts: 97.8% double support
```

Interpretation: the restore-policy KL term on PPO rollout observations
preserves calmness, not the gate-passing walking distribution. This closes
restore-policy-KL-only scale tuning as the next branch. The next deployable
policy work must either correct rollout states back toward the gate-passing
source-VX manifold or add recurrent/phase-aware state that preserves the
stance-transition mechanism.

Gate-aware rollout correction plumbing was added after the restore-policy KL
controls. The relabeler can now write row-level sample weights for low progress,
double-support drift, reverse velocity, lateral velocity, and high
fitted-bridge tracking error; the PPO-loc BC student trainer now consumes those
weights. Two failed seed-1 traces were relabeled with the source-VX teacher and
merged with the eight source-VX walking traces:

```text
relabel artifact: outputs/analysis/GATE_AWARE_ROLLOUT_CORRECTION_RELABEL.md
relabel status: PASS_BC_TRACE_RELABEL_READY
merged manifest: outputs/analysis/GATE_AWARE_ROLLOUT_CORRECTION_MERGED_MANIFEST.md
merged status: PASS_FILTERED_BC_MANIFEST_READY
merged samples: 5000
```

A tiny 200-step supervised smoke fit verified the weighted manifest path and
ONNX export:

```text
artifact: outputs/analysis/GATE_AWARE_ROLLOUT_CORRECTION_STUDENT_SMOKE.md
status: PASS_PPO_LOC_BC_FIT_SMOKE
```

This is not a deployable policy. It is a substrate for the next offline branch:
a real gate-aware rollout-correction student or a recurrent/phase-aware student
followed by the strict fitted-backlash multi-seed candidate gate. Robot
validation remains blocked.

A bounded two-seed screen of the smoke ONNX confirmed it is not a candidate:

```text
artifact: outputs/analysis/GATE_AWARE_ROLLOUT_CORRECTION_STUDENT_SMOKE_SCREEN.md
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 1: fall_or_nan after 98 samples
seed 4: fall_or_nan after 56 samples
```

The screen is only a sanity check for the exported smoke model; it does not
invalidate the weighted correction-data path.

## Corrected Knee Bridge Re-Anchor

The left-knee soft-offset error was fixed on the robot and the correction was
validated on stand:

```text
left_knee offset:  -1.488 -> 0.0371 rad
right_knee offset:  0.0798 rad unchanged
left/right knee joint-space agreement after monitor: within about 0.63 deg
```

Corrected low-speed sine sweeps passed for the pitch chain at 0.25, 0.5, and
1.0 Hz with 0.03 rad amplitude. The left knee no longer appears as a low-speed
tracking outlier.

The corrected suspended `x=0.08` replay of `BEST_WALK_ONNX_2` still held:

```text
status: HOLD_DYNAMIC_TRACKING_STILL_BLOCKS_WALKING
pitch-chain sent velocity p95: 3.14-5.22 rad/s
pitch-chain tracking p95:      0.125-0.171 rad after startup filtering
dynamic lag:                   mostly 3-4 ticks
write errors:                  0
read checksum errors:          20
```

This confirms the old knee asymmetry was a real confound and is now gone, but
it was not the full walking blocker. The upstream policy remains dynamically
too aggressive for the corrected real actuator chain. Direct deployment of
`BEST_WALK_ONNX_2` remains dead and grounded replay remains blocked.

The canonical corrected actuator bridge for all subsequent sim/eval/training is
now:

```text
outputs/analysis/actuator_response_fit_corrected_knee.json
sha256: 3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0
```

The old `outputs/analysis/actuator_response_fit.json` is historical only for
new candidate gates. Future gates must use the corrected per-joint pitch-chain
velocity limits rather than the old global `3.75 rad/s` ceiling:

```text
left_hip_pitch  2.50 rad/s
left_knee       3.25 rad/s
left_ankle      2.75 rad/s
right_hip_pitch 2.25 rad/s
right_knee      2.75 rad/s
right_ankle     2.00 rad/s
```

Read-checksum sensitivity was checked by refitting after dropping read-error
event windows. Delay remained 3 ticks, but one joint fit hit the velocity upper
grid bound, so the exclusion fit is logged as a warning rather than used to
loosen the envelope. The conservative full corrected dynamic fit remains
canonical.

Current objective: produce a deployable policy that walks forward 8/8 seeds
in-envelope against this corrected bridge before any first grounded hardware
test.

Corrected-bridge Step 1 rerolled `BEST_WALK_ONNX_2` at `x=0.08` through the
canonical corrected bridge in `flat_terrain_backlash`:

```text
artifact: outputs/analysis/CORRECTED_BRIDGE_BEST_WALK_REROLL_X008.md
pass: 0/8
duration_complete: 7/8
falls: 1/8
max corrected per-joint velocity excess mean: 2.4227 rad/s
max tracking p95 mean: 0.2661 rad
```

Corrected-window mining then checked 1030 short windows:

```text
artifact: outputs/analysis/CORRECTED_BRIDGE_TEACHER_WINDOWS_X008.md
pass_windows: 1
pass_left_stance_windows: 0
pass_right_stance_windows: 0
top rejection reason: over_corrected_envelope, 1029/1030 windows
```

Decision: the old asymmetric-bridge teacher data and source-VX selectors are
not current evidence. The knee correction removed the asymmetry confound, but
it did not recover a balanced corrected-bridge teacher source from
`BEST_WALK_ONNX_2`. Future deployable-policy work must rebuild any teacher
source under the corrected bridge or train directly against the corrected
per-joint gate.

A small corrected-bridge command screen also checked straight low commands and
the upstream turning command:

```text
artifact: outputs/analysis/CORRECTED_BRIDGE_COMMAND_SCREEN.md
status: HOLD_MOVEMENT_REQUIRES_OVER_ENVELOPE
straight x=0.02: in envelope, no forward motion
straight x=0.04: near envelope, no forward motion
straight x=0.08: moves, but over corrected envelope
upstream turn: moves, but over corrected envelope
```

This closes the remaining `BEST_WALK_ONNX_2` source loophole for the checked
command cells: movement still requires corrected-envelope violation.

A short corrected-bridge screen of existing student/candidate ONNX files found
one lead but no deployable result:

```text
artifact: outputs/analysis/CORRECTED_BRIDGE_EXISTING_CANDIDATE_SCREEN.md
duration: 3 s
seeds: 0, 1

dagger_iter3: tracking hold
phase_quadrant: tracking hold
phase_smooth: low-progress/tracking hold
gate_aware_smoke: fall/saturation hold
ppo_warmstart: tracking hold
cmd_conditioned: 2/2 short-screen pass
```

`cmd_conditioned` stayed under the corrected per-joint velocity envelope in
both short seeds and had max pitch-chain tracking p95 below `0.20 rad`, but its
mean track ratio was only about `0.41` over a 3 s screen. It is a warm-start
lead for the full corrected gate, not a promotion candidate.

Full corrected-bridge gates then promoted `cmd_conditioned` as the current
sim-side deployment candidate:

```text
decision artifact: outputs/analysis/CORRECTED_BRIDGE_DEPLOYABLE_CANDIDATE_DECISION.md
package artifact: outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_CANDIDATE_PACKAGE.md
stable policy package: policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/
policy: policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx
policy sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e

x=0.08 fitted corrected bridge:
  passes: 8/8
  falls: 0/8
  duration complete: 8/8
  mean vx: 0.0339 m/s
  mean track ratio: 0.4238
  max corrected velocity excess: 0.0000 rad/s
  max pitch-chain tracking p95: 0.1973 rad

x=0.0 fitted corrected bridge:
  passes: 8/8
  falls: 0/8
  duration complete: 8/8
  mean vx: 0.0003 m/s
  max corrected velocity excess: 0.0000 rad/s
  max pitch-chain tracking p95: 0.0748 rad
```

This is a slow in-envelope walker, not a full-speed `x=0.08` tracker. It is
eligible for stand/suspended hardware telemetry validation only after review;
grounded replay remains blocked. Operator handoff packets for reviewed
stand/suspended telemetry are prepared at:

```text
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_HW_X0_HANDOFF.md
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_HW_X008_HANDOFF.md
```

These packets were generated by the offline-safe planning mode of
`tools/instrumented_lowcmd_hw_eval.py`; no robot command was run.

Stand/suspended hardware transfer was then run with Rob present and the robot
on the stand:

```text
decision artifact: outputs/analysis/CORRECTED_CANDIDATE_STAND_TRANSFER_DECISION.md

x=0.0 stand:
  samples: 747
  max pitch-chain sent velocity p95: 0.2310 rad/s
  max pitch-chain tracking p95: 0.0145 rad
  post-startup max tracking: 0.0235 rad
  action saturation: 0%
  write errors: 0
  read checksum increments: 18

x=0.08 stand:
  samples: 747
  suspended gate: WARN_PROCEED_WITH_CAUTION
  max pitch-chain sent velocity p95: 0.4065 rad/s
  max target-analyzer pitch-chain velocity p95: 0.3950 rad/s
  max pitch-chain tracking p95: 0.0222 rad
  post-startup max tracking: 0.0235 rad
  action saturation: 0%
  rate limit active: 0%
  write errors: 0
  read checksum increments: 6
```

The `x=0.08` stand run is the first hardware transfer evidence that the
corrected candidate commands a trackable waveform on the real Duck. Grounded
replay remains a separate human decision because read checksum warnings still
exist and the candidate is intentionally slow.

Phase 2 robustness update:

```text
artifact: docs/PHASE2_DOMAIN_RANDOMIZATION_ROBUSTNESS.md
decision: outputs/analysis/PHASE2_STAGE_C_TERRAIN_Z002_DECISION.md
status: HOLD_STAGE_C_TERRAIN_Z002_TRACKING_MARGIN
```

The Stage A promoted candidate remains the current deployable sim candidate for
flat-ground corrected-bridge gates:

```text
policy: policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
sha256: a082be6cf5c486073523bbd0fba4ea3645dc448270ca0a8e28c4ce5a4e8d31c4
```

Phase 2 push evals showed that this candidate already tolerates mild and
moderate synthetic torso pushes in the corrected-bridge evaluator while staying
upright and in-envelope. The harder blocker is terrain:

```text
flat: pass
rough hfield z=0.002: near-pass / strict tracking hold
rough hfield z=0.005: hold
stock rough hfield z=0.010: hard hold
```

Stage C0-C2 terrain fine-tunes completed successfully but did not promote a new
candidate. The best z=0.002 short-screen result still missed strict tracking:

```text
c0_245760:
  seed 0 tracking p95: 0.2040 rad
  seed 1 tracking p95: 0.1965 rad
  mean track ratio: 0.3965
  velocity excess: 0.0000 rad/s

c2_163840:
  seed 0 tracking p95: 0.2044 rad
  seed 1 tracking p95: 0.1941 rad
  mean track ratio: 0.4070
  velocity excess: 0.0000 rad/s
```

The remaining Stage C miss is small and localized: upright behavior and
corrected velocity-envelope compliance are preserved, but terrain-induced
joint-target tracking, most visibly on seed 0 / left knee in the short screen,
stays just above the `0.20 rad` strict gate. Robot validation remains blocked
for terrain robustness; no robot, SSH, deploy, or grounded replay was performed
for these Phase 2 terrain runs.

Follow-up instrumentation added passive terrain clearance/support metrics to
the offline evaluator:

```text
artifact: outputs/analysis/PHASE2_STAGE_C_TERRAIN_CLEARANCE_INSTRUMENTATION.md
screen: outputs/analysis/PHASE2_STAGE_C_TERRAIN_Z002_CLEARANCE_SCREEN_CPU.md
status: PASS_CLEARANCE_METRICS_ADDED
```

Focused seed-0 `z=0.002` terrain comparison shows the terrain gait is a
low-clearance shuffle:

```text
a2_gain099:
  min swing peak lift: 0.0153 m
  single support: 17.6%
  double support: 82.4%

c0_245760:
  min swing peak lift: 0.0159 m
  single support: 16.8%
  double support: 83.2%

c2_163840:
  min swing peak lift: 0.0163 m
  single support: 17.2%
  double support: 82.8%
```

This matches the carpet observation: the policy is stepping but barely lifting.
The next terrain robustness step should explicitly increase swing clearance and
reduce double-support dwell while preserving the corrected actuator envelope and
command-conditioned forward motion.

Stage C3 then tested contact-timing pressure directly:

```text
artifact: outputs/analysis/PHASE2_STAGE_C3_CONTACT_TIMING_DECISION.md
screen: outputs/analysis/PHASE2_STAGE_C3_TERRAIN_Z002_SCREEN_CPU.md
status: HOLD_STAGE_C3_CONTACT_TIMING_NOT_ENOUGH
```

C3 warm-started from the best C2 terrain checkpoint and added forward
single-support, double-support dwell, and contact-transition reward pressure.
The best screened checkpoint, `c3_245760`, improved support timing but still
did not promote:

```text
tracking p95: 0.2046 rad
track ratio: 0.4061
velocity excess: 0.0000 rad/s
min swing peak lift: 0.0165 m
single support: 20.8%
double support: 79.2%
```

Contact timing alone is therefore insufficient. The next offline terrain
robustness step should add an explicit swing-clearance / feet-height objective
or target-source change while preserving the corrected actuator envelope and
the flat-ground command-conditioned gait. No robot, SSH, deploy, runtime change,
or grounded replay was performed for C3.

Stage C4 clearance-reward plumbing was added after that C3 hold:

```text
artifact: outputs/analysis/PHASE2_STAGE_C4_CLEARANCE_REWARD_PLUMBING.md
status: PASS_CLEARANCE_REWARD_PLUMBING
```

The new default-off `forward_swing_clearance` term measures per-foot swing peak
lift above the last stance height, so it is suitable for heightfield terrain.
The Playground runner and RDK training wrapper expose matching flags, and a
tiny CPU smoke plus direct one-step env check passed. This is only plumbing; no
candidate was promoted and no robot-side work was performed.

C4 then tested the clearance objective from the best C3 checkpoint:

```text
artifact: outputs/analysis/PHASE2_STAGE_C4_CLEARANCE_DECISION.md
screen: outputs/analysis/PHASE2_STAGE_C4_TERRAIN_Z002_SCREEN_CPU.md
status: HOLD_STAGE_C4_CLEARANCE_OVERDRIVES_GAIT
```

The final `c4_245760` checkpoint raised single-support time but destroyed the
gait: it fell after 33 samples, moved backward, and exceeded the corrected
velocity envelope. A weaker C4b retry did not reach training because local ROCm
failed with `rocblas_status_internal_error` during JAX evaluator reset. The
next terrain attempt should use a staged/gentler clearance objective plus
stronger gait-preservation pressure, and should treat repeated local ROCm
failures as backend holds rather than policy results.

C5a tested that gentler clearance direction with restore-policy KL:

```text
artifact: outputs/analysis/PHASE2_STAGE_C5A_CLEARANCE_PRESERVE_DECISION.md
screen: outputs/analysis/PHASE2_STAGE_C5A_TERRAIN_Z002_SCREEN_CPU.md
status: HOLD_STAGE_C5A_RETREATS_TO_DOUBLE_SUPPORT
```

Local ROCm failed twice after C4 with `rocblas_status_internal_error` during
JAX evaluator reset. A basic JAX matmul still passed, and C5a completed after
setting:

```text
XLA_FLAGS=--xla_gpu_autotune_level=0
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

C5a stayed stable and in-envelope, but regressed into more double support and
less forward progress:

```text
tracking p95: 0.1946 rad
track ratio: 0.2220
velocity excess: 0.0000 rad/s
min swing peak lift: 0.0086 m
single support: 9.6%
double support: 90.4%
```

The terrain reward issue is now sharper: a touchdown clearance penalty can be
avoided by reducing swing/transition behavior. The next offline attempt should
pair very weak clearance pressure with stronger transition/single-support
pressure and moderate gait preservation.

Stage C8/C9 and follow-up diagnostics narrowed the terrain blocker further:

```text
C8 swing-balance scalar pressure: HOLD
global action-gain diagnostic 1.05/1.10: HOLD
C9 forward swing-advance scalar pressure: HOLD
rough-terrain foot-placement MPC preflight: HOLD_TERRAIN_TARGET_SOURCE_NOT_READY
```

C9 confirmed the forward-swing-advance reward hook is plumbed and trainable,
but trained checkpoints retreated into low progress and failed to recover the
planted seed. The action-gain diagnostic stayed in-envelope but worsened
progress, so global amplitude is not the carpet fix. A bounded rough-terrain
MPC teacher preflight also failed the target-source gate: it was actuator-safe
and laterally calm, but produced only `0.003-0.008 m/s` forward speed and
remained double-support / single-contact-pattern dominated. The updated
target-source scorer now includes optional hard step-transition gates. Under
those gates, seed 2 produced one tiny swing segment, but seed 4 stayed planted
with `0` swing segments, `0.0000 m` rel-x range, and no measured swing peak
lift.

Current Phase 2 interpretation: the blocker is target manifold / stepping
structure. The next offline branch should require per-foot swing segments,
forward relative-foot excursion, touchdown advance, and balanced support as
hard target-source gates before more PPO/BC. Robot validation remains blocked.

A follow-up C7 terrain-height threshold check at `terrain_hfield_z_scale=0.001`
kept the same conclusion. Seed 2 passed the hard swing gate, but seed 4 still
failed with `0` swing segments and `0.0000 m` rel-x range. The carpet-like
failure is therefore not just that `z=0.002` is too high; the current gait has a
seed-dependent planted-foot mode that survives gentler terrain.

The next Phase 2 branch is pre-registered in
`docs/PHASE2_NEXT_TERRAIN_STEP_BRANCH.md`: no more scalar terrain reward sweeps
until a source/candidate clears a hard per-foot step-transition gate. The
immediate target is eliminating the seed-4 planted-foot mode offline.

The first existing-trace hard-step rescore found a flat fitted-bridge source:
live-oracle DAgger iteration 1 contains 100-tick seed `2,4` windows with
`0.054-0.057 m/s` forward speed, `2.225-2.229 rad/s` sent target p95, tracking
p95 near `0.181 rad`, and per-foot swing segments. This is recorded in
`outputs/analysis/PHASE2_EXISTING_TRACE_HARD_STEP_SOURCE_RESCORE.md`.
However, the live-oracle iteration 0 candidate did not transfer to
`rough_terrain_backlash` at `z=0.001`: both seeds completed 5 seconds and
stepped, but exceeded the corrected per-joint envelope and tracking gate
(`3.57-3.58 rad/s` max pitch velocity p95 and `0.254-0.259 rad` tracking p95).
That transfer hold is recorded in
`outputs/analysis/PHASE2_LIVE_ORACLE_ITER0_TERRAIN_Z001_SWING_GATE_CPU.md`.
Window-level rescoring then found terrain-safe hard-step source windows in the
same live-oracle terrain traces:

```text
z=0.001: seed 2/4 windows at 0.049-0.056 m/s, sent vel p95 1.998-2.189,
         tracking p95 0.171-0.176
z=0.002: seed 2/4 windows at 0.053-0.056 m/s, sent vel p95 2.090-2.219,
         tracking p95 0.170-0.179
```

Artifacts:

- `outputs/analysis/PHASE2_LIVE_ORACLE_ITER0_TERRAIN_Z001_WINDOW_SOURCE_SCORE.md`
- `outputs/analysis/PHASE2_LIVE_ORACLE_ITER0_TERRAIN_Z002_WINDOW_SOURCE_SCORE.md`

Current state: terrain-safe source windows exist at `z=0.001` and `z=0.002`,
but the full candidate policy still fails the rough-terrain envelope/tracking
gate. Next step is a curated terrain-window source manifest or live-oracle
relabel pass, not robot validation.

The curated manifest is now pinned as:

```text
outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_SOURCE_MANIFEST.md
outputs/analysis/phase2_terrain_safe_hard_step_source_manifest.json
source_policy_sha256: f3492159a775b0e0f73a25cf528b84ae202c16d5b2ba2f1344f7b7256e4e7261
```

A small PPO-loc BC smoke trained from four curated terrain slices fit the source
actions tightly, but failed closed-loop on `z=0.002`:

```text
fit: PASS_PPO_LOC_BC_FIT_SMOKE, p95 action error 0.008626
gate: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 2/4 vx: 0.0048 / 0.0059 m/s
seed 2/4 max velocity excess: 2.7400 / 2.7400 rad/s
```

This is the same compression failure seen earlier: source windows exist, but a
small memoryless BC student does not preserve them in closed loop. The next
offline step should use live relabel/DAgger or memory/phase conditioning rather
than promoting this BC candidate.

A small recurrent BC diagnostic on the same four windows also failed:

```text
fit: PASS_RECURRENT_BC_FIT_SMOKE, p95 action error 0.040416
gate: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 2/4 fall samples: 84 / 46
seed 2/4 mean vx: -0.1820 / -0.3372 m/s
```

Current interpretation: the curated terrain windows are useful source material,
but a tiny static dataset is not enough. The next offline branch should collect
live/on-policy relabel coverage from terrain states or build a larger
terrain-window dataset before another student promotion attempt.

That live/on-policy relabel branch was run for three bounded offline iterations
after extending `tools/run_live_oracle_dagger_iteration.py` with terrain hfield
and hard swing-gate arguments. The result is recorded in
`outputs/analysis/PHASE2_TERRAIN_LIVE_ORACLE_DAGGER_DECISION.md`:

```text
status: HOLD_TERRAIN_LIVE_ORACLE_DAGGER_TRACKING_PLATEAU
iter 0: low-progress/freeze remains
iter 1: progress recovers, tracking/envelope holds
iter 2: vx 0.0459-0.0526 m/s, track ratio 0.5736-0.6570,
        velocity excess 0.8704-0.8938 rad/s,
        tracking p95 0.2527-0.2533 rad
```

Current state: terrain-safe source windows exist and live DAgger can recover
forward progress, but the relabeled student still exceeds the corrected terrain
tracking/envelope gate. The next offline step should make oracle labels
tracking-aware, not repeat the same relabel loop and not run robot validation.

A first tracking-aware label-rate filter was then tested offline. It clipped
pitch-chain oracle labels to `2.25 rad/s`, trained a smooth PPO-compatible BC
student, and ran the same `rough_terrain_backlash` `z=0.002` gate on seeds
`2,4`. The result is recorded in
`outputs/analysis/PHASE2_TERRAIN_TRACKING_AWARE_LABEL_DECISION.md`:

```text
status: HOLD_TRACKING_AWARE_LABEL_FILTER_FREEZES
seed 2/4 vx: 0.0107 / 0.0105 m/s
seed 2/4 track ratio: 0.1335 / 0.1314
seed 2/4 double support: 90% / 96%
```

This reduced velocity excess/tracking pressure but removed the swing/advance
needed for terrain progress. The next offline branch must preserve transition
structure while enforcing the corrected per-joint envelope; simple global label
smoothing is closed. Robot validation remains blocked.

Trace comparison made that failure mode explicit:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_TRACKING_AWARE_TRACE_COMPARISON.md
iter2 seed 2/4 single support: 35.2% / 30.4%
filtered seed 2/4 single support: 10.0% / 4.0%
```

The next branch is pre-registered in
`docs/PHASE2_TRANSITION_PRESERVING_TERRAIN_BRANCH.md`: preserve the support
transition and apply corrected-envelope pressure in closed-loop, rather than
globally smoothing labels before the policy ever steps.

A PPO-shaped warm-start for that branch was then built from the live-oracle
iter2 aggregate:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_PPO_SHAPE_WARMSTART_DECISION.md
status: PASS_TRANSITION_PRESERVING_PPO_WARMSTART_READY
step0 ONNX: outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0.onnx
local checkpoint: outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0_checkpoint
```

The exported step-0 policy preserves rough-terrain forward transition behavior
but still holds on tracking/envelope, which is exactly the target for the next
offline PPO fine-tune:

```text
seed 2/4 track ratio: 0.6652 / 0.5947
seed 2/4 single support: 38.4% / 32.0%
seed 2/4 max tracking p95: 0.2598 / 0.2533
```

Tiny PPO fine-tune smokes from that restore point were then run on CPU. The
restore/export path works, but both scalar reward-side recipes erased the
support transition after only 80 timesteps:

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PRESERVING_PPO_SMOKE_DECISION.md
status: HOLD_REWARD_PPO_ERODES_SUPPORT_TRANSITION
normal trust-region seed 2/4 track ratio: 0.0516 / 0.1115
normal trust-region seed 2/4 double support: 96.8% / 99.2%
lockdown trust-region seed 2/4 track ratio: 0.0548 / 0.1181
lockdown trust-region seed 2/4 double support: 96.8% / 98.0%
```

The apparent tracking improvement came from stopping the step, not from learning
a terrain-safe in-envelope gait. Longer runs of the same scalar reward-PPO
recipe are closed. The next offline branch should preserve transition labels
directly, either through transition-aware relabeling or explicit action-space
correction. Robot validation remains blocked.

That transition-aware relabel branch was then tested by protecting all
non-double-support samples and a 6-tick window around contact transitions, while
rate-limiting only sustained double-support pitch-chain labels:

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_RATE_LIMIT_DECISION.md
status: PARTIAL_PASS_TRACKING_PLATEAU_BROKEN_HOLD_SEED4_SWING
label curation changed ticks: 13 / 500
changed contact counts: {'11': 13}
```

The resulting diagnostic BC student broke the terrain tracking/envelope plateau:

```text
rough z=0.002 seed 2: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.3641
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1876 rad

rough z=0.002 seed 4: HOLD_CANDIDATE_TERRAIN_SWING
  track ratio: 0.3184
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1914 rad
```

This is not deployable yet. Seed 4 still lacks the required swing/advance
segments, but the rough-terrain blocker has narrowed from tracking/envelope to
seed-4 swing preservation. The next offline branch should keep
transition-protected rate limiting and add seed-balanced swing/advance or
contact-phase-balanced label weighting. Robot validation remains blocked.

A simple seed-4 weighted follow-up was then run:

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_SEED4_WEIGHTED_DECISION.md
status: HOLD_SEED_WEIGHTING_REINTRODUCES_TRACKING_EXCESS
seed 2/4 track ratio: 0.5112 / 0.4184
seed 2/4 max velocity excess: 0.2465 / 0.2935 rad/s
seed 2/4 max tracking p95: 0.2202 / 0.2222 rad
seed 2/4 min swing segments: 7 / 6
```

This proves seed weighting can restore swing/advance, but it does so by
reintroducing the corrected-envelope/tracking failure. Naive weighting is
closed. The next offline branch needs contact-phase-balanced or action-space
correction that preserves the swing gain while keeping zero velocity excess and
tracking p95 under `0.20 rad`. Robot validation remains blocked.

A scalar supervised rate-penalty sweep on the seed-weighted manifest was also
run:

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_SEED4_WEIGHTED_RATE_SWEEP_DECISION.md
status: HOLD_RATE_REGULARIZATION_SWING_TRACKING_TRADEOFF
rate 0.08 seed 2/4 max velocity excess: 0.0822 / 0.1252 rad/s
rate 0.08 seed 2/4 max tracking p95: 0.2024 / 0.2067 rad
rate 0.08 seed 2/4 min swing segments: 7 / 0
rate 0.20 seed 2/4 max velocity excess: 0.0314 / 0.0943 rad/s
rate 0.20 seed 2/4 max tracking p95: 0.2083 / 0.2113 rad
rate 0.20 seed 2/4 min swing segments: 4 / 0
```

Rate regularization reduces excess but again erodes seed-4 swing. This closes
the simple sample-weight plus scalar rate-penalty family. The next offline
branch should target contact-phase-balanced labels or selective per-contact /
per-joint action-space correction.

Selective per-joint action-space correction was then tested on the seed-weighted
traces:

```text
artifact: outputs/analysis/PHASE2_ACTION_SPACE_COMMAND_CONDITIONING_DECISION.md
status: PARTIAL_PASS_ACTION_SPACE_CORRECTION_HOLD_COMMAND_CONDITIONED_SWING
corrected joints: right_knee 2.25, right_ankle 2.00, left_knee 2.25 rad/s
```

The plain feed-forward student trained from corrected x=0.08 labels passed the
rough `z=0.002` diagnostic gate on seeds 2 and 4:

```text
seed 2/4 track ratio: 0.4784 / 0.4738
seed 2/4 max velocity excess: 0.0000 / 0.0000 rad/s
seed 2/4 max tracking p95: 0.1989 / 0.1913 rad
seed 2/4 min swing segments: 6 / 6
```

It is not promotable because it walks on x=0.0:

```text
seed 2/4 x=0.0 mean vx: 0.0442 / 0.0369 m/s
```

Plain mixed-command BC collapsed x=0.08 forward progress, while a
phase/command-modulated student preserved x=0 command semantics but still held
on seed-4 swing at x=0.08. The blocker has narrowed again: combine the
three-joint corrected x=0.08 swing behavior with explicit command conditioning.
Robot validation remains blocked.

A focused phase/command seed-4 weighting follow-up was then run:

```text
artifact: outputs/analysis/PHASE2_PHASECMD_SEED4_WEIGHTING_DECISION.md
status: HOLD_SCALAR_SEED4_WEIGHTING_EXHAUSTED
```

The x2.5 seed-4 moving-label weight preserved zero-command behavior and nearly
cleared rough `z=0.002` at x=0.08:

```text
seed 2: PASS, vx 0.0352, tracking 0.1881, excess 0.0000, rel-x 0.0048
seed 4: HOLD_CANDIDATE_TERRAIN_SWING, vx 0.0329, tracking 0.1887,
        excess 0.0000, rel-x 0.0029 against a 0.0030 threshold
x=0.0 seed 2/4 vx: -0.0015 / 0.0026 m/s
```

Increasing the same scalar seed-4 weight to x4.0 improved seed 2 but removed
seed-4 swing entirely:

```text
seed 4 min swing segments: 0
seed 4 rel-x p95: 0.0000 m
```

The carpet hardware observation and the rough sim gate now agree: the remaining
blocker is insufficient seed-4 right-foot swing/forward advance, not corrected
envelope excess, actuator tracking, or zero-command drift. Global seed weighting
is closed; the next branch needs targeted right-foot swing-phase relabeling or
a contact/phase-conditioned architecture. Robot validation remains blocked.

The targeted right-foot swing-phase version then passed the local rough
diagnostic:

```text
artifact: outputs/analysis/PHASE2_RIGHT_SWING_TARGETED_WEIGHTING_DECISION.md
status: PASS_LOCAL_RIGHT_SWING_TARGETED_DIAGNOSTIC
weighted rows: seed-4 contact-code 10 only, 18/250 samples, weight 6.0
```

Results:

```text
x=0.08 rough z=0.002 seed 2: PASS
  vx 0.0409, track ratio 0.5114, excess 0.0000, tracking 0.1922,
  swing segments 6, rel-x 0.0131

x=0.08 rough z=0.002 seed 4: PASS
  vx 0.0341, track ratio 0.4269, excess 0.0000, tracking 0.1952,
  swing segments 2, rel-x 0.0064

x=0.0 rough z=0.002 seed 2/4 vx: -0.0013 / 0.0032 m/s
```

This is the first local rough-terrain command-conditioned pass that preserves
the corrected envelope, tracking, x=0.0 semantics, and seed-4 swing/advance.
It is not promoted yet; it must now pass the wider 8-seed rough diagnostic and
then the canonical corrected-bridge gates. Robot validation remains blocked.

The wider rough diagnostic and first live-oracle follow-up were then run:

```text
artifact: outputs/analysis/PHASE2_LIVE_ORACLE_RIGHT_SWING_ITER1_DECISION.md
status: HOLD_LIVE_ORACLE_ITER1_MIXED_IMPROVEMENT
```

Targeted right-swing candidate at x=0.08 rough `z=0.002`:

```text
passes: seeds 2,4,6
low-progress holds: seeds 0,1,5,7
target-velocity hold: seed 3
falls: 0/8
```

Live-oracle iter1 relabeling produced 3250 aggregate samples and improved the
distribution:

```text
passes: seeds 1,2,3,6,7
terrain-swing holds: seeds 0,4
fall/reverse hold: seed 5
```

This is useful but not promotable. Live-oracle labels can fix low-progress and
velocity-excess seeds, but flat aggregation can also erase the seed-4 targeted
right-swing fix and introduce a seed-5 reverse/fall. The next iteration should
preserve seed-4 right-swing labels and inspect/filter seed-5 before another
student fit. Robot validation remains blocked.

A selective live-oracle aggregate was also tested:

```text
artifact: outputs/analysis/PHASE2_LIVE_ORACLE_RIGHT_SWING_ITER1_SELECTIVE_DECISION.md
status: HOLD_SELECTIVE_AGGREGATE_NOT_SUFFICIENT
excluded live x=0.08 seeds: 4,5
kept entries: 11
```

It did not solve the regression:

```text
passes: seeds 1,2
terrain-swing hold: seed 0
target-velocity hold: seed 3
tracking holds: seeds 4,6,7
fall/reverse hold: seed 5
```

This closes flat aggregate entry selection. The next useful sim-side move is
per-record/per-phase filtering: cap/filter the seed-5 right-ankle reverse/fall
burst while preserving the targeted seed-4 right-swing rows. Robot validation
remains blocked.

The first per-record seed-5 cap/downweight branch was tested:

```text
artifact: outputs/analysis/PHASE2_LIVE_ORACLE_RIGHT_SWING_ITER1_SEED5_CAPPED_DECISION.md
status: HOLD_SEED5_CAPPED_NOT_SUFFICIENT
x=0.08 rough z=0.002: 6/8 pass
x=0.0 rough z=0.002: 7/8 pass
remaining failing seed: 5
```

This branch capped four seed-5 right-ankle label deltas and downweighted the
seed-5 reverse/fall tail. It improved the rough x=0.08 distribution relative
to flat selective aggregation: seed 3 and seed 4 passed, and only seed 0
terrain-swing plus seed 5 fall remained. However, seed 5 still fell at x=0.08
and also fell at x=0.0, so the right-ankle burst is not the full mechanism.

The next useful branch should collect and compare full-observation seed-5
traces at x=0.0 and x=0.08 against passing neighboring seeds 4 and 6. Do not
continue tail-only caps or flat aggregate variants. Robot validation remains
blocked.

That comparison is now recorded:

```text
artifact: outputs/analysis/PHASE2_SEED5_CAPPED_NEIGHBOR_TRACE_DIVERGENCE.md
status: PASS_TRACE_DIVERGENCE_CHARACTERIZED
```

Seed 5 diverges early from passing neighbor seeds 4 and 6. At x=0.08,
contact/support differs at tick 0, pitch-chain sent/action velocity exceeds
2.5 rad/s at tick 1, velocity turns negative by tick 10, pitch divergence
appears by tick 25, and height collapse does not begin until about tick 51. At
x=0.0, seed 5 also falls: support differs at tick 0, pitch-chain rate exceeds
2.5 rad/s at tick 1, pitch divergence appears by tick 18, and height collapse
follows around tick 37.

This means seed 5 is a command-independent early-state stability mode, not a
tail-only right-ankle label-rate problem. The next correction should emphasize
early seed-5 states before pitch divergence and gate x=0.0 plus x=0.08
together. Robot validation remains blocked.

The first early-state weighted BC correction was tested:

```text
artifact: outputs/analysis/PHASE2_SEED5_EARLY_STATE_DECISION.md
status: HOLD_SEED5_EARLY_STATE_BC_NOT_SUFFICIENT
x=0.08 rough z=0.002: 4/8 pass
x=0.0 rough z=0.002: 7/8 pass
```

The branch relabelled only seed5 early states before pitch divergence, capped
pitch-chain label rates at 2.25 rad/s equivalent, and weighted those early
records 10x. Seed 5 still fell at both x=0.08 and x=0.0, and x=0.08 pass seeds
0, 1, and 6 regressed into tracking holds.

This closes two local seed5 fixes:

```text
tail-only cap/downweight: partial improvement, seed5 still falls
early-state weighted BC: seed5 still falls, other seeds regress
```

The next useful branch should change the correction mechanism rather than
increase scalar weights: frame-stack/recurrent state, or a recovery teacher
that changes seed5's first contact transition. Robot validation remains
blocked.

The cheapest deployable representation change was tested:

```text
artifact: outputs/analysis/PHASE2_SEED5_EARLY_STATE_CONTACTPHASE_DECISION.md
status: HOLD_CONTACTPHASE_SEED5_STILL_FALLS
context: obs[6,97,98,99,100]
x=0.08 rough z=0.002: 5/8 pass
x=0.0 rough z=0.002 seed 5: fall at 43 samples
```

Adding foot-contact bits to the phase/command-modulated feed-forward student
preserved several rough-terrain passes but did not recover seed 5. Seed 5 still
falls at both positive and zero command, so the remaining terrain blocker is
not solved by minor feed-forward context changes. The next useful offline
branch is explicit state/history or a recovery teacher that changes seed 5's
first contact transition. Robot validation remains blocked.
