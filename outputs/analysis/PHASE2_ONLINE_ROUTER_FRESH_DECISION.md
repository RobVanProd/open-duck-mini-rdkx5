# Phase 2 Fresh Online Router Decision

status: `PASS_ONLINE_ROUTER_FRESH_COMPACT_SOURCE`

## Summary

The health-gated router behavior was replayed from freshly generated branch
rollouts, not just from the earlier precomputed trace corpus.

This is an offline eval-only router/source-generation result. It did not train,
SSH, deploy, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

Fresh compact corrected-bridge sweeps:

```text
outputs/analysis/PHASE2_ONLINE_ROUTER_FRESH_ITER24_25_SWEEP.md
outputs/analysis/phase2_online_router_fresh_iter24_25_sweep.json
outputs/analysis/PHASE2_ONLINE_ROUTER_FRESH_ITER26_27_SWEEP.md
outputs/analysis/phase2_online_router_fresh_iter26_27_sweep.json
```

Router gate:

```text
outputs/analysis/PHASE2_ONLINE_ROUTER_FRESH_ITER24_27_GATE.md
outputs/analysis/phase2_online_router_fresh_iter24_27_gate.json
```

Selected fresh behavior manifest:

```text
outputs/analysis/PHASE2_ONLINE_ROUTER_FRESH_SELECTED_MANIFEST.md
outputs/analysis/phase2_online_router_fresh_selected_manifest.json
```

## Gate

Canonical compact screen:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0075
bridge: fitted corrected actuator bridge
reset: home-support, settle 10 ticks
pushes: 0.075-0.125 every 1.0-1.5 s
seeds: 0,1,2,6,7
```

Router configuration:

```text
prefix_ticks: 100
knn_k: 3
policy_onehot_scale: 5.0
pitch_guard_limit_rad: 0.20
pitch_guard_scale: 1.0
target_track_ratio: 0.35
```

## Fresh Branch Coverage

| branch | compact passes | compact falls | note |
|---|---:|---:|---|
| `iter24` | 4/5 | 1/5 | covers seeds 0,1,2,7; misses seed 6 |
| `iter25` | 3/5 | 2/5 | covers seeds 1,2,6 |
| `iter26` | 1/5 | 4/5 | covers seed 6 |
| `iter27` | 2/5 | 3/5 | covers seeds 0,1 |

The two-branch router using only `iter24,iter25` held on seed `6`, because the
prefix score still preferred failing `iter24`. The full four-branch context
restored the route and selected a passing branch for every compact seed.

## Routed Result

| seed | selected branch | selected status | track ratio | mean vx |
|---:|---|---|---:|---:|
| 0 | `iter24` | `PASS_CANDIDATE_SIM_GATE` | 0.3256 | 0.0261 |
| 1 | `iter25` | `PASS_CANDIDATE_SIM_GATE` | 0.3567 | 0.0285 |
| 2 | `iter24` | `PASS_CANDIDATE_SIM_GATE` | 0.3278 | 0.0262 |
| 6 | `iter25` | `PASS_CANDIDATE_SIM_GATE` | 0.3273 | 0.0262 |
| 7 | `iter24` | `PASS_CANDIDATE_SIM_GATE` | 0.3437 | 0.0275 |

Selected manifest:

```text
status: PASS_BC_TRACE_MANIFEST_READY
dataset_id: f2ecbdfab21ccafa
entries: 5
samples: 3750
```

## Decision

The router branch remains useful as an eval-only behavior-preservation source:
fresh branch rollouts plus prefix-health routing reproduce a compact-gate pass.

This is still not a Phase 2 DR warm start by itself:

- the router runs multiple branch policies and selects after a prefix;
- it is not a single deployable ONNX policy;
- prior static and recurrent compression attempts failed or regressed;
- Phase 2 DR still requires a trainable parent that preserves this routed
  behavior, or an explicit decision to train/evaluate with a wrapper objective.

## Next

Use the fresh selected manifest as the authoritative behavior source for the
next bounded parent attempt. Do not launch long domain-randomized training until
that parent clears the compact corrected-bridge behavior-preservation gate.
