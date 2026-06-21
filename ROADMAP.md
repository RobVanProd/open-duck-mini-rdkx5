# Roadmap

This roadmap is ordered to avoid tuning before evidence. Each phase has explicit gates. Do not advance to hardware walking until the earlier gates pass.

## Phase 0: Repo Safety And Evidence Hygiene

Goal: keep the RDK runtime, evidence, docs, tools, and policy baseline organized and reviewable.

Required evidence:

- Current board config snapshot.
- Policy hash match.
- Runtime path and package versions.
- Clear safety and evidence rules.
- RHO-inspired roboticist operating model.

Pass gates:

- No private SSH keys, known_hosts, raw huge logs, videos, or secrets in git.
- `docs/telemetry_schema.json` validates.
- Tools and instrumentation compile.
- Docs identify the current next diagnostic gate.

Files/scripts:

- `README.md`
- `PROJECT_GOAL.md`
- `ROADMAP.md`
- `docs/SAFETY_RULES.md`
- `docs/EVIDENCE_FLOW.md`
- `docs/ROBOTICIST_PLAYBOOK.md`
- `tools/snapshot_robot_config.py`

Do not change yet:

- Runtime behavior.
- Policy files.
- Robot config.
- Offsets, gains, remaps, action scale, phase timing.

## Phase 1: Static Observation Truth Tests

Goal: prove the stationary upright robot's observation vector matches the policy's expected world.

Required evidence:

- `home_pose_log_test` JSONL.
- Analyzer summary for `obs[0:6]`.
- Joint tracking p50/p95/p99.
- Bus error counts.
- Foot contact state while stationary.

Pass gates:

- Gyro near zero.
- Accelerometer roughly `[small, small, +9.5]`.
- Accel z-scores against ONNX normalization are reasonable.
- Joint tracking errors are small and stable.
- Bus errors are zero or explainably rare.

Files/scripts:

- `instrumentation/scripts/sim2real_diagnostics.py`
- `tools/analyze_telemetry_obs.py`
- `docs/run_sim2real_diagnostics.md`

Do not change yet:

- IMU offsets or remaps.
- Joint offsets.
- Walking policy behavior.

## Phase 2: IMU Frame/Offset Verification

Goal: map physical tilt directions to policy accelerometer axes and signs.

Required evidence:

- `imu_tilt_test` JSONL.
- Analyzer summary.
- Notes for upright, nose forward, nose backward, left tilt, right tilt.

Pass gates:

- Nose forward/back affects one accelerometer axis with opposite signs.
- Left/right tilt affects a different axis with opposite signs.
- Returning upright returns `obs[3:6]` near the original upright vector.
- `imu_upside_down=true` is supported by evidence.

Files/scripts:

- `instrumentation/scripts/sim2real_diagnostics.py`
- `tools/analyze_telemetry_obs.py`

Do not change yet:

- BNO055 axis remap.
- IMU bias/tare behavior.
- Policy observation builder.

## Phase 3: Joint Identity And Home Pose Verification

Goal: prove action index, joint name, servo ID, physical joint, sign, and readback match.

Required evidence:

- `joint_identity_test` JSONL.
- `joint_identity_test_summary.json`.
- Operator notes or video for physical positive direction.
- Home-pose tracking evidence for compensated readings.

Pass gates:

- Correct side and joint move for every index.
- Positive and negative commands produce expected measured deltas.
- Hip pitch, knee, and ankle joints respond symmetrically enough for policy replay.
- The large live `left_knee` offset is either validated or flagged as a root cause.

Files/scripts:

- `instrumentation/scripts/sim2real_diagnostics.py`
- `docs/joint_map_template.yaml`

Do not change yet:

- `duck_config.json`.
- `joints_dir`.
- Servo IDs.

## Phase 4: Suspended Policy Replay

Goal: run `BEST_WALK_ONNX_2` with the feet free to separate observation/action/joint issues from ground contact issues.

Required evidence:

