# Live-Oracle DAgger Phase Student Decision

status: `IN_PROGRESS_HOLD_ITER0`

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
The x=0.0 drift indicates the next iteration should repair command-aware
oracle labelling before spending the remaining budget.

## Current Recommendation

Do not promote the iteration-0 candidate.

Proceed only after revising the live-oracle relabeling path so zero-command
states receive zero-command-preserving labels. Then run iteration 1 using the
same canonical strict evaluator and compare directly against the iteration-0
tracking/drift numbers.
