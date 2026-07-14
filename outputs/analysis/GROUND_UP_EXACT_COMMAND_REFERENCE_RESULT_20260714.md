# Ground-Up Exact-Command Reference Result

status: `CLOSE_EXACT_COMMAND_LOOKUP_NO_VALID_TEACHER`

## Result

| arm | passing runs | completed backward | falls | decision |
|---|---:|---:|---:|---|
| `N0_NEAREST_GRID` | 0/4 | 2 | 2 | control failed |
| `N1_EXACT_INTERPOLATED` | 0/4 | 2 | 2 | no improvement |

The exact-command table fixed a real lookup defect but did not fix behavior.
Every exact-interpolated run failed the frozen emergence gate. Seed `100`
completed at both commands but moved backward; seed `101` fell and moved
backward at both commands.

Nearest-grid x=`0.074` and x=`0.08` produced identical trajectories because
both commands alias to one table row. Exact interpolation removed that alias,
but the resulting trajectories still moved backward or fell.

## Contract evidence

- original table SHA-256:
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`
- exact table SHA-256:
  `75409f6759df47b1f08c0540476ad10bca82e846908a534a4a079c2e0b99272b`
- step-zero final-action ONNX SHA-256:
  `b7adb8981e920d9e690f42256e0a84ab0bf0c2020443fe7979ddbb450d5d43d7`
- maximum exact-versus-nearest action difference: `0.212030`
- exact table maximum absolute action: `0.545254`
- every interpolated joint-rate envelope check passed
- execution: local CPU only

## Decision

Close the exact-command lookup hypothesis. The polynomial/projected reference
is not a valid open-loop teacher under the frozen simulator and actuator
bridge, even after command interpolation. Do not spend accelerator compute on
another cloning, reference-only conditioning, or reference-anchoring variant.

The reference may remain a tracking target, as the original search plan
specified, but the next formulation must provide a genuinely closed-loop
source of corrective behavior. Selecting that mechanism requires a separate
evidence audit; it is not inferred from training reward or visual preference.

There is no offline winner and no robot clearance.
