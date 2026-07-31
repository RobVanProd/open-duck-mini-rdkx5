# Live-Oracle DAgger Iteration 1 Decision

status: `HOLD_ITER1_SEED5_COLLAPSE`

This iteration was offline-only. It did not SSH, deploy, run robot tests,
change robot runtime behavior, or start hardware validation.

## Inputs

- branch: `codex/live-oracle-dagger-phase-student`
- rung: `deployable_obs101_phase_memory_command_aware_x0`
- initial student: `outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate.onnx`
- live-oracle data artifact: `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_1_DATA.md`
- student fit artifact: `outputs/analysis/LIVE_ORACLE_DAGGER_ITER_1_STUDENT_FIT.md`
- candidate ONNX: `outputs/analysis/live_oracle_dagger_phase_student_iter1_candidate/candidate.onnx`
- canonical evaluator: `flat_terrain_backlash`, fitted bridge, 8 seeds, 15s

## What Changed From Iteration 0

Iteration 1 kept the x=0.08 source-VX selector relabeling, but changed x=0.0
relabeling to a `zero_action` teacher. This directly targeted iteration 0's
zero-command drift failure.

Data produced:

- x=0.08 live rollouts: 8 traces / 6000 samples
- x=0.0 live rollouts: 2 traces / 1500 samples
- aggregate manifest: 18 entries
- aggregate samples: 11500

Student fit smoke:

- MAE: 0.013365
- p95 abs error: 0.042801
- target-rate p95: 2.098875 rad/s
- ONNX verification p95 abs error: 0.00000012

## Canonical x=0.08 Gate

Required:

- duration complete: 8 / 8
- falls: 0 / 8
- mean track ratio: >= 0.50
- max pitch-chain sent vel p95: <= 3.75 rad/s
- max pitch-chain tracking p95: <= 0.20 rad

Observed:

- duration complete: 7 / 8
- falls: 1 / 8
- mean track ratio: 0.1847
- mean local vx: 0.0148 m/s
- seed 5 termination: `fall_or_nan` at 74 samples
- completed-seed max pitch-chain sent vel p95 range: 3.6815 to 3.7287 rad/s
- completed-seed max pitch-chain tracking p95 range: 0.2600 to 0.2666 rad

Decision:

`HOLD_CANDIDATE_FALL_OR_TERMINATION`

The candidate regressed relative to iteration 0 on x=0.08 because seed 5 falls
early. Completed seeds still fail the 0.20 rad tracking threshold.

## Canonical x=0.0 Gate

Required:

- duration complete: 8 / 8
- falls: 0 / 8
- mean |vx|: <= 0.005 m/s

Observed:

- duration complete: 7 / 8
- falls: 1 / 8
- seed 5 termination: `fall_or_nan` at 48 samples
- passing seeds have mean local vx near zero: -0.0041 to 0.0015 m/s
- passing seeds have max pitch-chain tracking p95: 0.0416 rad
- aggregate vx_mean: -0.0425 m/s because seed 5 reverses before falling

Decision:

`PARTIAL_FIX_X0_SEMANTICS_WITH_SEED5_COLLAPSE`

The zero-action relabel path fixed the x=0.0 drift on 7 / 8 seeds, but seed 5
became a shared collapse case at both x=0.0 and x=0.08.

## Interpretation

Iteration 1 shows that command-aware relabeling is necessary: it converts most
x=0.0 seeds from forward drift into near-zero velocity and low tracking error.
However, applying the zero-action labels this way makes the student brittle on
seed 5 and does not improve the strict x=0.08 tracking plateau.

This is not yet an F1 or F2 branch falsifier:

- F1 is not triggered because only rung 1 has been tried.
- F2 is not triggered because the live-oracle map did not collapse globally to
  standstill; it created a seed-specific collapse while preserving motion on
  other x=0.08 seeds.

## Next Recommendation

Do not promote this candidate.

Before iteration 2, isolate seed 5 against iteration 0 and iteration 1:

- compare x=0.0 seed 5 traces to identify whether zero-action labels cause an
  abrupt posture/control discontinuity
- reduce the zero-command label influence or blend it with the student's prior
  only near true zero-command states
- preserve the command-aware x=0.0 fix, but prevent the seed-5 reverse/fall
  pocket

The knee hardware correction reported by the operator should be tracked
separately. It does not change this offline iteration result, but it means the
old actuator bridge should be refreshed before any future robot candidate is
treated as hardware-ready.
