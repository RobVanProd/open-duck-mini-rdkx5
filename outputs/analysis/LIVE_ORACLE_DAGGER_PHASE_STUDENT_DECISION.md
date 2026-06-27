# Live-Oracle DAgger Phase Student Decision

status: `IN_PROGRESS_HOLD_COMMAND_GATE_X0_SOLVED_X008_TRACKING_PLATEAU`

This decision file tracks the pre-registered branch outcome. No robot tests,
SSH, deployment, policy overwrite, or runtime behavior changes have been
performed on this branch.

## Current Branch State

Step 0 evaluator reconciliation is complete:

- canonical evaluator: `tools/run_candidate_seed_sweep.py`
- sim task: `flat_terrain_backlash`
- bridge mode: `fitted`
- gate seeds: 8
- gate duration: 15s
- strict metrics: per-pitch-chain max p95, not flattened all-joint p95

Iteration 0 is complete and documented in:

- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_0_DATA.md`
- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_0_STUDENT_FIT.md`
- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_0_X008_GATE.md`
- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_0_X0_GATE.md`
- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_0_DECISION.md`

Iteration 1 is complete and documented in:

- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_1_DATA.md`
- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_1_STUDENT_FIT.md`
- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_1_X008_GATE.md`
- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_1_X0_GATE.md`
- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_1_DECISION.md`
- `outputs/analysis/LIVE_ORACLE_DAGGER_SEED5_TRACE_ISOLATION.md`

Soft x=0.0 relabel ablations and the command-gated x0-safe diagnostic are also
complete and documented in:

- `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_2_3_SOFT_X0_ABLATION.md`
- `outputs/analysis/LIVE_ORACLE_COMMAND_GATED_X0SAFE_ITER0_DECISION.md`
- `outputs/analysis/LIVE_ORACLE_COMMAND_GATED_X0SAFE_ITER0_X0_GATE.md`
- `outputs/analysis/LIVE_ORACLE_COMMAND_GATED_X0SAFE_ITER0_X008_GATE.md`
- `outputs/analysis/LIVE_ORACLE_ITER0_X008_PHASE_TRACKING_PLATEAU_AUDIT.md`

## Iteration 0 Outcome

Result:

`HOLD_ITER0_TRACKING_AND_X0_DRIFT`

Summary:

- x=0.08 duration complete: 8 / 8
- x=0.08 falls: 0 / 8
- x=0.08 mean track ratio: 0.5613
- x=0.08 max pitch-chain sent vel p95: 3.6791 rad/s
- x=0.08 max pitch-chain tracking p95: 0.2665 rad
- x=0.0 duration complete: 8 / 8
- x=0.0 falls: 0 / 8
- x=0.0 mean local vx: 0.0441 m/s

The candidate is stable, in-envelope, and moves forward at x=0.08, but it does
not break the strict 0.20 rad tracking threshold. It also violates
zero-command semantics by drifting forward at x=0.0.

## Falsifier Status

- F1 representation-insufficient: `NOT_TRIGGERED`
- F2 oracle-map collapse: `NOT_TRIGGERED`

Rationale:

This is only the first live-oracle iteration on rung 1. It did not collapse to
standstill or falls, but it also did not improve tracking enough to promote.
Iteration 1 repaired most x=0.0 command drift with zero-action labels, but
introduced a shared seed-5 collapse at x=0.0 and x=0.08. That is a rung-1
command-conditioning failure, not yet a branch falsifier.

## Current Recommendation

Do not promote the iteration-0 or iteration-1 candidate.

Before iteration 2, isolate seed 5 against iteration 0 and iteration 1. Preserve
the command-aware x=0.0 improvement, but reduce or smooth the zero-action label
influence so it does not create the seed-5 reverse/fall pocket.

Seed-5 isolation is now complete:

- iteration 0 seed 5 survives at both x=0.08 and x=0.0, with the old forward
  drift/tracking-hold behavior
- iteration 1 seed 5 reverses and collapses at both x=0.08 and x=0.0
- x=0.0 iteration-1 collapse occurs at low target-rate, not high target-rate
  overdrive

