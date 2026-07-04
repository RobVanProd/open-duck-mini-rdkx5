# Phase 2 z0.0075 Iter21 Balanced Post-Push Recovery Rate150

Status: `HOLD_SEED6_7_POST_PUSH_STABILITY`

This candidate merged the Iter21 early-lunge recovery base, the seed5 late post-push
recovery snippets, and the seed2/3/6 regressed-seed recovery snippets. It improved the
focused x=0.08 rough-terrain intermediate-push screen but did not clear it.

## Files

- `candidate.onnx`
- source manifest: `outputs/analysis/phase2_z0075_iter21_balanced_post_push_recovery_merged_manifest.json`
- student report: `outputs/analysis/PHASE2_Z0075_ITER21_BALANCED_POST_PUSH_RECOVERY_RATE150_STUDENT.md`
- focused gate report: `outputs/analysis/PHASE2_Z0075_ITER21_BALANCED_POST_PUSH_RECOVERY_RATE150_X008_FOCUSED_SEED_SCREEN.md`

## Hashes

- candidate ONNX sha256: `78d66e100a983d8d99e875972acc73264ef54ab352e55489a7087361b05a090e`
- student NPZ sha256: `c7de3c05fd77b1057496eb09e14d887887bc8340cda2c2f11b60aa5a6c44fa31`
- merged manifest sha256: `a007f2c05ef2409b5eab9b81404ddb209de991e34f58ab84fce806f9cd9453c2`

## Focused Screen

x=0.08, `rough_terrain_backlash`, fitted corrected bridge, z=0.0075 roughness,
intermediate pushes, reset mode `home-support`, reset settle `10`.

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3427 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3800 | 0.0000 |
| 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3979 | 0.0000 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3696 | 0.0000 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 212 | 1.4723 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 619 | 0.7163 | 0.0000 |

## Decision

Do not deploy or promote this candidate. It is a useful baseline because it shows the
remaining failure is post-push rough-terrain stability transfer on seeds 6 and 7, with no
corrected-envelope velocity excess.
