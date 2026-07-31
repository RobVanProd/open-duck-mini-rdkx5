# Live-Oracle DAgger Iteration 0 Decision

status: `HOLD_ITER0_TRACKING_AND_X0_DRIFT`

This iteration was offline-only. It did not SSH, deploy, run robot tests,
change robot runtime behavior, or start hardware validation.

## Inputs

- branch: `codex/live-oracle-dagger-phase-student`
- rung: `deployable_obs101_phase_memory`
- initial student: `outputs/analysis/source_vx_selector_trace_dagger2_mlp128_rate_reg_candidate/candidate.onnx`
- live-oracle data artifact: `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_0_DATA.md`
- student fit artifact: `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_0_STUDENT_FIT.md`
- candidate ONNX: `outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate.onnx`
- canonical evaluator: `flat_terrain_backlash`, fitted bridge, 8 seeds, 15s

## What Iteration 0 Did

Iteration 0 rolled out the current student on its own visited states, queried the
source-VX selector oracle on those live states, aggregated the relabelled states
with the source-VX manifest, and fit a deployable `obs[1,101] -> actions[1,14]`
MLP student.

Data produced:

- x=0.08 live rollouts: 8 traces / 6000 samples
- x=0.0 live rollouts: 2 traces / 1500 samples
- aggregate manifest: 18 entries
- aggregate samples: 11500

Student fit smoke:

- MAE: 0.013879
- p95 abs error: 0.043352
- target-rate p95: 2.225589 rad/s
- ONNX verification p95 abs error: 0.00000016

## Canonical x=0.08 Gate

Required:

- duration complete: 8 / 8
- falls: 0 / 8
- mean track ratio: >= 0.50
- max pitch-chain sent vel p95: <= 3.75 rad/s
- max pitch-chain tracking p95: <= 0.20 rad

Observed:

- duration complete: 8 / 8
- falls: 0 / 8
- mean track ratio: 0.5613
- mean local vx: 0.0449 m/s
- max pitch-chain sent vel p95 range: 3.6195 to 3.6791 rad/s
- max pitch-chain tracking p95 range: 0.2601 to 0.2665 rad

Decision:

`HOLD_CANDIDATE_TRACKING`

The candidate is stable and moving forward, but it does not break the strict
tracking plateau. Tracking remains near 0.26 rad, above the 0.20 rad promotion
threshold and still close to the prior deployable-student plateau.

## Canonical x=0.0 Gate

Required:

- duration complete: 8 / 8
- falls: 0 / 8
- mean |vx|: <= 0.005 m/s

Observed:

- duration complete: 8 / 8
- falls: 0 / 8
- mean local vx: 0.0441 m/s
- max pitch-chain sent vel p95 range: 3.6735 to 3.7365 rad/s
- max pitch-chain tracking p95 range: 0.2565 to 0.2678 rad

Decision:

`HOLD_X0_COMMAND_SEMANTICS`

The same student drifts forward at zero command. The source-VX oracle labels
used for x=0.0 relabelling are not sufficient to preserve the zero-command
contract.

## Interpretation

Iteration 0 did not collapse into falls or immediate standstill. It completes
the full horizon on all seeds at both commands. However, it fails both promotion
requirements:

- strict fitted-bridge tracking remains around 0.26 rad
- zero-command semantics are not preserved

This is not yet an F1 or F2 branch falsifier. It is only the first live-oracle
iteration on the first deployable rung. Before iteration 1, the relabelling path
should account for command semantics, especially x=0.0, so the oracle does not
teach forward motion when the command is zero.

## Next Recommendation

Do not promote this candidate.

For the next iteration, keep the canonical evaluator unchanged, but revise the
live-oracle loop so x=0.0 rollouts are relabelled by a zero-command-preserving
oracle or by a command-aware label policy. Then run iteration 1 and compare:

- x=0.08 max tracking p95 against the 0.26 rad iteration-0 value
- x=0.0 mean |vx| against the 0.0441 m/s iteration-0 drift
- whether tracking improves without returning to standstill
