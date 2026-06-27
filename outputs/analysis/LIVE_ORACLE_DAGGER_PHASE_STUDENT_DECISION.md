# Live-Oracle DAgger Phase Student Decision

status: `IN_PROGRESS_HOLD_ITER1`

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
