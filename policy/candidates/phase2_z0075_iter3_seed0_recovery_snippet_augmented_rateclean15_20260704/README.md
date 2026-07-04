# Phase 2 z=0.0075 Iter3 Snippet-Augmented Rateclean15

status: `HOLD_RATE_CLEAN_REINTRODUCED_SEED0_FALL`

This candidate is preserved as an offline evidence artifact. It is not
promoted.

## Files

- `candidate.onnx`
- `student.npz`

## Hashes

- candidate.onnx: `924699fc7b4c580181b715f37dd2d22fd506352399ec0d25de34377a993ed265`
- student.npz: `acd2fcc6e34ff823a65b2073a554efa45462b771dd8f47178236ec69868885a5`

## Fit

- manifest: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_snippet_augmented_weighted_manifest.json`
- dataset_id: `9f4ba6b1c342d17b`
- target-rate regularization: limit `1.5 rad/s`, scale `1.0`
- samples: `51294`
- MAE: `0.010091`
- p95 abs error: `0.034079`
- max abs error: `0.671804`
- target-rate p95: `1.332225 rad/s`
- target-rate max: `1.669861 rad/s`
- ONNX max abs error: `0.00000024`

## Compact Boundary Screen

z=0.0075 rough terrain, fitted corrected bridge, intermediate pushes
0.075-0.125:

- x=0.08 seed 0: `HOLD_CANDIDATE_FALL_OR_TERMINATION`, 116 samples,
  track ratio `2.1662`, p95/max velocity excess `0.0000/0.0000`
- x=0.08 seed 7: `PASS_CANDIDATE_SIM_GATE`, 750 samples,
  track ratio `0.4022`, p95/max velocity excess `0.0000/0.0000`
- x=0.0 seeds 0 and 1: `PASS_CANDIDATE_SIM_GATE`, mean vx `0.0008 m/s`,
  no velocity excess

## Decision

Do not promote this candidate. It proves global rate regularization can remove
the non-rateclean snippet candidate's target-velocity excess, but it also
removes enough recovery behavior that seed 0 falls again.

No robot validation, SSH, deploy, grounded replay, runtime behavior change, or
PPO training was performed.
