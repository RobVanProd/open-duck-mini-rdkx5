# Phase 2 Command-Gated Live-Oracle PPO-Loc Decision

status: `HOLD_LIVE_ORACLE_PPO_LOC_SEED6_MOVING_GATE`

Offline sim/eval/BC analysis only. No robot tests, SSH, deploy, grounded
replay, runtime behavior change, or domain-randomized PPO training were
performed.

## Summary

The first live-oracle DAgger correction materially improved the PPO-compatible
single-MLP compression, but it did not produce a trainable warm-start that
clears the compact corrected-bridge moving gate.

The baseline single-MLP compression passed `3/5` at `x=0.08` and `5/5` at
`x=0.0`. Live-oracle iter1 improved the moving gate to `4/5` while preserving
zero-command behavior. Live-oracle iter2 kept the moving gate at `4/5` and made
the remaining seed-6 failure worse.

## Iteration 1

- data artifact: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter1/LIVE_ORACLE_DAGGER_ITERATION.md`
- aggregate manifest: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter1/live_oracle_dagger_aggregate_manifest.json`
- aggregate samples: `10413`
- weighted samples: `16320`
- student: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter1_ppo_loc_bc_student/candidate.onnx`
- NPZ: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter1_ppo_loc_bc_student/candidate_mlp.npz`
- fit p95 abs error: `0.009336`
- fit max abs error: `0.149078`
- fit target-rate p95: `1.250601` rad/s
- fit target-rate max: `2.889865` rad/s

Compact gates:

- `x=0.08`: `4/5` pass, failed seed `6`
- `x=0.0`: `5/5` pass
- corrected velocity-envelope excess: `0`

## Iteration 2

- data artifact: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2/LIVE_ORACLE_DAGGER_ITERATION.md`
- aggregate manifest: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2/live_oracle_dagger_aggregate_manifest.json`
- aggregate samples: `11555`
- weighted samples: `19827`
- student: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_bc_student/candidate.onnx`
- NPZ: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_bc_student/candidate_mlp.npz`
- fit p95 abs error: `0.010067`
- fit max abs error: `0.198142`
- fit target-rate p95: `1.220553` rad/s
- fit target-rate max: `2.245606` rad/s

Compact `x=0.08` gate:

- pass count: `4/5`
- failed seed: `6`
- seed-6 failure sample: `341`
- seed-6 mean local vx: `-0.0322` m/s
- seed-6 track ratio: `-0.4030`
- corrected velocity-envelope excess: `0`

The iter2 `x=0.0` full compact gate was not run because the moving gate already
held. Iter2's live-oracle data collection did include seed-6 zero-command
preservation trace data.

## Decision

Do not launch Phase 2 domain-randomized PPO training from either live-oracle
PPO-loc student.

Live-oracle DAgger is useful evidence because it fixed the original seed-0 and
seed-7 trainable-compression failures without breaking zero command, but the
remaining seed-6 moving failure persists after a focused second correction.
Repeating the same single-MLP PPO-loc correction is now a weak next move.

The active Phase 2 blocker remains a trainable warm-start representation that
preserves the graph-gated moving branch across the compact seed set. Next work
should inspect the seed-6 failure trace and/or move to a representation that
can carry the branch/phase structure, rather than starting DR training.
