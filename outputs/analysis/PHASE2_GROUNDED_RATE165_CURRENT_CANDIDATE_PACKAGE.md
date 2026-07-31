# Candidate Policy Package

status: `INFO_NON_DEPLOYABLE_ARTIFACT`
generated_at: `2026-07-12T02:01:35Z`

## Candidate

- name: `phase2_grounded_rate165_current_20260711`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx`
- sha256: `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`
- size_bytes: `886302`

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

## Non-Deployable Notice

Offline grounded-start candidate only. Robot deployment and moving validation require explicit operator approval and physical support.

## Source Revisions

| repo | branch | commit | dirty status |
|---|---|---|---|
| `rdk_repo` | `codex/live-oracle-dagger-phase-student` | `ae0b6f85fbe5892bc1a2a38532e24bfa116c58c1` | `dirty` |
| `playground_repo` | `codex/forward-progress-reward` | `c890423e433120967cec16da091a9ec9ebd42ae2` | `dirty` |

## Evidence

| evidence | required | status | path |
|---|---|---|---|
| `contract_audit` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_grounded_rate165_policy_sim_contract_audit.json` |
| `target_velocity_summary` | `False` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_phase_contact_rate165_student.json` |
| `candidate_gate_x0` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_phase_contact_rate165_x0_gate.json` |
| `candidate_gate_x008` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_phase_contact_rate165_x008_gate.json` |
| `actuator_bridge_eval_legacy` | `False` | `MISSING` | `None` |
| `training_manifest` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_phase_contact_rate165_student.json` |

## Sim Gate Status

| gate | eval_role | overall_status | candidate_gate_status | pass/total |
|---|---|---|---|---:|
| `candidate_gate_x0` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |
| `candidate_gate_x008` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |

## Training Manifest

- status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- platform: `None`
- actuator_bridge_enabled: `None`
- target_rate_scale: `None`
- actuator_tracking_scale: `None`

## Robot Gate

This package does not approve robot testing. Robot-side suspended
validation still requires reviewed sim gates, Rob physically present,
and explicit approval for the specific test.
