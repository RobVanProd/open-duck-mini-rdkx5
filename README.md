# Open Duck Mini RDK-X5 Runtime And Sim-To-Real Diagnostics

Private working repository for the Open Duck Mini RDK-X5 board runtime, robot-specific calibration evidence, and non-invasive sim-to-real diagnostic tooling.

This repository exists because the live board runtime at `/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5` is an RDK-X5 fork and is not a git repository. The goal is to preserve the exact board-side runtime and make diagnostics reproducible before changing training, gains, offsets, IMU remaps, friction, phase timing, or policy behavior.

The repository and its documentation are part of the robot's working state. Keep them current when the board runtime, config, evidence, analysis results, or next diagnostic gate changes.

## Current Next Step

The ground-up RDK-X5 runtime has cleared the supported, no-policy hardware
gates through Gate 4. Policy work remains offline and Gate 5 remains closed.

The completed T1 accelerometer-bias dose response proves that the robot's
upright `accel_x` mismatch is behaviorally first-order: `+1.6 m/s^2` reduced
the unmodified baseline's simulated forward velocity by `86.41%`. T2 is held
because the exact corrected-replay raw JSONL is unavailable. T4 is complete
and independently audited: all `32/32` baseline cells, cell contracts, raw
result hashes, aggregates, and gate rows reproduce exactly. The baseline
finishes all cells without a fall but fails `13` current gate rows. Under the
preregistered decision rule, a gate the baseline fails cannot remain a minimum
feasibility boundary unless it is relaxed to baseline evidence; it may instead
remain explicitly labeled as a stretch goal. T4 makes no automatic gate
change.

The read-only T5 protection-envelope audit changed the policy decision
boundary. Feetech documents duration-triggered over-current and overload
protection, not a one-tick rejection at stall torque/current. When the frozen
V121, V123, and V128 traces are reclassified using the documented two-second
rules, all three become complete `16/16` nominal passes. V177 also becomes
`16/16` as a post-handoff diagnostic.

T6 then tested all four reopened frozen policy pairs against the prospectively
selected R2 `TORSO_COM_X_NEG` endpoint (`-0.05 m`), which was the first
configuration failure of the prior winner. The complete `64/64` CPU matrix has
no robust survivor: V121, V123, and V128 score `0/16`; V177 scores `1/16`.
All four have negative worst-case moving velocity, while their worst strict
over-current/overload runs are only `3`–`5` ticks against the corrected
`100`-tick trip rule. An independent auditor reproduced all `16` manifests,
`16` evaluations, `64` trace hashes, `64` exact COM readbacks, every aggregate,
and the final decision with zero issues. The frozen-policy comparison is
closed.

T7 then found and prospectively tested a concrete mismatch in the older
response-conditioned campaign. Training generated its response context while
commanding the frozen V91 universal support target, but the formal V103
evaluator executed the calibrator ONNX action head instead. T7 ran the actual
universal-target graph on the exact current composed stack for nominal and
`±0.05 m` torso-COM, both actuator fits, and two independent repeats:
`12/12` cells pass 600-tick support, corrected servo protection, action/state
chaining, exact model readback, and response-signal gates. Repeats are
bit-exact; signed COM context separation is `0.156809`/`0.156854`, above the
frozen `0.15` threshold. The independent audit reports zero issues. This earns
only a zero-training, state-coherent support-to-locomotion handoff screen; no
hosted training is yet earned.

T8 completed that handoff screen. Both V121 checkpoints, both measured
actuator fits, and all three moving commands pass: `12/12` moving cells are
full 600-tick walks with tracking p95 at most `0.151526 rad`, positive
body-frame velocity, zero saturation/rate excess, corrected servo protection,
and exact response/recurrent/applied-target state continuity. The four x=0
cells are stable, stationary, and otherwise green, but fail one frozen
quantity at scored tick 0. The exact-zero deadband action follows the universal
support action directly, producing a one-tick six-joint rate-envelope excess
up to `3.989999 rad/s`; ticks 1–599 have zero excess. T8 therefore holds
`12/16` and earns no training. A corrected independent audit passes with zero
issues after preserving and fixing a reporting-only world-X/body-frame error
that could not change the hold.

Current gate:

