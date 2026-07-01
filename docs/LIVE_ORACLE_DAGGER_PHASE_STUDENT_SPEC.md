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
- Prior memoryless distillations, static DAgger passes, kNN/linear/blend
  students, and feed-forward PPO-shape students held at the same tracking
  plateau or froze.
- Reward-side PPO controls, including behavior prior, adaptive KL,
  progress-failure termination, restore-policy KL, and low-alpha weight blends,
  collapsed into standstill.
- Static relabel-then-freeze DAgger is closed. This branch must run a live
  loop: roll out the current student, query the oracle on those visited states,
  aggregate, retrain, and gate.

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
