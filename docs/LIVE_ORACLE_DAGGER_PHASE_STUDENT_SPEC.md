# Live-Oracle DAgger Phase Student Spec

Status: `PRE_REGISTERED_NOT_STARTED`

Branch ID: `LIVE_ORACLE_DAGGER_PHASE_STUDENT`

This branch supersedes `PLAN_GATE_AWARE_ROLLOUT_CORRECTION_OR_RECURRENT_STUDENT`.
It is offline-only until a candidate clears the strict canonical fitted-bridge
gate. No robot test, SSH, deploy, hardware calibration write, policy overwrite,
or runtime behavior change is in scope for this branch.

## Objective

Distill the working source-VX selector into a deployable policy that clears the
strict fitted-bridge tracking gate by:

- querying the selector as a live oracle on the student's own visited states at
  every iteration
- adding enough state/phase memory for the student to represent the
  stance-transition action that memoryless students have failed to reproduce

## Settled Evidence

- The source-VX selector proved in-envelope all-seed forward walking exists in
  sim under the fitted actuator bridge.
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

No live-oracle DAgger iteration may be interpreted as a branch result until
Step 0 passes.

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
bridge: fitted
duration: 15 seconds
seeds: 0-7
```

For `x=0.08`, all must pass:

```text
duration_complete: 8/8
falls: 0/8
mean track ratio: >= 0.50
max pitch-chain sent velocity p95: <= 3.75 rad/s
max pitch-chain tracking p95: <= 0.20 rad
```

For `x=0.0`, all must pass:

```text
duration_complete: 8/8
falls: 0/8
mean |vx|: <= 0.005 m/s
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
