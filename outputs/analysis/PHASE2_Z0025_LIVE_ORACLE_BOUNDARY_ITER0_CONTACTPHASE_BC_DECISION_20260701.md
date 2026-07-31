# Phase 2 z=0.0025 Live-Oracle Contact+Phase BC Decision

status: `HOLD_CONTACTPHASE_BC_TARGET_VELOCITY`

This was an offline supervised BC fit and CPU sim screen. It did not SSH,
deploy, train PPO, run robot tests, or change runtime behavior.

## Candidate

- source manifest: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0/live_oracle_dagger_aggregate_manifest.json`
- aggregate dataset_id: `e1d14b2c3f81d443`
- aggregate samples: `10500`
- model: contact+phase-modulated feed-forward BC student
- context indices: `[6, 97, 98, 99, 100]`
- ONNX: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_bc_candidate/candidate.onnx`
- ONNX sha256: `344d851a50c5d20b820ab41cade134d743b8373543b27caf0385f1653259d3e9`
- NPZ sha256: `92a012a57fd82ef905146f3374e6bc64bff43d12f08c6e4e34337cbf4e621649`

## Fit Result

- fit status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- MAE: `0.005621`
- p95 abs error: `0.015610`
- max abs error: `0.477506`
- target-rate p95: `1.688535 rad/s`
- target-rate max: `2.991217 rad/s`
- ONNX fidelity p95 abs error: `0.00000012`
- ONNX fidelity max abs error: `0.00000024`

## x=0.08 Boundary Screen

Task: `rough_terrain_backlash`, z-scale `0.0025`, corrected fitted bridge,
seeds `0,3,4,6`, duration `15s`.

| seed | status | samples | mean vx | track ratio | max vel excess | tracking p95 |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0322 | 0.4022 | 0.6004 | 0.1953 |
| 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0305 | 0.3810 | 0.4152 | 0.1905 |
| 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0349 | 0.4364 | 0.5087 | 0.1921 |
| 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0372 | 0.4645 | 0.4916 | 0.1911 |

Distribution:

- falls: `0/4`
- duration complete: `4/4`
- mean track ratio: `0.4211`
- mean vx: `0.0337 m/s`
- mean single support: `26.2%`
- mean double support: `73.8%`
- p95 velocity excess mean: `0.0000`
- max instantaneous velocity excess mean: `0.5040`

Compared with the input boundary student on the same four seeds:

- track ratio improved from `0.2477` to `0.4211`
- mean vx improved from `0.0198 m/s` to `0.0337 m/s`
- but target-velocity hold expanded from seeds `0,4` to all `0,3,4,6`

## x=0.0 Preservation Screen

Task: `rough_terrain_backlash`, z-scale `0.0025`, corrected fitted bridge,
seeds `0-1`, duration `15s`.

| seed | status | samples | mean vx | max vel excess | tracking p95 |
|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0003 | 0.0000 | 0.0359 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | -0.0005 | 0.0000 | 0.0350 |

Distribution:

- falls: `0/2`
- duration complete: `2/2`
- mean vx: `-0.0001 m/s`
- zero-command semantics preserved

## Decision

`HOLD_CONTACTPHASE_BC_TARGET_VELOCITY`

The live-oracle aggregate fit made a meaningful movement improvement and
preserved zero-command behavior, but the deployable feed-forward student is not
promotable because every screened x=0.08 boundary seed violates the corrected
instantaneous target-velocity envelope.

The next fix should not be another scalar PPO/reward run. The most direct next
offline step is to add a label-side target-rate projection or per-joint
instantaneous envelope correction to the live-oracle relabeled traces, then
refit the same deployable contact+phase model and re-screen the same boundary
seeds.

Robot validation remains blocked.
