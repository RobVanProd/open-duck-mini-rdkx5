# Phase 2 Command-Gated Parent Decision

status: `PASS_COMPACT_COMMAND_GATED_PARENT_READY`

Offline sim/eval only. No robot tests, SSH, deploy, grounded replay, runtime
behavior change, or domain-randomized training were performed.

## Summary

The seed-7-weighted parent-pair lateral student solved the compact `x=0.08`
rough+push moving-command screen but failed `x=0.0` command semantics. A
deployable ONNX command gate now routes:

- `abs(obs[6]) <= 0.02`: `outputs/analysis/zero_action_policy.onnx`
- `abs(obs[6]) > 0.02`: `outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_student/candidate.onnx`

The command-gated ONNX preserves the moving branch and fixes zero-command
behavior on the compact corrected-bridge screen.

## Candidate

- analysis ONNX: `outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020/candidate.onnx`
- packaged ONNX: `policy/candidates/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_20260705/candidate.onnx`
- sha256: `f3d5d735e96cf88bfe037bd4c6c1289eebc5d25bcc7722416f62dcee292866d0`
- ONNX gate verify: `PASS_ONNX_GATE_VERIFY`
- max routing error: `0.0`

## Compact Gates

Shared gate settings:

- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain: `z=0.0075`
- reset: `home-support`
- reset settle ticks: `10`
- pushes: enabled, `0.075`-`0.125`, interval `1.0`-`1.5` s
- seeds: `0,1,2,6,7`
- duration: `15` s

### x=0.08

- gate artifact: `outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_x008_gate.json`
- pass count: `5/5`
- falls: `0`
- duration complete: `5/5`
- mean vx: `0.0258` m/s
- mean track ratio: `0.3230`
- mean body pitch p95: `0.1830` rad
- mean max pitch-chain velocity p95: `1.5981` rad/s
- p95 velocity excess: `0.0000`
- mean push success: `0.9526`

### x=0.0

- gate artifact: `outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_x000_gate.json`
- pass count: `5/5`
- falls: `0`
- duration complete: `5/5`
- mean vx: `0.0008` m/s
- mean body pitch p95: `0.0661` rad
- mean max pitch-chain velocity p95: `0.0000` rad/s
- p95 velocity excess: `0.0000`
- mean push success: `0.9526`

## Decision

The prior `HOLD_COMMAND_SEMANTICS_X0` blocker is resolved on the compact
rough+push screen. This candidate is a valid Phase 2 compact warm-start for the
next offline domain-randomization stage.

This is not a robot approval. Before any robot-side validation, the candidate
still needs the staged Phase 2 DR curriculum and reviewed full gates.
