# Real-Build Torso-COM Input Audit

Status: `HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`

Decision: `MEASURE_BUILD_SPECIFIC_MASS_AND_X_PLACEMENT`

## Available evidence

- The local stock Open Duck Mini repository contains the V2 URDF/MJCF and stock
  STL geometry, including Pi Zero and stock battery component geometry.
- The compiled simulator torso is body 2 `trunk_assembly`, mass
  0.6985260248184204 kg, with inertial X position
  -0.04832589998841286 m.
- Project evidence proves the physical build uses an RDK-X5 and a non-stock
  battery arrangement.

## Missing build-specific evidence

The workspace contains no RDK-X5-specific torso assembly CAD, no as-built mass
ledger, no common trunk datum for the installed components, and no measured X
positions or uncertainty bounds for the RDK-X5 thermal/mount stack and battery
assembly. Stock Pi Zero/battery geometry cannot answer the as-built question.

Per the preregistration, no numerical real-build COM or pass/fail comparison is
reported. Populate `real_build_torso_com_measurement_template.json` with scale
or build-CAD evidence before running the interval calculation. This hold does
not weaken the composite winner and does not authorize model correction.