```text
HOLD_GATE_5_PENDING_COMMAND_AWARE_X0_PREFIX_BYPASS_CPU_SCREEN
```

Read these first:

```text
PROJECT_GOAL.md
outputs/analysis/T1_ACCEL_BIAS_V4_DOSE_RESPONSE_RESULT_20260725.md
outputs/analysis/T4_BASELINE_ALL_GATES_RESULT_20260725.md
outputs/analysis/T5_ACTUATOR_PROTECTION_REANALYSIS_RESULT_20260725.md
outputs/analysis/T6_CORRECTED_ROBUSTNESS_SCREEN_RESULT_20260725.md
outputs/analysis/T6_CORRECTED_ROBUSTNESS_SCREEN_INDEPENDENT_AUDIT_20260725.md
outputs/analysis/T7_UNIVERSAL_RESPONSE_SUPPORT_RESULT_20260725.md
outputs/analysis/T7_UNIVERSAL_RESPONSE_SUPPORT_INDEPENDENT_AUDIT_20260725.md
outputs/analysis/T8_STATE_COHERENT_HANDOFF_RESULT_20260726.md
outputs/analysis/T8_STATE_COHERENT_HANDOFF_INDEPENDENT_AUDIT_V2_20260726.md
outputs/analysis/T8_STATE_COHERENT_HANDOFF_FAILURE_ANALYSIS_20260726.md
outputs/analysis/WINNER_V177_NOMINAL_BEHAVIOR_RESULT_20260725.md
```

The next earned falsifier is a separately preregistered, CPU-only,
zero-training command-aware startup screen. While paused/x=0, the robot remains
at home and bypasses response excitation because the frozen deadband output is
context-independent exact zero. Moving commands retain the already-green T8
direct handoff from universal support. Four new x=0 cells are required; the
twelve immutable audited T8 moving cells are reused without rerunning them.
The mechanism continues to infer configuration only from runtime-available
signals and requires no weighing, calipers, or static COM entry. No Colab
continuation is authorized until this branch and a subsequent CPU contract
explicitly earn one.

Current candidate:

```text
NONE_SELECTED_FOR_RDK_OR_GATE_5
```

Do not tune hardware gains, patch IMU remaps, edit offsets, change action

Primary docs:

- [Project goal](PROJECT_GOAL.md)
- [Project findings](docs/PROJECT_FINDINGS.md)
- [Roadmap](ROADMAP.md)
- [Weight-transfer target plan](docs/WEIGHT_TRANSFER_TARGET_PLAN.md)
- [Safety rules](docs/SAFETY_RULES.md)
- [Evidence flow](docs/EVIDENCE_FLOW.md)
- [Issue backlog](docs/ISSUE_BACKLOG.md)
- [Roboticist playbook](docs/ROBOTICIST_PLAYBOOK.md)
- [Deploy instrumentation](docs/DEPLOY_INSTRUMENTATION.md)
- [Diagnostic runbook](docs/run_sim2real_diagnostics.md)
- [Training actuator wrapper workflow](docs/TRAINING_ACTUATOR_WRAPPER_WORKFLOW.md)
- [Candidate policy validation gates](docs/CANDIDATE_POLICY_VALIDATION_GATES.md)
- [CUDA backend training runbook](docs/CUDA_BACKEND_TRAINING_RUNBOOK.md)
- [CUDA / Colab single cell](docs/CUDA_COLAB_SINGLE_CELL.md)
- [Diagnostic thresholds](docs/DIAGNOSTIC_THRESHOLDS.md)
- [Agent instructions](AGENTS.md)

## Current Board State

- Board: D-Robotics RDK-X5, hostname `ubuntu`
- Current SSH target: `sunrise@192.168.1.50`
- Runtime on board: `/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5`
- Python env on board: `/home/sunrise/duck_env/bin/python`
- Policy: `/home/sunrise/BEST_WALK_ONNX_2.onnx`
- Policy SHA256: `3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067`
- `imu_upside_down`: `true`
- `start_paused`: `true`
- IMU calibration pickle: not found in the snapshot search paths

The exact live config snapshot is in `evidence/20260621T180046Z_rdkx5_config_snapshot.json`.

## Repository Layout