Therefore iteration 2 should not increase zero-action weight. It should blend
or schedule the x=0.0 zero-action labels so the zero-command fix is preserved
without creating a reverse/fall pocket on seed 5.

Soft zero-label ablations are also complete:

- iteration 2 used x=0.0 zero-action alpha 0.5 and still fell on seed 5
- iteration 3 used x=0.0 zero-action alpha 0.2 and still fell on seed 5
- both failures occur at low target-rate, not actuator overdrive

Do not spend more rung-1 budget on scalar zero-action alpha sweeps. The next
step should change structure: separate command-conditioned heads, add a
command-aware gate in the student, or move to the next representation rung
instead of globally blending zero labels into the same feed-forward map.

## Command-Gated X0-Safe Diagnostic

Result:

`HOLD_X008_TRACKING_PLATEAU_X0_SOLVED_BY_COMMAND_GATE`

Summary:

- wrapper: `outputs/analysis/live_oracle_command_gated_x0safe_iter0_candidate/candidate.onnx`
- ONNX branch verification max action error: `0.0`
- gate: use x0-safe recovery policy when `abs(obs[6]) <= 0.02`, otherwise use iteration-0 movement policy
- x=0.0 duration complete: `8 / 8`
- x=0.0 falls: `0 / 8`
- x=0.0 mean local vx: `0.0003 m/s`
- x=0.0 max pitch-chain tracking p95: `0.0718 rad`
- x=0.08 duration complete: `8 / 8`
- x=0.08 falls: `0 / 8`
- x=0.08 mean track ratio: `0.5613`
- x=0.08 max pitch-chain sent vel p95: `3.6791 rad/s`
- x=0.08 max pitch-chain tracking p95: `0.2665 rad`

Interpretation:

Hard command-regime separation fixes zero-command semantics, including the
seed-5 x=0.0 failure. It does not fix the x=0.08 tracking plateau because the
high-command branch is still the iteration-0 movement student. Therefore the
remaining live-oracle student blocker is no longer "can x0 and x008 coexist at
all"; it is "can a high-command representation reduce tracking below 0.20 rad
without losing the movement behavior."

Do not promote the command-gated wrapper to robot validation. It is diagnostic
evidence supporting a structural command-conditioned/phase-aware student rather
than more scalar relabel or alpha sweeps.

## Phase Tracking Plateau Audit

Result:

`PASS_PHASE_TRACKING_PLATEAU_AUDIT`

Summary:

- artifact: `outputs/analysis/LIVE_ORACLE_ITER0_X008_PHASE_TRACKING_PLATEAU_AUDIT.md`
- trace source: iteration-0 x=0.08 full-observation rollouts
- samples: `6000`
- all-sample max pitch-chain tracking p95: `0.2454 rad`
- all-sample max pitch-chain sent velocity p95: `3.6586 rad/s`
- dominant tracking joint in every phase bin: `right_knee`
- worst phase bin: `1`
- worst phase-bin right-knee tracking p95: `0.2567 rad`
- worst phase-bin right-knee sent velocity p95: `3.9081 rad/s`

Interpretation:

The x=0.08 plateau is not a generic all-joint failure. The dominant residual is
right-knee tracking, with the worst error concentrated in one phase quadrant
and with right-knee p95 sent velocity locally above the fitted envelope. This
supports a high-command phase/right-knee-specific representation or correction
before escalating to full recurrence. It also argues against more global scalar
x0 relabeling or whole-policy alpha sweeps.

## Hardware Track Note

The operator reported a real hardware correction after these offline bridge
experiments were already underway:

- `left_knee` soft offset changed from `-1.488` to `0.0371`
- post-update knee joint-space agreement on stand: L-R joint about `-0.63 deg`
- torque was left off after the monitor run

This does not change the offline iteration-0/1 gate results because those are
fixed-sim comparisons. It does mean the old actuator bridge should be refreshed
on the corrected hardware before any future candidate is treated as
hardware-ready.
