# Phase 2 Full-8 Router Threshold -1.8 Candidate Decision

status: `PASS_PHASE2_ROUTER_WARMSTART_SIM_GATE`

Offline sim/package decision only. No robot tests, SSH, deploy, grounded
replay, hardware training, or runtime behavior change was performed.

## Candidate

```text
policy/candidates/phase2_full8_router_tneg1p8_20260705/candidate.onnx
```

```text
sha256: f3e88820b87025788c97636599cd2caf6ef249f7cb7e50ddde31ff5c1c5457d0
contract: obs[1,101] -> continuous_actions[1,14]
package status: READY_FOR_SIM_GATE_REVIEW
```

This is a composed observation-MLP router:

```text
branch A: policy/candidates/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_20260705/candidate.onnx
branch B: policy/candidates/phase2_z0075_iter25_dual_anchor_weight4_history_context_rate150_20260704/candidate.onnx
gate:     outputs/analysis/phase2_full8_mlp_router_gate_seed0_seed5_startup_cost_wide/gate_mlp.npz
rule:     branch B when gate_logit >= -1.8
```

## Why -1.8

The previous threshold probes bracketed the routing conflict:

```text
threshold  0.0: seed 0 PASS, seed 5 HOLD, seed 7 PASS
threshold -2.0: seed 0 HOLD, seed 5 PASS, seed 7 PASS
```

The `-1.8` midpoint was selected from the seed-0/seed-5 startup logit traces,
not from a broad threshold sweep. It is the first scalar cutoff in this router
family to clear the hard seed set.

## x=0.08 Gate

Artifact:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG1P8_X008_FULL8_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8_x008_full8_gate.json
```

Gate:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0075
bridge: corrected fitted actuator bridge
reset: home-support, settle 10 ticks
pushes: enabled, 0.075-0.125, every 1.0-1.5 s
seeds: 0-7
```

Result:

```text
8/8 PASS
0/8 falls
mean vx: 0.0276 m/s
mean track ratio: 0.3456
mean body pitch p95: 0.1859 rad
mean base height min: 0.1580 m
p95 velocity excess: 0.0000 rad/s
max velocity excess: 0.0000 rad/s
```

## x=0.0 Gate

Artifact:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG1P8_X000_FULL8_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8_x000_full8_gate.json
```

Result:

```text
8/8 PASS
0/8 falls
mean vx: 0.0007 m/s
double support: 100%
p95 velocity excess: 0.0000 rad/s
max velocity excess: 0.0000 rad/s
```

## Decision

Promote this artifact as the current offline Phase 2 warm-start candidate for
review and domain-randomization planning.

Do not treat this as robot approval. The policy is still slow and was not
ground-tested. The next offline task is Phase 2 DR from this warm-start:

```text
start with narrow randomization on rough_terrain_backlash
preserve x=0.08 8/8 pass
preserve x=0.0 command semantics
keep corrected-bridge velocity excess at 0
track whether robustness improves without killing forward motion
```

Grounded replay and robot validation remain blocked pending explicit review.
