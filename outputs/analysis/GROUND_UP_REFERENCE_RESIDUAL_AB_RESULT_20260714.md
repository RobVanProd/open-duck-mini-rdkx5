# Ground-Up Reference-Residual A/B Result

status: `NO_REFERENCE_RESIDUAL_WINNER`

## Outcome

The reference-anchored residual actor failed the preregistered offline gate and
performed worse than its clean reference-conditioned control.

| arm | passing runs | persistent seeds | hard failures | full checkpoints |
|---|---:|---:|---:|---:|
| `A0_CURRENT_REFCOND` | 1/8 | 0 | 7 | 0 |
| `A1_REFERENCE_ANCHORED_RESIDUAL` | 0/8 | 0 | 8 | 0 |

A0's only pass was x=`0.074`, seed `100`, at 3,010,560 steps. It did not
persist at 4,014,080. A1 had no passing run at either checkpoint. At both A1
checkpoints, x=`0.08`, seed `100` completed with positive displacement but was
a constant saturated action vector; seed `101` fell with the same saturation
failure. Both A1 x=`0.074`, seed `101` runs fell, while seed `100` completed but
moved backward.

Therefore A1 fails both required conditions: it does not pass all eight runs
and it does not outrank A0. It is eliminated without post-hoc tuning.

## Training and artifact contract

- Playground commit: `b9be205ac64488c23504ca42e5ec790337adeec3`
- Colab device contract: JAX/JAXlib `0.8.2`, MuJoCo `3.9.0`, Playground
  `0.0.5`, one CUDA T4
- A0 training seconds: `1003.894675856`
- A1 training seconds: `830.947760504`
- hosted sweep seconds: `1884.952218033`
- A0 archive SHA-256:
  `6d511666a6435dc565dd026d67642eb89d8cf4bec1c08be94466d3d20e44eb0c`
- A1 archive SHA-256:
  `7cccf38d1bea2596d0fd44c8e9eeabc3248f0321e39adaa4707a5a9e59788564`
- A1 3M ONNX SHA-256:
  `77d2736ba0cc4114dfbf95ea55c40312a64dc62f81d26f9d12ef6ffcdb24044f`
- A1 4M ONNX SHA-256:
  `60534a3fe273294520c5e5f05fa2671440c885be63f820ddf38b7d65183f7296`

Both archives and the final manifest were recovered before the Colab session
was stopped. Colab then reported zero active sessions. All behavior evaluation
ran on local CPU. No robot, RDK-X5, local iGPU, or onboard GPU was accessed.

## Evidence-selected next audit

The current reference lookup does not provide the commanded reference point.
For command `[0.074, 0, 0]`, the L1 nearest-neighbor lookup selects table row
`[0.074, -0.037, -0.074]`; an equal-distance lateral row also exists, and the
table contains no zero lateral or zero yaw coordinate. The two tied lateral
rows differ by as much as `0.38466` normalized action units across the cycle.

Before more accelerator use, quantify exact-command interpolation and test the
interpolated reference itself in the existing CPU-only reference audit. This
is an input-contract correction audit, not authorization to retrain. Direct
cloning, the nearest-reference conditioned actor, and the nearest-reference
anchored residual actor remain rejected.

There is no offline winner and no robot clearance.
