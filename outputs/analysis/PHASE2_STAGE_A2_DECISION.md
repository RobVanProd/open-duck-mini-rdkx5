# Phase 2 Stage A2 Decision

status: `HOLD_STAGE_A2_NEAR_MISS_NO_PROMOTION`

## Summary

Stage A2 was a behavior-preserving retry after Stage A regressed the Phase 1
gait into low forward progress. It completed offline on the local ROCm GPU and
produced three exported checkpoints.

Compared with Stage A, A2 preserved substantially more `x=0.08` motion, but no
checkpoint fully clears the strict corrected-bridge gate. Robot validation
remains blocked.

## Training Run

```text
output_dir:
  outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu

manifest:
  outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/smoke_manifest.final.json

manifest_sha256:
  3b52e8862298f415b248fe0f0f045b90293ab6dd870f005197af2572e6c5885b

status:
  PASS_SMOKE_RUN

elapsed:
  407.62 s
```

Recipe changes from Stage A:

- lower learning rate: `3e-5`
- smaller PPO batch/env count: `128` envs
- stronger restore-policy KL: `1.0`
- stronger behavior prior: `-0.4`
- weaker DR/noise ranges
- no pushes

Export hashes:

```text
163840: bef47b5faadb348b03a66a8dc3070d40a7953d7adb01367185213e70c500f2d1
327680: 362a81c1438f3752e97f05a14676acf2ce449092ca3985ad77a9a7f220ed582c
491520: 01350f996866c086c22a9544f80d1c48c93fa7dc4e4fb2740f2b96db648ed0a7
```

## Checkpoint Screen

Artifact:

```text
outputs/analysis/PHASE2_STAGE_A2_CHECKPOINT_SCREEN_X008.md
outputs/analysis/phase2_stage_a2_checkpoint_screen_x008.json
```

Seed-0, 5 s, corrected bridge:

```text
a2_164k:
  status: HOLD_CANDIDATE_TRACKING
  track ratio: 0.3755
  vx: 0.0300 m/s
  max tracking p95: 0.2027 rad

a2_328k:
  status: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.2704
  vx: 0.0216 m/s
  max tracking p95: 0.1924 rad

a2_492k:
  status: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.2723
  vx: 0.0218 m/s
  max tracking p95: 0.1820 rad
```

## Full Gates

### A2 164k, x=0.08

Artifact:

```text
outputs/analysis/PHASE2_STAGE_A2_164K_X008_GATE.md
outputs/analysis/phase2_stage_a2_164k_x008_gate.json
```

Result:

```text
duration_complete: 8/8
falls: 0/8
generic pass count: 7/8
mean track ratio: 0.3694
mean vx: 0.0296 m/s
max pitch velocity p95 excess: 0.0 rad/s
max tracking p95: 0.2004 rad
hold reason: seed 0 tracking p95 is 0.0004 rad over the 0.20 rad threshold
```

### A2 164k, x=0.0

Artifact:

```text
outputs/analysis/PHASE2_STAGE_A2_164K_X000_GATE.md
outputs/analysis/phase2_stage_a2_164k_x000_gate.json
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE on 8/8 seeds
duration_complete: 8/8
falls: 0/8
mean vx: 0.0004 m/s
max pitch velocity p95 excess: 0.0 rad/s
max tracking p95: 0.0751 rad
```

### A2 492k, x=0.08

Artifact:

```text
outputs/analysis/PHASE2_STAGE_A2_492K_X008_GATE.md
outputs/analysis/phase2_stage_a2_492k_x008_gate.json
```

Result:

```text
duration_complete: 8/8
falls: 0/8
generic pass count: 6/8
mean track ratio: 0.2580
mean vx: 0.0206 m/s
max pitch velocity p95 excess: 0.0 rad/s
max tracking p95: 0.1901 rad
hold reason: seeds 3 and 6 are low-forward-progress holds
```

## A3 Attempt

Stage A3 attempted an even tighter preservation run, but it failed before
training with the known local ROCm/MJX path:

```text
status: HOLD_SMOKE_RUN
returncode: -6
error: ROCM_ERROR_ILLEGAL_ADDRESS while setting ROCm context
manifest:
  outputs/phase2_domain_randomization/stage_a3_ultra_preserve_narrow_flat_no_push_gpu/smoke_20260628T032920Z_gpu/smoke_manifest.final.json
manifest_sha256:
  c1333c413a71188f60959d654e5bf6cfae4c00746f7deaa4fb00b4b878478150
```

This is a backend failure, not a policy result.

## Interpretation

A2 confirms the direction: stronger behavior preservation avoids the Stage A
standstill regression. The best checkpoint is close, but still not promotable.

The next useful training change is not Stage B randomization. It should keep the
A2 preservation posture and add a small targeted correction for tracking without
allowing the optimizer to erase forward motion.

Robot validation remains blocked.
