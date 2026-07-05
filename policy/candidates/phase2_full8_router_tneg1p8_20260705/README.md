# Phase 2 Full-8 Router Threshold -1.8 Candidate

status: `OFFLINE_SIM_GATE_PASSED_NOT_ROBOT_APPROVED`

This candidate is a composed observation-MLP router over two existing ONNX
policies. It is not a new domain-randomized training result. It is packaged as
the current best corrected-bridge warm-start candidate because it cleared the
offline full-8 corrected-bridge gates needed before Phase 2 DR can proceed.

## Contract

```text
obs[1,101] -> continuous_actions[1,14]
```

## Routing

```text
branch A: policy/candidates/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_20260705/candidate.onnx
branch B: policy/candidates/phase2_z0075_iter25_dual_anchor_weight4_history_context_rate150_20260704/candidate.onnx
gate:     outputs/analysis/phase2_full8_mlp_router_gate_seed0_seed5_startup_cost_wide/gate_mlp.npz
rule:     branch B when gate_logit >= -1.8
```

## Evidence

```text
x=0.08 rough_terrain_backlash z=0.0075 gentle pushes:
  8/8 PASS, 0 falls, mean vx 0.0276 m/s, track ratio 0.3456, velocity excess 0

x=0.0 rough_terrain_backlash z=0.0075 gentle pushes:
  8/8 PASS, 0 falls, mean vx 0.0007 m/s, velocity excess 0
```

Evidence files:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG1P8_X008_FULL8_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8_x008_full8_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG1P8_X000_FULL8_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8_x000_full8_gate.json
policy/candidates/phase2_full8_router_tneg1p8_20260705/onnx_verify.json
```

No robot, SSH, deploy, grounded replay, or runtime behavior change was
performed. Robot validation remains blocked until this candidate is reviewed
and the next explicit hardware test is approved.
