# Live-Oracle DAgger Phase Student Spec

Status: `HOLD_ITER0_SOURCE_NEEDS_STRENGTHENING`

Branch ID: `LIVE_ORACLE_DAGGER_PHASE_STUDENT`

This branch supersedes `PLAN_GATE_AWARE_ROLLOUT_CORRECTION_OR_RECURRENT_STUDENT`.
It is offline-only until a candidate clears the strict canonical corrected
fitted-bridge gate. No robot test, SSH, deploy, hardware calibration write,
policy overwrite, or runtime behavior change is in scope for this branch.

## Objective

Distill a corrected-bridge source selector into a deployable policy that clears
the strict corrected fitted-bridge tracking gate by:

- querying the corrected selector as a live oracle on the student's own visited
  states at every iteration
- adding enough state/phase memory for the student to represent the
  stance-transition action that memoryless students have failed to reproduce

## Settled Evidence

- The source-VX selector proved in-envelope all-seed forward walking exists in
  sim under the old fitted actuator bridge.
- After the left-knee correction, the old bridge is deprecated. Future branch
  results must re-anchor on
  `outputs/analysis/actuator_response_fit_corrected_knee.json`.
- Corrected-bridge Step 1 found that the old `BEST_WALK_ONNX_2` source mostly
  violates the corrected per-joint envelope. Only `1/1030` mined short windows
  passed, and it was double-support-centered. The old source-VX selector is
  therefore historical evidence, not a valid live oracle for this branch.
