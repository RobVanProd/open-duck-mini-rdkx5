# Phase 2 Command-Gated Trainable Compression Decision

status: `HOLD_TRAINABLE_COMPRESSION_MOVING_GATE`

Offline sim/eval/BC analysis only. No robot tests, SSH, deploy, grounded replay,
runtime behavior change, or domain-randomized PPO training were performed.

## Summary

The graph-level command-gated ONNX clears the compact corrected-bridge
rough+push gate at both `x=0.08` and `x=0.0`, but the first PPO-compatible
single-MLP compressions do not preserve the moving-command gate.

This means Phase 2 has a valid deployable-shape eval candidate, but it still
does not have a trainable PPO/Orbax warm-start checkpoint for domain
randomization.

## Source Candidate

- graph-gated ONNX: `policy/candidates/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_20260705/candidate.onnx`
- sha256: `f3d5d735e96cf88bfe037bd4c6c1289eebc5d25bcc7722416f62dcee292866d0`
- compact `x=0.08`: `5/5` pass
- compact `x=0.0`: `5/5` pass

## Combined BC Manifest

- manifest: `outputs/analysis/phase2_command_gated_zero0020_bc_manifest.json`
- dataset_id: `24beb17ef0e1de02`
- entries: `10`
- samples: `7500`
- source traces: graph-gated `x=0.08` and `x=0.0` compact gate traces

## Unweighted PPO-Loc MLP

- fit: `outputs/analysis/phase2_command_gated_zero0020_ppo_loc_bc_student.json`
- ONNX: `outputs/analysis/phase2_command_gated_zero0020_ppo_loc_bc_student/candidate.onnx`
- NPZ: `outputs/analysis/phase2_command_gated_zero0020_ppo_loc_bc_student/candidate_mlp.npz`
- fit p95 abs error: `0.004215`
- target-rate p95: `1.264834` rad/s
- ONNX verification max abs error: `0.00000011`

Compact gates:

- `x=0.08`: `3/5` pass, seeds `0` and `7` fall or terminate
- `x=0.0`: `5/5` pass

## Seed-0/7 Weighted PPO-Loc MLP

- weighted manifest: `outputs/analysis/phase2_command_gated_zero0020_seed07_weighted_bc_manifest.json`
- dataset_id: `716fd971d4b33945`
- weighted samples: `10500`
- fit: `outputs/analysis/phase2_command_gated_zero0020_seed07_weighted_ppo_loc_bc_student.json`
- ONNX: `outputs/analysis/phase2_command_gated_zero0020_seed07_weighted_ppo_loc_bc_student/candidate.onnx`
- NPZ: `outputs/analysis/phase2_command_gated_zero0020_seed07_weighted_ppo_loc_bc_student/candidate_mlp.npz`
- fit p95 abs error: `0.004171`
- target-rate p95: `1.261821` rad/s
- ONNX verification max abs error: `0.00000013`

Compact `x=0.08` gate:

- pass count: `3/5`
- failed seeds: `0`, `2`
- seed `7` recovered, but the failure moved to seed `2`
- one seed had max velocity excess `0.1877` rad/s

## Decision

Do not start Phase 2 domain-randomized PPO training from either trainable MLP.
The graph-level command gate remains the best compact eval candidate, but a
trainable warm-start still needs either:

- a representation that preserves the command-gated behavior without collapsing
  the moving branch, or
- a PPO-compatible initialization path that can carry the command-gated branch
  structure directly.

The active Phase 2 goal remains open.
