# Candidate Policy Package

status: `READY_FOR_SIM_GATE_REVIEW`
generated_at: `2026-07-05T22:02:46Z`

## Candidate

- name: `phase2_full8_router_tneg1p8_20260705`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/phase2_full8_router_tneg1p8_20260705/candidate.onnx`
- sha256: `f3e88820b87025788c97636599cd2caf6ef249f7cb7e50ddde31ff5c1c5457d0`
- size_bytes: `3791912`

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
| `rdk_repo` | `codex/live-oracle-dagger-phase-student` | `10e500431ad9cba354868cf3faa1adccccfd3557` | `dirty` |
| `playground_repo` | `codex/forward-progress-reward` | `4af95c9756a07aa245f4312b6ee68510fbcd2d15` | `dirty` |

## Evidence

| evidence | required | status | path |
|---|---|---|---|
| `contract_audit` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/policy_sim_contract_audit.json` |
| `target_velocity_summary` | `False` | `MISSING` | `None` |
| `candidate_gate_x0` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8_x000_full8_gate.json` |
| `candidate_gate_x008` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8_x008_full8_gate.json` |
| `actuator_bridge_eval_legacy` | `False` | `MISSING` | `None` |
| `training_manifest` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/phase2_full8_router_tneg1p8_20260705/training_manifest.json` |

## Sim Gate Status

| gate | eval_role | overall_status | candidate_gate_status | pass/total |
|---|---|---|---|---:|
| `candidate_gate_x0` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |
| `candidate_gate_x008` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |

## Training Manifest

- status: `PASS_ROUTED_COMPOSITION_MANIFEST`
- platform: `offline_cpu_eval`
- actuator_bridge_enabled: `True`
- target_rate_scale: `None`
- actuator_tracking_scale: `None`

```bash
compose_obs_mlp_gated_onnx_policy.py --threshold -1.8 followed by corrected-bridge rough_terrain_backlash x=0.08/x=0.0 full-8 CPU gates
```

## Robot Gate

This package does not approve robot testing. Robot-side suspended
validation still requires reviewed sim gates, Rob physically present,
and explicit approval for the specific test.