- A corrected z=0.0024 rough-terrain source manifest now exists:
  `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
  (`d8498b665c201936`, 8 entries, 6000 samples, all BC-ready).
- z=0.005 live-oracle terrain-support iteration 0 completed data collection
  with corrected bridge and no robot/SSH/deploy/training:
  `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0_aggregate_manifest.json`
  (`3f68992af82062f7`, 18 entries, 12806 samples).
- Iteration 0 student fits have now been evaluated:
  `outputs/analysis/PHASE2_Z005_LIVE_ORACLE_ITER0_STUDENT_FIT_DECISION.md`.
  The phase/command-modulated feed-forward student fits cleanly and stays
  mostly in-envelope but under-progresses and still falls on seed 5. The
  recurrent H96 diagnostic is worse, falling on all seeds and hitting the
  simulator target-slew ceiling. Do not keep fitting the same aggregate with
  larger supervised models; the z=0.005 source/oracle must be strengthened
  before another live-oracle iteration is meaningful.
- A tiny seed-5 composite recovery BC smoke was also tested:
  `outputs/analysis/PHASE2_A2_SEED5_Z005_COMPOSITE_RECOVERY_BC_SMOKE_DECISION.md`.
  It fit 141 labels cleanly offline but failed the short closed-loop seed-5
  z=0.005 support gate with corrected-envelope velocity excess and high action
  saturation. This closes one-shot fixed BC on the composite recovery manifest;
  the next iteration must use live/on-policy recovery states with immediate
  short gates before scaling.
- The bounded seed-5 live/on-policy recovery DAgger precheck then produced
  `outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_ITER1_SEED5_SHORT_DECISION.md`.
  It generated a 6117-sample aggregate and fit a phase/command-modulated
  student, but the student still failed both short z=0.005 seed-5 gates before
  2 seconds. This means the current z=0.0024 source/oracle is still too weak
  for z=0.005 support recovery; do not scale iter1 or use it as a parent.
- Prior memoryless distillations, static DAgger passes, kNN/linear/blend
  students, and feed-forward PPO-shape students held at the same tracking
  plateau or froze.
- Reward-side PPO controls, including behavior prior, adaptive KL,
  progress-failure termination, restore-policy KL, and low-alpha weight blends,
  collapsed into standstill.
- Static relabel-then-freeze DAgger is closed. This branch must run a live
  loop: roll out the current student, query the oracle on those visited states,
  aggregate, retrain, and gate.
- The latest z=0.00245 A100 motion-recovery run completed on the pinned
  JAX/Brax stack and exported checkpoints at 40960, 81920, and 122880 steps,
  but the compact corrected-bridge checkpoint sweep held every checkpoint for
  low forward progress at `x=0.08`. The best checkpoint had track ratio
  `0.2339` and mean local `vx=0.0187 m/s`, below the compact promotion
  thresholds, while staying comfortably inside the corrected velocity envelope.
  This closes the small scalar-progress-pressure retry:
  `outputs/analysis/PHASE2_Z00245_MOTION_RECOVERY_A100_RESULT_20260702.md`.
- The strongest current z=0.0025 positive-motion source is
  `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`.
  It passed the full corrected-bridge `x=0.08`, `z=0.0025` gate 8/8 with mean
  track ratio `0.3742`, mean local `vx=0.0299 m/s`, and no corrected-envelope
  velocity excess, but it held at `x=0.0` because seed 5 collapsed. This
  candidate is a source/parent for zero-command repair, not a deployable or
  robot-test candidate:
  `outputs/analysis/PHASE2_Z0025_BOUNDARY_RATE1P9_FULL_GATE_DECISION_20260702.md`.
- The next live-oracle branch must repair seed-5 zero-command semantics for
  that z=0.0025 parent before any higher-terrain or push-robustness scaling.
  Hard zero-action relabeling fixed most zero-command drift in an earlier
  iteration but created a seed-specific collapse pocket. Use softened
  zero-command relabeling (`--x0-zero-action-alpha < 1.0`) and immediate
  seed-5 `x=0.0` short gates before running another full A100 training job.
- A bounded `z=0.0025` soft-zero live-oracle data iteration has been collected
  from that parent:
  `outputs/analysis/PHASE2_Z0025_LIVE_ORACLE_X0_SEED5_SOFTZERO_ITER2_DATA_DECISION_20260702.md`.
  The positive-command portion again passed `x=0.08` 8/8 in-envelope, while
  the targeted `x=0.0` seed-5 rollout reproduced the collapse at 43 samples
  and produced 43 soft-zero corrective labels. Treat the aggregate as data for
  the next supervised fit, not as a candidate result.
- The first contact/phase-modulated student fit from that aggregate also held
  the immediate short `x=0.0` seed-5 repair gate, falling again at 43 samples
  with reverse drift and no velocity-envelope excess:
  `outputs/analysis/PHASE2_Z0025_LIVE_ORACLE_SEED5_SOFTZERO_ITER2_BC_DECISION_20260702.md`.
  Do not run full gates, A100 scaling, robot validation, or more alpha-only
  soft-zero retries from this candidate. The collapse pocket needs a
  stabilizing zero-command support source/teacher, not only labels from the
  first 43 samples of the same failing rollout.
- The older flat-terrain hard-seed zero-command recovery candidate was tested
  as a possible support source for the current `rough_terrain_backlash`,
  `z=0.0025`, seed-5 reset pocket and did not transfer. It fell at 59 samples
  with reverse drift at `x=0.0`, although it stayed inside the corrected
  velocity envelope:
  `outputs/analysis/PHASE2_Z0025_FLAT_HARDSEED_SUPPORT_TRANSFER_DECISION_20260702.md`.
  Do not use that flat-terrain candidate as the support source for the current
  rough-terrain seed-5 repair.
- A command-gated diagnostic combining BEST at `x=0.0` with the rate1p9 parent
  at `x=0.08` confirmed that active zero-command support can catch the hard
  seed-5 rough reset, while preserving the parent positive-command branch on a
  short seed-5 check. It is not promotable: the BEST zero-command catch uses
  an over-envelope transient, and scaled BEST catches either fall or still
  exceed the corrected envelope:
  `outputs/analysis/PHASE2_Z0025_BEST_X0_RATE1P9_COMMAND_GATED_SUPPORT_SCREEN_DECISION_20260702.md`.
  Treat BEST as a support-recovery mechanism to constrain/distill, not as a
  deployable zero-command component.
- The stronger existing baseline for the current z=0.0025 rung is the
  target-limited command-gated candidate
  `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx`
  (`6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2`).
  It already passes the `rough_terrain_backlash`, `z=0.0025`,
  corrected-bridge stronger-push gate at both `x=0.0` and `x=0.08` for `8/8`
  seeds with no corrected velocity excess:
  `outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_STRONGER_PUSH_DECISION_20260701.md`.
  Its current blocker is the documented seed-5 support cliff at `z=0.0026+`,
  not the already-solved z=0.0025 support pocket.
- The `z=0.0026` seed-5 blocker has now been narrowed: `x=0.0` survives the
  2-second short gate in-envelope, while `x=0.08` fails at 57 samples with
  reverse-height collapse and no corrected-envelope velocity excess:
  `outputs/analysis/PHASE2_TARGETLIMITED0999_Z0026_SUPPORT_TRANSFER_DECISION_20260702.md`.
  The next repair should target moving-command support transfer at `z=0.0026`,
  not another zero-command-only reset repair.
- The scalar `z=0.0026` phase/single-support continuation is now closed. The
  reduced A100 `ss8` run exported an ONNX successfully, but the corrected CPU
  gate held with `8/8` early falls at 187 samples, max pitch-chain p95 velocity
  returning to `5.24 rad/s`, and corrected p95 velocity excess `2.99 rad/s`:
  `outputs/analysis/PHASE2_SS8_20480_A100_GATE_RESULT_20260703.md`.
  Do not keep adding timesteps to this scalar reward family.
- A clean corrected `z=0.0026` / `home-support` source manifest has been
  re-established from the Phase 1 rate-limited candidate:
  `outputs/analysis/PHASE2_PHASE1_RATE175_Z0026_X008_SOURCE_MANIFEST.md`
  (`0d4c2e82ef0ff64e`, 8 entries, 6000 samples). The source completed
  `x=0.08` for all 8 seeds with track ratio `0.4130`, corrected p95 velocity
  excess `0.0000`, max excess `0.0190`, and max tracking p95 `0.1859 rad`.
  It is a corrected teacher/source parent, not a deployable promotion result.
- `tools/run_live_oracle_dagger_iteration.py` now forwards
  `--reset-mode home-support` to candidate rollouts. Future corrected
  live-oracle iterations for Phase 2 must use the current gate convention:
  `rough_terrain_backlash`, `z=0.0026`, `home-support`, corrected bridge.

## Blocking Step 0

The corrected bridge must be treated as canonical before any new candidate gate:

```text
docs/CORRECTED_BRIDGE_CAMPAIGN_GOAL.md
docs/CURRENT_ACTUATOR_BRIDGE.md
outputs/analysis/current_actuator_bridge.json
```

The old `outputs/analysis/actuator_response_fit.json` is historical only for
new candidate gates.

Before trusting any gate number from this branch, reconcile the evaluator
discrepancy where one path reported `sent_vel95 ~= 2.2 rad/s` and the standard
task-matched evaluator reported `max_pitch_vel_p95 ~= 3.8 rad/s` for related
exports.

Required artifact:

```text
docs/EVALUATOR_RECONCILIATION.md
```

Gate:

```text
PASS_EVALUATOR_CANONICAL
```

No live-oracle DAgger candidate may be interpreted as a branch result until
Step 0 passes, a corrected-bridge source/oracle has been rebuilt, and the
exported student clears the canonical corrected evaluator.

Corrected Step 1 artifact:

```text
outputs/analysis/CORRECTED_BRIDGE_STEP1_FEASIBILITY_DECISION.md
```

Corrected terrain source and iter0 data artifacts:

```text
outputs/analysis/PHASE2_CORRECTED_TERRAIN_SOURCE_DECISION.md
outputs/analysis/PHASE2_Z005_LIVE_ORACLE_TERRAIN_SUPPORT_ITER0_RUN.md
outputs/analysis/PHASE2_Z005_LIVE_ORACLE_TERRAIN_SUPPORT_ITER0_AGGREGATE_MANIFEST.md
```

Latest recovery DAgger next-step artifact:

```text
outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_NEXT_DECISION.md
outputs/analysis/phase2_z005_recovery_dagger_next_decision.json
```

Latest recovery DAgger short-gate decision:

```text
outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_ITER1_SEED5_SHORT_DECISION.md
outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short_decision.json
```

Latest z=0.0025 seed-5 soft-zero data decision:

```text
outputs/analysis/PHASE2_Z0025_LIVE_ORACLE_X0_SEED5_SOFTZERO_ITER2_DATA_DECISION_20260702.md
outputs/analysis/phase2_z0025_live_oracle_x0_seed5_softzero_iter2_data_decision_20260702.json
```

Latest z=0.0025 seed-5 soft-zero student decision:

```text
outputs/analysis/PHASE2_Z0025_LIVE_ORACLE_SEED5_SOFTZERO_ITER2_BC_DECISION_20260702.md
outputs/analysis/phase2_z0025_live_oracle_seed5_softzero_iter2_bc_decision_20260702.json
```

Latest z=0.0025 flat hard-seed support transfer decision:

```text
outputs/analysis/PHASE2_Z0025_FLAT_HARDSEED_SUPPORT_TRANSFER_DECISION_20260702.md
outputs/analysis/phase2_z0025_flat_hardseed_support_transfer_decision_20260702.json
```

Latest z=0.0025 BEST x0 / rate1p9 x0.08 command-gated support screen:

```text
outputs/analysis/PHASE2_Z0025_BEST_X0_RATE1P9_COMMAND_GATED_SUPPORT_SCREEN_DECISION_20260702.md
outputs/analysis/phase2_z0025_best_x0_rate1p9_command_gated_support_screen_decision_20260702.json
```

Current z=0.0025 target-limited stronger-push baseline:

```text
outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_STRONGER_PUSH_DECISION_20260701.md
outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx
```

Current z=0.0026 support-transfer blocker:

```text
outputs/analysis/PHASE2_TARGETLIMITED0999_Z0026_SUPPORT_TRANSFER_DECISION_20260702.md
outputs/analysis/phase2_targetlimited0999_z0026_support_transfer_decision_20260702.json
```

Scalar branch closure and corrected source re-anchor:

```text
outputs/analysis/PHASE2_SCALAR_BRANCH_EXHAUSTED_CORRECTED_SOURCE_REANCHOR_20260703.md
outputs/analysis/phase2_scalar_branch_exhausted_corrected_source_reanchor_20260703.json
outputs/analysis/PHASE2_PHASE1_RATE175_Z0026_X008_SOURCE_TRACE.md
outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace.json
outputs/analysis/PHASE2_PHASE1_RATE175_Z0026_X008_SOURCE_MANIFEST.md
outputs/analysis/phase2_phase1_rate175_z0026_x008_source_manifest.json
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_plan/LIVE_ORACLE_DAGGER_ITERATION.md
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_plan/live_oracle_dagger_iteration.json
```

## Hypotheses

H1 representation:

```text
The deployable plateau is caused by a memoryless map being unable to represent
the phase-dependent stance-transition action. A student carrying gait-cycle
state will reduce strict-gate tracking p95 below the prior ~0.27 rad plateau.
```

H2 training signal:

```text
The standstill collapse is caused by reward maximization having a trivial
low-action optimum. Training where the primary signal is matching the live
selector oracle removes that optimum.
```

## Live-Oracle DAgger Loop

Hard budget: at most 6 iterations per representation rung.

Each iteration:

1. Roll out the current student with fitted bridge active:
   - `x=0.08`: 8 seeds, 15 seconds, full-observation traces
   - `x=0.0`: 2 seeds, 15 seconds, full-observation traces
2. Query the source-VX selector oracle on every student-visited state using
   the live rollout's local-vx estimate.
3. Aggregate the new `(obs, oracle_action)` rows into the manifest while
   retaining prior data.
4. Retrain the student on the aggregate dataset.
5. Gate on the canonical evaluator from Step 0.

## Representation Ladder

Run rungs in order and falsify before escalating:

1. Frame-stacked feed-forward student with 4 observation frames.
2. Explicit gait-phase conditioning, after verifying the phase fields and
   layout rather than inventing indices.
3. Small GRU/LSTM over the observation stream, with explicit ONNX hidden-state
   contract and fidelity verification.

The deployable policy contract remains:

```text
obs[1,101] -> continuous_actions[1,14]
```

If a representation requires extra runtime state, the export contract and
fidelity check must document that explicitly before promotion.

## Acceptance Gate

Canonical evaluator:

```text
task: flat_terrain_backlash
bridge: fitted corrected actuator bridge
fit_json: outputs/analysis/actuator_response_fit_corrected_knee.json
duration: 15 seconds
seeds: 0-7
```

For `x=0.08`, all must pass:

```text
duration_complete: 8/8
falls: 0/8
mean track ratio: >= 0.50
pitch-chain sent velocity p95: <= corrected per-joint fitted limits
max pitch-chain tracking p95: <= 0.20 rad
```

Corrected per-joint fitted limits:

| joint | velocity limit rad/s |
|---|---:|
| left_hip_pitch | 2.50 |
| left_knee | 3.25 |
| left_ankle | 2.75 |
| right_hip_pitch | 2.25 |
| right_knee | 2.75 |
| right_ankle | 2.00 |

For `x=0.0`, all must pass:

```text
duration_complete: 8/8
falls: 0/8
mean |vx|: <= 0.005 m/s
pitch-chain sent velocity p95: <= corrected per-joint fitted limits
```

Promotion requires ONNX export and action fidelity error no greater than
`1e-6`. A smoke-only pass is not promotable.

## Falsifiers

F1 representation insufficient:

```text
All three representation rungs run to budget and still hold at strict tracking
p95 > 0.24 rad.
```

F2 oracle-map collapse:

```text
Live-oracle DAgger collapses to mean track ratio < 0.2 at low target rate.
```

Both falsifiers must stop the branch and produce a decision artifact instead of
opening another local tweak loop.

## Closed Branches

Do not revisit these inside this branch:

- global blend-alpha sweeps
- uniform pitch-chain rate clipping
- transition-adjacent sample deletion
- post-hoc ONNX weight interpolation
- scalar PPO reward, termination, or KL controls
- static relabel-then-freeze DAgger
- small scalar progress-pressure retries from the Phase A2 warm-start

## Required Artifacts

```text
docs/EVALUATOR_RECONCILIATION.md
docs/LIVE_ORACLE_DAGGER_PHASE_STUDENT_SPEC.md
outputs/analysis/LIVE_ORACLE_DAGGER_ITER_{n}_GATE.md
outputs/analysis/LIVE_ORACLE_DAGGER_PHASE_STUDENT_candidate/candidate.onnx
outputs/analysis/LIVE_ORACLE_DAGGER_PHASE_STUDENT_DECISION.md
tools/instrumented_lowcmd_hw_eval.py
```

`tools/instrumented_lowcmd_hw_eval.py` is a later handoff artifact for
operator-run hardware logging. It must be read-only logging with no autonomous
walking decision logic.
