# Phase 2 z=0.0025 Contact+Phase Rate1p9 BC Boundary Decision

status: `PASS_RATE1P9_BOUNDARY_SUBSET`

This was an offline supervised BC fit and CPU sim screen. It did not SSH,
deploy, train PPO, run robot tests, or change runtime behavior.

## Candidate

- source manifest: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0/live_oracle_dagger_aggregate_manifest.json`
- aggregate dataset_id: `e1d14b2c3f81d443`
- aggregate samples: `10500`
- model: contact+phase-modulated feed-forward BC student
- context indices: `[6, 97, 98, 99, 100]`
- target-rate regularizer: scale `1.5`, scalar limit `1.9 rad/s`
- ONNX: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- ONNX sha256: `f00ba8a89f4e24e7c393309acd434cbc95132473aa3df562dacf4fe527049822`
- NPZ sha256: `713c58e1600d6da4e7519c61e50ff0870166da88415b645cfd78c7436e188aeb`

## Fit Result

- fit status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- MAE: `0.007882`
- p95 abs error: `0.024644`
- max abs error: `0.527430`
- target-rate p95: `1.662375 rad/s`
- target-rate p99: `1.874476 rad/s`
- target-rate max: `2.037482 rad/s`
- ONNX fidelity p95 abs error: `0.00000018`
- ONNX fidelity max abs error: `0.00000048`

## x=0.08 Boundary Screen

Task: `rough_terrain_backlash`, z-scale `0.0025`, corrected fitted bridge,
seeds `0,3,4,6`, duration `15s`.

| seed | status | samples | mean vx | track ratio | max vel excess | tracking p95 |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0289 | 0.3616 | 0.0000 | 0.1945 |
| 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0255 | 0.3184 | 0.0000 | 0.1945 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0318 | 0.3971 | 0.0000 | 0.1923 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0312 | 0.3903 | 0.0000 | 0.1917 |

Distribution:

- falls: `0/4`
- duration complete: `4/4`
- passed: `4/4`
- mean track ratio: `0.3668`
- mean vx: `0.0293 m/s`
- p95 velocity excess mean: `0.0000`
- max instantaneous velocity excess mean: `0.0000`
- mean single support: `21.5%`
- mean double support: `78.5%`

## x=0.0 Preservation Screen

Task: `rough_terrain_backlash`, z-scale `0.0025`, corrected fitted bridge,
seeds `0-1`, duration `15s`.

| seed | status | samples | mean vx | max vel excess | tracking p95 |
|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | -0.0001 | 0.0000 | 0.0374 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | -0.0009 | 0.0000 | 0.0399 |

Distribution:

- falls: `0/2`
- duration complete: `2/2`
- passed: `2/2`
- mean vx: `-0.0005 m/s`
- zero-command semantics preserved

## Decision

`PASS_RATE1P9_BOUNDARY_SUBSET`

The rate1p9 contact+phase BC candidate clears the four z=0.0025 boundary seeds
that previously failed and preserves zero-command behavior. It is not yet a
promoted candidate because the standard full x=0.08 gate is eight seeds.

Next step: run the full 8-seed x=0.08 gate and the standard x=0.0 gate against
the corrected bridge. If both pass, this becomes the next offline Phase 2
candidate for further robustness screening. Robot validation remains blocked.