- Runtime telemetry contract check passed.
- Opt-in walker telemetry patch deployed with a deployment summary.
- `suspended_policy_replay_x0.jsonl`.
- `suspended_policy_replay_x0_terminal.log`.
- `suspended_policy_replay_x0_gate.md`.
- Optional `suspended_policy_replay_x008.jsonl` only if `x=0.0` is sane.
- Analyzer summary.

Pass gates:

- Actions are bounded and not immediately saturated.
- Left/right motion is plausibly symmetric.
- Actual joints track targets.
- Bus errors do not burst during policy replay.
- Terminal CRC/read/control-budget warnings are captured and reviewed.
- HWI retry error counters are present in telemetry when deployed.
- The robot does not drive an obvious forward-biased posture in the air.
- Replay does not run if full runtime telemetry support is missing.
- Do not run `x=0.08` unless the `x=0.0` gate summary recommends `PASS_X0`.

Files/scripts:

- `instrumentation/scripts/sim2real_diagnostics.py`
- `runtime/scripts/v2_rl_walk_mujoco.py`
- `tools/analyze_telemetry_obs.py`
- `tools/check_runtime_telemetry_contract.py`
- `tools/analyze_runtime_warnings.py`
- `tools/analyze_suspended_replay.py`

Do not change yet:

- Ground contact parameters.
- TPU/friction assumptions.
- Training config.

## Phase 5: Grounded Replay And Failure Capture

Goal: capture the forward-fall failure with synchronized telemetry and side-view video.

Required evidence:

- `grounded_policy_replay.jsonl`.
- Analyzer summary.
- Final 3-5 seconds of JSONL before fall.
- Side-view video.

Pass/fail gates:

- Run only after Phases 1-4 pass.
- Stop immediately on large lean, fall, slip, asymmetry, or bus-error burst.
- Decide whether failure is contact/load related or still appears in observations/actions.

Files/scripts:

- `instrumentation/scripts/sim2real_diagnostics.py`
- `tools/analyze_telemetry_obs.py`

Do not change yet:

- Training.
- Friction tuning before replay evidence is reviewed.

## Phase 6: Minimal Patch Experiments

Goal: apply exactly one evidence-backed fix at a time.

Required evidence:

- Failed gate metric.
- Proposed patch.
- Before/after telemetry.

Pass gates:

- Patch addresses one root cause only.
- Default behavior remains reviewable.
- `BEST_WALK_ONNX_2` is rerun after the patch.

Files/scripts:

- Patch-specific.
- `SIM2REAL_RESULTS_SUMMARY.md`.

Do not change yet:

- Multiple variables at once.
- Training.

## Phase 7: Actuator System Identification

Goal: measure target-vs-actual tracking, lag, and asymmetry under controlled supported tests.

Required evidence:

- `actuator_sine_sweep` telemetry.
- Tracking error and phase lag per joint.

Pass gates:

- Hip pitch, knee, and ankle tracking are quantified.
- Any actuator lag or weak response is isolated before training changes.

Files/scripts:

- `instrumentation/scripts/sim2real_diagnostics.py`

Do not change yet:

- Sim actuator parameters without measured evidence.

## Phase 8: TPU/Contact Friction Prior And Randomized Sim Training

Goal: bridge contact/friction only after sensor/action/joint contracts pass.

Required evidence:

- Grounded replay evidence.
- Contact/slip analysis.
- Actuator tracking evidence.

Pass gates:

- Friction/contact is a leading root cause after earlier phases.
- Sim assumptions are updated from measurement, not guesses.

Files/scripts:

- Playground/training configs.
- Contact/friction test notes.

Do not change yet:

- Policy architecture without a measured reason.

## Phase 9: New Policy Training And Deployment

Goal: train and deploy a new policy after the real robot contract is understood.

Required evidence:

- Completed bridge gates.
- Updated sim assumptions.
- Known good diagnostic baseline.

Pass gates:

- Training changes are tied to measured sim-to-real gaps.
- Deployment uses the same telemetry gates as `BEST_WALK_ONNX_2`.

Files/scripts:

- Training repo/configs.
- Deployment runbook.

Do not change yet:

- Skip validation gates for new policies.
