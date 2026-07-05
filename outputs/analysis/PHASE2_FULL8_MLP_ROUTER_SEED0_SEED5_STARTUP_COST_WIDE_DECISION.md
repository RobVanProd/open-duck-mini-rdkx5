# Full-8 MLP Router Seed0/Seed5 Startup-Cost Wide Decision

status: `HOLD_FULL8_MLP_ROUTER_SEED5_CLOSED_LOOP_LUNGE`

Offline analysis only. No robot tests, SSH, deploy, grounded replay, hardware
training, or runtime behavior change was performed.

## Inputs

- seed-5 failure trace: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_STARTUP_COST_SEED5_TRACE_GATE.md`
- seed-5 branch replay: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_STARTUP_COST_SEED5_BRANCH_TRACE.md`
- narrow symmetric gate report: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_SEPARABILITY.md`
- wide symmetric gate report: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_SEPARABILITY.md`
- wide hard screen: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_X008_SEED0_5_7_GATE.md`

## Seed-5 Trace Read

The prior seed0-startup-cost router reproduced the seed-5 fall with full
observation tracing:

```text
seed 5: HOLD, 158 samples, vx 0.1298 m/s, track_ratio 1.6227, base min 0.0149
```

Replaying the seed0-startup-cost gate over that trace showed the opposite
startup problem from seed 0:

```text
all ticks branch B: 25.95%
first 80 ticks branch B: 0.00%
tail 80 ticks branch B: 51.25%
single-support branch B: 70.00%
double-support branch B: 18.98%
```

Seed 0 failed because branch B dominated startup. Seed 5 fails after the
seed-0 correction because branch B is absent from startup and only appears
later in the failing rollout.

## Symmetric Gate Attempts

The MLP-router training diagnostic now supports both branch-A and branch-B
corrective traces:

```text
--extra-negative-trace / --extra-negative-first-ticks / --extra-negative-weight
--extra-positive-trace / --extra-positive-first-ticks / --extra-positive-weight
```

The narrow `128,64` symmetric gate did not meet held-out separability:

```text
status: HOLD_MLP_ROUTER_OVERLAP
test balanced accuracy: 79.24%
test positive selected: 66.00%
test negative false selected: 7.52%
```

A wider `256,128,64` symmetric gate did meet the trace-label thresholds:

```text
status: PASS_MLP_ROUTER_SEPARABLE
test balanced accuracy: 88.52%
test positive selected: 80.67%
test negative false selected: 3.62%
gate_npz_sha256: 1492635af6ca5a4c0a1b7d39077f29ec58bf3eae6fb4bb9f262e74ed3c07d36e
candidate_sha256: 29e9e05cf877c6ead2ae1e05e5d27c32faec1adc75122d516b6db679c9786f6c
onnx_verify_sha256: aa20259c72fc4c1b0b4e844059e8834f574312cd74c2544e8556de95ba7a54d0
```

The composed ONNX verified exactly:

```text
status: PASS_ONNX_OBS_MLP_GATE_VERIFY
max_abs_error: 0.0
```

## Closed-Loop Screen

The wide symmetric router was screened at `x=0.08`, fitted corrected bridge,
`rough_terrain_backlash`, `z=0.0075`, home-support reset, and gentle pushes
over seeds `0,5,7`.

| seed | status | samples | vx | track_ratio | body_pitch_p95 | base_min | p95_vel_excess | max_vel_excess |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0268 | 0.3348 | 0.1668 | 0.1591 | 0.0000 | 0.0000 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 161 | 0.1296 | 1.6196 | 0.8511 | 0.0132 | 0.0000 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0254 | 0.3178 | 0.1914 | 0.1572 | 0.0000 | 0.0000 |

Distribution:

```text
passes: 2/3
falls: 1/3
mean track ratio: 0.7574
mean vx: 0.0606 m/s
velocity excess: 0.0000 p95, 0.0000 instantaneous
```

## Decision

Do not promote this candidate and do not start Phase 2 domain-randomization
training from it.

The wider stateless MLP router can fit the symmetric startup labels, but the
composed closed-loop candidate still fails seed 5 by lunging and falling while
remaining inside the corrected velocity envelope. This means branch-label
classification alone is still too weak: it can satisfy startup branch choices
without producing a stable closed-loop transition.

Recommended next step:

```text
Stop one-off branch-label weighting.
Move to a closed-loop-aware router objective or stateful/prefix router:
  - train against rollout-level costs, not source labels alone
  - preserve seed 0 and 7 passing behavior
  - suppress seed 5 lunge/pitch failure
  - require the composed ONNX to pass the same 0/5/7 hard screen before full-8
```

Phase 2 DR remains blocked until a deployable corrected-bridge candidate clears
the canonical multi-seed gate.
