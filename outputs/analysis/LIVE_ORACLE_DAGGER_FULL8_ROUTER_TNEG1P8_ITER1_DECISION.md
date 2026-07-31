# Live-Oracle DAgger Full8 Router Iteration 1 Decision

status: `HOLD_LIVE_ORACLE_ITER1_SHIFTED_FAILURE_SURFACE`

Offline data collection, behavior-cloning fit, and corrected-bridge gate only.
No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or
domain-randomized PPO training were performed.

## Purpose

Static trainable compression of the promoted full8 router was not promotable:
the PPO-loc students held at `6/8`, failing seeds `5` and `6`. This iteration
closed one DAgger loop around the better PPO-loc seed56-weighted student:

1. roll out that student on its own x=0.08 and x=0.0 visited states,
2. relabel x=0.08 states with the corrected full8 router source oracle,
3. relabel x=0.0 states with zero action to preserve command semantics,
4. aggregate those labels with the corrected router trace manifest,
5. train a PPO-compatible `obs[1,101] -> actions[1,14]` BC student,
6. gate the exported ONNX at x=0.08.

## Inputs

- student rolled out: `outputs/analysis/phase2_full8_router_tneg1p8_ppo_loc_bc_seed56_weighted_student/candidate.onnx`
- teacher manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest.json`
- base manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest_seed56_weighted.json`
- iteration artifact: `outputs/analysis/LIVE_ORACLE_DAGGER_FULL8_ROUTER_TNEG1P8_ITER1_DATA.md`
- aggregate manifest: `outputs/analysis/live_oracle_dagger_full8_router_tneg1p8/iter_001/live_oracle_dagger_aggregate_manifest.json`

Aggregate:

```text
entries: 26
samples: 18836
weighted samples in student fit: 38022
x=0.08 relabel samples: 5336
x=0.0 relabel samples: 1500
```

The x=0.08 live rollout reproduced the expected seed failures from the starting
student:

```text
starting student x=0.08: 6/8 duration complete
failed seeds: 5, 6
```

The x=0.0 live rollout preserved command semantics for the two sampled seeds:

```text
x=0.0 sampled seeds: 0, 1
duration complete: 2/2
mean vx: 0.0008 m/s
```

## Student Fit

Artifact:

```text
outputs/analysis/LIVE_ORACLE_DAGGER_FULL8_ROUTER_TNEG1P8_ITER1_PPO_LOC_STUDENT.md
outputs/analysis/live_oracle_dagger_full8_router_tneg1p8_iter1_ppo_loc_student.json
```

Result:

```text
status: PASS_PPO_LOC_BC_FIT_SMOKE
ONNX: outputs/analysis/live_oracle_dagger_full8_router_tneg1p8_iter1_ppo_loc_student/candidate.onnx
ONNX sha256: aaaf462d781c07c9c46e5b6b6ee6c5b56eed087db290127168303d37972f96cd
NPZ sha256: 6b55da25affc6444e29ca9592dc79667708ab8962ceecf12f64f7fe4d2c5c5e9
MAE: 0.003753
p95 abs error: 0.011881
max abs error: 0.091833
target-rate p95: 1.308459 rad/s
target-rate max: 2.117395 rad/s
ONNX p95 abs error: 0.00000008
ONNX max abs error: 0.00000012
```

## x=0.08 Corrected-Bridge Gate

Artifact:

```text
outputs/analysis/LIVE_ORACLE_DAGGER_FULL8_ROUTER_TNEG1P8_ITER1_PPO_LOC_X008_GATE.md
outputs/analysis/live_oracle_dagger_full8_router_tneg1p8_iter1_ppo_loc_x008_gate.json
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
duration complete: 6/8
falls: 2/8
failed seeds: 4, 6
samples mean/min/max: 706 / 564 / 750
mean vx: 0.0273 m/s
mean track ratio: 0.3415
mean body pitch p95: 0.2013 rad
mean base height min: 0.1277 m
p95 velocity excess mean/max: 0.0000 / 0.0000 rad/s
max velocity excess mean/max: 0.0878 / 0.7025 rad/s
max tracking p95 mean/max: 0.1900 / 0.1954 rad
```

Compared with the starting seed56-weighted PPO-loc student:

```text
starting failures: seed 5 at 154 samples, seed 6 at 682 samples
iter1 failures:    seed 4 at 564 samples, seed 6 at 584 samples
seed 5: recovered to duration_complete
seed 4: regressed from duration_complete to fall
seed 6: still fails, and earlier than before
```

## Decision

Do not launch domain-randomized PPO from this iteration-1 student. It remains
`6/8` at x=0.08 and is not a Phase 2 trainable warm start.

The useful result is diagnostic: live-oracle relabeling is affecting the hard
seed surface, but a single memoryless PPO-loc BC student still cannot preserve
the full router's all-seed closed-loop behavior. The next iteration should
target the shifted failures explicitly, especially seed `6`, and should avoid
assuming the recovered seed `5` means the conversion problem is solved.

recommended_next: `Run a second live-oracle iteration from iter1 with seed-4/seed-6 active relabel emphasis or move to a stateful/branch-aware student; do not start DR from this ONNX.`

The companion x=0.0 full-8 promotion gate was skipped because the x=0.08 gate is
already a hard hold.
