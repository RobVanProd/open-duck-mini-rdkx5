# Candidate Policy Package

status: `READY_FOR_SIM_GATE_REVIEW`
generated_at: `2026-07-05T11:32:39Z`

## Candidate

- name: `phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_20260705`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020/candidate.onnx`
- sha256: `f3d5d735e96cf88bfe037bd4c6c1289eebc5d25bcc7722416f62dcee292866d0`
- size_bytes: `2299201`

## Contract

- status: `PASS_POLICY_CONTRACT`
- expected input dim: `101`
- actual input dim: `101`
- expected output dim: `14`
- actual output dim: `14`

| kind | name | shape | dtype |
|---|---|---|---|
| input | `obs` | `[1, 101]` | `tensor(float)` |
| output | `continuous_actions` | `[1, 14]` | `tensor(float)` |

## Source Revisions

| repo | branch | commit | dirty status |
|---|---|---|---|
| `rdk_repo` | `codex/live-oracle-dagger-phase-student` | `770d983462a3a93ab75be9b04b1d0ea6355da7f3` | `dirty` |
| `playground_repo` | `codex/forward-progress-reward` | `4af95c9756a07aa245f4312b6ee68510fbcd2d15` | `dirty` |

## Evidence

| evidence | required | status | path |
|---|---|---|---|
| `contract_audit` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/policy_sim_contract_audit.json` |
| `target_velocity_summary` | `False` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit_corrected_knee.json` |
| `candidate_gate_x0` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_x000_gate.json` |
| `candidate_gate_x008` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_x008_gate.json` |
| `actuator_bridge_eval_legacy` | `False` | `MISSING` | `None` |
| `training_manifest` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_manifest.json` |

## Sim Gate Status

| gate | eval_role | overall_status | candidate_gate_status | pass/total |
|---|---|---|---|---:|
| `candidate_gate_x0` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `5/5` |
| `candidate_gate_x008` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `5/5` |

## Training Manifest

- status: `PASS_WEIGHTED_BC_MANIFEST_READY`
- platform: `None`
- actuator_bridge_enabled: `None`
- target_rate_scale: `None`
- actuator_tracking_scale: `None`

## Robot Gate

This package does not approve robot testing. Robot-side suspended
validation still requires reviewed sim gates, Rob physically present,
and explicit approval for the specific test.