```text
runtime/                 Board RDK-X5 runtime copied from the robot
instrumentation/         Additive diagnostic files to deploy into runtime/
tools/                   Workstation analysis and snapshot utilities
docs/                    Audit, runbook, telemetry schema, joint map, test plan
evidence/                Captured board config and calibration evidence
policy/                  Matching BEST_WALK_ONNX_2 baseline policy
```

## Safety Rules

- Do not run walking tests until home pose, IMU tilt, foot contact, joint identity, and suspended replay checks pass.
- Do not run suspended replay unless `v2_rl_walk_mujoco.py` exposes opt-in telemetry support and the replay command writes JSONL telemetry.
- Do not tune gains, offsets, action scale, friction, phase timing, IMU remaps, or policy code during evidence collection.
- Any moving diagnostic must be run with the robot physically supported unless the test explicitly says grounded.
- Keep fingers clear and be ready to cut power.
- Moving diagnostics require an explicit safety flag in the command.

## Diagnostic Gate Order

Run this order. Stop immediately if a gate fails.

```text
1. snapshot_robot_config
2. home_pose_log_test
3. analyze home pose log
4. imu_tilt_test
5. analyze IMU tilt log
6. foot_contact_test
7. joint_identity_test
8. suspended_policy_replay, x = 0.0
9. suspended_policy_replay, x = 0.08 only if x = 0.0 looks sane
10. push test
11. grounded_policy_replay
12. actuator_sine_sweep
```

The first strict gate is upright acceleration:

```text
obs[3:6] should be roughly [small, small, +9.5]
```

Expected ONNX accel means:

```text
obs[3] accel_x ~= -0.037894
obs[4] accel_y ~= -0.079717
obs[5] accel_z ~=  9.490142
```

Suspended replay evidence must include both JSONL telemetry and terminal log
capture so servo CRC/read warnings and control-budget warnings are visible in
the gate summary before increasing command speed.

CRC/read retry warnings are not an automatic stop. The suspended replay gate
holds only when they correlate with control damage such as dt spikes, action
saturation or jumps, post-startup tracking spikes, write failures, visible
twitching, or a read-error burst. Otherwise the gate reports
`WARN_PROCEED_WITH_CAUTION` and the next low-risk suspended command can be
considered.

## Key Live Calibration Facts

The live `duck_config.json` offsets are recorded in `evidence/duck_config_20260621T180046Z.json` and `docs/joint_map_template.yaml`.

Notable offsets:

```text
left_knee  -1.4880 rad
right_knee  0.0798 rad
```

This asymmetry may be legitimate after mechanical repair, but it must be verified by home-pose telemetry and `joint_identity_test`. Do not change it without evidence.

## Board Runtime Differences

The board runtime is not identical to the local upstream reference:

- `raw_imu.py` uses an RDK-compatible `I2CCompat` layer.
- `feet_contacts.py` uses `Hobot.GPIO` on RDK-X5.
- `rustypot_position_hwi.py` retries servo bus operations.
- `joints_dir` is all `+1.0`; no software sign flip is intended.

See `docs/SIM2REAL_AUDIT.md` for the full map.

## Deployment

Read `docs/DEPLOY_INSTRUMENTATION.md` before copying instrumentation to the board. The instrumentation is designed to be additive and disabled by default, but board runtime files should still be backed up before any overwrite.

Check the runtime telemetry contract locally before deploying:

```bash
python3 tools/check_runtime_telemetry_contract.py
```

Dry-run first:

```bash
bash scripts/deploy_instrumentation_to_duck.sh --dry-run
```

Apply only after the plan is reviewed:

```bash
bash scripts/deploy_instrumentation_to_duck.sh --apply
```

## Analysis

Use the workstation tools for analysis. The board Python env has `onnxruntime` but not `onnx`, so ONNX normalization extraction should usually run off-board.

```bash
python3 tools/analyze_telemetry_obs.py path/to/home_pose_log_test.jsonl \
  --onnx-model policy/BEST_WALK_ONNX_2.onnx
```

## What Not To Do Yet

- Do not retrain.
- Do not tune offsets.
- Do not patch IMU axes or offsets.
- Do not change action scale.
- Do not change gains.
- Do not change phase timing.
- Do not debug friction/TPU/contact until sensor/action/joint truth tables pass.
