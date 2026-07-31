# Candidate Policy Package

status: `READY_FOR_SIM_GATE_REVIEW`
generated_at: `2026-06-28T00:30:36Z`

## Candidate

- name: `corrected_bridge_cmd_conditioned_rate175`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate.onnx`
- sha256: `63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e`
- size_bytes: `874724`

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
| `rdk_repo` | `codex/live-oracle-dagger-phase-student` | `06f52622e6c45fdb3327e1778c5ba1aaa1949485` | `dirty` |
| `playground_repo` | `codex/forward-progress-reward` | `ad924c4c6d492fe682748f7cc82cf3c96dbad75c` | `clean` |

## Evidence

| evidence | required | status | path |
|---|---|---|---|
| `contract_audit` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/policy_sim_contract_audit.json` |
| `target_velocity_summary` | `False` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_FULL_GATE.md` |
| `candidate_gate_x0` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/corrected_bridge_cmd_conditioned_x0_gate.json` |
| `candidate_gate_x008` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/corrected_bridge_cmd_conditioned_full_gate.json` |
| `actuator_bridge_eval_legacy` | `False` | `MISSING` | `None` |
| `training_manifest` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_bc_student.json` |

## Sim Gate Status

| gate | eval_role | overall_status | candidate_gate_status | pass/total |
|---|---|---|---|---:|
| `candidate_gate_x0` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |
| `candidate_gate_x008` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |

## Training Manifest

- status: `PASS_PPO_LOC_BC_FIT_SMOKE`
- platform: `None`
- actuator_bridge_enabled: `None`
- target_rate_scale: `None`
- actuator_tracking_scale: `None`

## Robot Gate

This package does not approve robot testing. Robot-side suspended
validation still requires reviewed sim gates, Rob physically present,
and explicit approval for the specific test.
