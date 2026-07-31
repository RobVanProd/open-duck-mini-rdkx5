# Ground-Up Exact-Command Reference CPU Preregistration

status: `PREREGISTERED_BEFORE_DIAGNOSTIC_EXECUTION`

## Evidence

The reference-conditioned and reference-anchored A/B used nearest-neighbor
reference lookup. For intended command `[0.074, 0, 0]`, that lookup selects
`[0.074, -0.037, -0.074]`. The table contains no zero lateral/yaw cell.

Trilinear interpolation over the frozen projected table changes the action
cycle by up to `0.211943` normalized units at x=`0.074` and `0.212030` at
x=`0.08`. The exact rows remain within the action and per-joint velocity
envelopes. Exact-table SHA-256:
`75409f6759df47b1f08c0540476ad10bca82e846908a534a4a079c2e0b99272b`.

## Frozen diagnostic

Use the previously CPU-verified step-zero reference-residual ONNX, whose
deterministic final action equals the appended reference action. Compare:

- `N0_NEAREST_GRID`: original projected table SHA-256
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`;
- `N1_EXACT_INTERPOLATED`: exact-command table SHA-256
  `75409f6759df47b1f08c0540476ad10bca82e846908a534a4a079c2e0b99272b`.

Everything else is frozen: ONNX SHA-256
`b7adb8981e920d9e690f42256e0a84ab0bf0c2020443fe7979ddbb450d5d43d7`,
fitted bridge, flat-backlash task, reference phase `0`, observation `115`,
x=`0.074/0.08`, seeds `100/101`, and duration `1.08 s`.

N1 is materially valid only if it passes all four runs with no fall/nonfinite,
no nonpositive displacement/mean velocity, and no constant saturated action
vector. A score increase short of all four is diagnostic improvement, not a
teacher or training authorization. If N1 does not outperform N0, close the
exact-command lookup hypothesis.

This is local CPU simulation only. No Colab, local GPU, iGPU, onboard GPU,
RDK-X5, robot, torque, or motor access is authorized.
