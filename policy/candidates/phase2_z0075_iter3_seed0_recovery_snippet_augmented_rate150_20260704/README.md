# Phase 2 z=0.0075 Iter3 Snippet-Augmented Rate150

status: `HOLD_RECOVERY_TRANSFERRED_BUT_RATE_SPIKED`

This candidate is preserved as an offline evidence artifact. It is not
promoted.

## Files

- `candidate.onnx`
- `student.npz`

## Hashes

- candidate.onnx: `c6e665b743468e796b070ba3bd405627fb42f3c611ddac257fbfbfb33e132c84`
- student.npz: `8c9cbc4b5737b4424ae2161b068afad13fd382dea2afe0fefa3382f6a635111d`

## Fit

- manifest: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_snippet_augmented_weighted_manifest.json`
- dataset_id: `9f4ba6b1c342d17b`
- samples: `51294`
- weighted samples: `51889.0000`
- MAE: `0.009070`
- p95 abs error: `0.028178`
- max abs error: `0.670479`
- target-rate p95: `1.355027 rad/s`
- target-rate max: `5.560378 rad/s`
- ONNX max abs error: `0.00000024`

## Compact Boundary Screen

z=0.0075 rough terrain, fitted corrected bridge, intermediate pushes
0.075-0.125:

- x=0.08 seed 0: `HOLD_CANDIDATE_TARGET_VELOCITY`, 750 samples,
  track ratio `0.4275`, p95/max velocity excess `0.0000/0.3722`
- x=0.08 seed 7: `HOLD_CANDIDATE_TARGET_VELOCITY`, 750 samples,
  track ratio `0.4098`, p95/max velocity excess `0.0000/0.2734`
- x=0.0 seeds 0 and 1: `PASS_CANDIDATE_SIM_GATE`, mean vx `0.0009 m/s`,
  no velocity excess

## Decision

Do not promote this candidate. It demonstrates that targeted oracle-labelled
push-window snippets can transfer seed-0 recovery and preserve zero-command
semantics, but the recovered behavior still needs target-rate cleanup before a
wider Phase 2 gate.

No robot validation, SSH, deploy, grounded replay, runtime behavior change, or
PPO training was performed.
