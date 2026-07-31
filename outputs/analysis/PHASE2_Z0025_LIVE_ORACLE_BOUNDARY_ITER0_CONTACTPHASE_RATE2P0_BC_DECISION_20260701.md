# Phase 2 z=0.0025 Contact+Phase Rate2p0 BC Decision

status: `HOLD_RATE2P0_BC_TINY_TARGET_VELOCITY_EXCESS`

This was an offline supervised BC fit and CPU sim screen. It did not SSH,
deploy, train PPO, run robot tests, or change runtime behavior.

## Candidate

- source manifest: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0/live_oracle_dagger_aggregate_manifest.json`
- aggregate dataset_id: `e1d14b2c3f81d443`
- aggregate samples: `10500`
- model: contact+phase-modulated feed-forward BC student
- context indices: `[6, 97, 98, 99, 100]`
- target-rate regularizer: scale `1.0`, scalar limit `2.0 rad/s`
- ONNX: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate2p0_bc_candidate/candidate.onnx`
- ONNX sha256: `e359a3f095d0b88299340a2caca48b686dda758640020f3a017bdb221d44d279`
- NPZ sha256: `0550e90cae60d1fc57552f38f366e3bc58f891f1641c0612d5572d72715190fe`

## Fit Result

- fit status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- MAE: `0.010195`
- p95 abs error: `0.028445`
- max abs error: `0.947577`
- target-rate p95: `1.623235 rad/s`
- target-rate p99: `1.918720 rad/s`
- target-rate max: `2.467730 rad/s`
- ONNX fidelity p95 abs error: `0.00000015`
- ONNX fidelity max abs error: `0.00000027`

Compared with the prior contact+phase fit, this lowered target-rate max from
`2.991217` to `2.467730 rad/s`, but increased p95 action error from `0.015610`
to `0.028445`.

## x=0.08 Boundary Screen

Task: `rough_terrain_backlash`, z-scale `0.0025`, corrected fitted bridge,
seeds `0,3,4,6`, duration `15s`.

| seed | status | samples | mean vx | track ratio | max vel excess | tracking p95 |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0242 | 0.3020 | 0.0000 | 0.1919 |
| 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0214 | 0.2680 | 0.0143 | 0.1895 |
| 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0256 | 0.3206 | 0.0374 | 0.1919 |
| 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0260 | 0.3252 | 0.0501 | 0.1931 |

Distribution:

- falls: `0/4`
- duration complete: `4/4`
- mean track ratio: `0.3040`
- mean vx: `0.0243 m/s`
- p95 velocity excess mean: `0.0000`
- max instantaneous velocity excess mean: `0.0254`

This is a near-pass relative to the previous contact+phase fit:

- previous contact+phase: 0/4 x=0.08 seeds passed, max excess mean `0.5040`
- rate2p0 contact+phase: 1/4 x=0.08 seeds passed, max excess mean `0.0254`

The tradeoff is reduced forward progress:

- previous contact+phase track ratio: `0.4211`
- rate2p0 contact+phase track ratio: `0.3040`

## x=0.0 Preservation Screen

Task: `rough_terrain_backlash`, z-scale `0.0025`, corrected fitted bridge,
seeds `0-1`, duration `15s`.

| seed | status | samples | mean vx | max vel excess | tracking p95 |
|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | -0.0004 | 0.0000 | 0.0327 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | -0.0013 | 0.0000 | 0.0320 |

Distribution:

- falls: `0/2`
- duration complete: `2/2`
- mean vx: `-0.0008 m/s`
- zero-command semantics preserved

## Decision

`HOLD_RATE2P0_BC_TINY_TARGET_VELOCITY_EXCESS`

The stronger target-rate regularizer nearly resolves the instantaneous
corrected-envelope issue while preserving x=0.0 behavior, but it is not
promotable because 3/4 screened x=0.08 boundary seeds still exceed the
instantaneous target-velocity envelope.

Next step: either tighten the label/model projection slightly more, or implement
per-joint target-rate projection so the right ankle and right hip pitch are
clamped without over-smoothing the whole gait. Any next candidate must be
re-screened on the same boundary seeds before a full 8-seed gate.

Robot validation remains blocked.
