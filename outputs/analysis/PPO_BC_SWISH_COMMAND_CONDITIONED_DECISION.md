# PPO BC Swish Command-Conditioned Decision

status: `HOLD_X0_HARD_SEED_STANDSTILL_STABILITY`

Command-conditioned BC preserves x=0.08 motion and removes zero-command drift on easy seeds, but x=0.0 still falls on seeds 3 and 5. Do not start PPO or robot validation from this checkpoint.

## Artifacts

- zero_action_policy: `outputs/analysis/zero_action_policy.onnx`
- zero_action_x0_trace_gate: `outputs/analysis/ZERO_ACTION_STANDSTILL_X0_TRACE_GATE.md`
- manifest: `outputs/analysis/PPO_SWISH_COMMAND_CONDITIONED_MANIFEST.md`
- bc_fit: `outputs/analysis/PPO_LOC_SWISH_COMMAND_CONDITIONED_BC_STUDENT.md`
- export_fidelity: `outputs/analysis/PPO_BC_SWISH_COMMAND_CONDITIONED_STEP0_EXPORT_FIDELITY.md`
- x000_gate: `outputs/analysis/PPO_BC_SWISH_COMMAND_CONDITIONED_STEP0_VALIDATION_FITTED_BACKLASH_X0.md`
- x008_gate: `outputs/analysis/PPO_BC_SWISH_COMMAND_CONDITIONED_STEP0_VALIDATION_FITTED_BACKLASH_X008.md`

## BC Fit

- samples: `12342`
- MAE: `0.010749`
- p95 abs error: `0.032331`
- max abs error: `0.306286`
- target-rate p95: `1.9567` rad/s
- target-rate max: `4.5019` rad/s

## Gate Comparison

| metric | zero action x=0.0 | source-VX recovery x=0.0 | command-conditioned x=0.0 | command-conditioned x=0.08 |
|---|---:|---:|---:|---:|
| falls | 2 / 8 | 0 / 8 | 2 / 8 | 0 / 8 |
| duration complete | 6 / 8 | 8 / 8 | 6 / 8 | 8 / 8 |
| mean vx | -0.0846 | 0.0415 | -0.0783 | 0.0413 |
| mean track ratio | NA | NA | NA | 0.5160 |
| min samples | 48 | 500 | 53 | 500 |
| max pitch velocity p95 mean | 0.0000 | 3.8335 | 0.2600 | 3.7717 |
| max tracking p95 mean | 0.0607 | 0.2657 | 0.0603 | 0.2638 |

## Interpretation

- Adding six stable zero-action standstill traces corrected the easy-seed x=0.0 velocity behavior: passing seeds now have near-zero vx instead of walking forward.
- The mixed candidate preserves x=0.08 movement: all eight seeds complete, mean vx 0.0413 m/s, mean track ratio 0.5160.
- The zero-action source itself falls on seeds 3 and 5, and the mixed candidate inherits those hard-seed zero-command failures.
- The next blocker is not x=0.08 seed-5 recovery. It is finding a stable x=0.0 standstill controller/data source for seeds 3 and 5.

## Next Gate

Find or generate stable x=0.0 standstill/recovery examples for seeds 3 and 5, then retrain the command-conditioned warm-start and rerun both x=0.0 and x=0.08 gates.
