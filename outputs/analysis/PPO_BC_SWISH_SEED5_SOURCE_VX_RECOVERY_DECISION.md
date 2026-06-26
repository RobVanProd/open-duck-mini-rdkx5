# PPO BC Swish Seed-5 Source-VX Recovery Decision

status: `HOLD_COMMAND_CONDITIONING_REQUIRED`

Source-VX relabeling removed the seed-5 reverse/fall basin, but the step-0 policy walks forward at command_x=0.0, so it is not ready for PPO or robot validation until command-conditioned standstill data/loss is added.

## Artifacts

- source_vx_relabel: `outputs/analysis/PPO_SWISH_SEED5_RELABEL_SOURCE_VX.md`
- manifest: `outputs/analysis/PPO_SWISH_SEED5_SOURCE_VX_RECOVERY_MANIFEST.md`
- bc_fit: `outputs/analysis/PPO_LOC_SWISH_SEED5_SOURCE_VX_RECOVERY_BC_STUDENT.md`
- export_fidelity: `outputs/analysis/PPO_BC_SWISH_SEED5_SOURCE_VX_RECOVERY_STEP0_EXPORT_FIDELITY.md`
- x008_gate: `outputs/analysis/PPO_BC_SWISH_SEED5_SOURCE_VX_RECOVERY_STEP0_VALIDATION_FITTED_BACKLASH.md`
- x000_gate: `outputs/analysis/PPO_BC_SWISH_SEED5_SOURCE_VX_RECOVERY_STEP0_VALIDATION_FITTED_BACKLASH_X0.md`

## Relabel Teacher

- teacher: `source_vx_blend` over `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- blend_alpha: `0.80`
- vx_blend_alpha: `1.00`
- vx_blend_threshold_m_s: `-0.02`
- source_vx_threshold_m_s: `0.02`
- alt_exclude_source_regex: `_seed4/`
- active model counts: `{'alt': 14, 'primary': 60}`
- action delta p95: `0.1506`

## BC Fit

- samples: `9342`
- MAE: `0.011618`
- p95 abs error: `0.035149`
- max abs error: `0.257882`
- target-rate p95: `2.2317` rad/s
- target-rate max: `4.3525` rad/s

## Gate Comparison

| metric | weak seed-5 relabel x=0.08 | source-VX x=0.08 | source-VX x=0.0 |
|---|---:|---:|---:|
| falls | 1 / 8 | 0 / 8 | 0 / 8 |
| duration complete | 7 / 8 | 8 / 8 | 8 / 8 |
| mean vx | 0.0120 | 0.0416 | 0.0415 |
| mean track ratio | 0.1496 | 0.5201 | NA |
| min samples | 75 | 500 | 500 |
| max pitch velocity p95 mean | 3.9029 | 3.8218 | 3.8335 |
| max tracking p95 mean | 0.2733 | 0.2662 | 0.2657 |

## Interpretation

- Source-VX relabeling is qualitatively better than plain blend relabeling: seed 5 changes from fall/termination to full-duration completion.
- At x=0.08, all 8 seeds complete under the fitted bridge with mean vx 0.0416 m/s and mean track ratio 0.5201.
- The policy still holds on tracking, so it is not deployable.
- At x=0.0, all 8 seeds also complete, but mean vx is 0.0415 m/s, showing the BC warm-start has learned a forward gait without command conditioning.
- Do not start PPO from this checkpoint until either command-conditioned standstill data is added or the PPO objective/initialization plan explicitly handles zero-command correction as the first training phase.

## Next Gate

Add command-conditioned standstill/no-motion data or an explicit zero-command correction phase, then rerun x=0.0 and x=0.08 fitted step-0 gates before PPO.
