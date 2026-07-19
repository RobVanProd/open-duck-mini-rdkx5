# Real-Build Torso-COM Direct-Reaction Preregistration

Status: `PREREGISTERED_DIRECT_POWERED_OFF_MEASUREMENT_ROUTE`

Formal physical measurements read: `0`

## Question

Can the X-axis COM of the complete as-built torso-fixed assembly be measured
directly, rather than reconstructed from the eight-group/46-field component
ledger, and does its complete uncertainty interval fit the selected composite
winner's unchanged asymmetric COM allowance?

This is an alternative evidence route to the same frozen deployment question.
It does not alter the policy, simulator, break-radius result, thresholds, or
authority boundary.

## Source-locked body and datum

The measured specimen is exactly the physical counterpart of simulator body 2
`trunk_assembly`: all parts fixed to that body are installed in deployment
configuration, while articulated child assemblies are excluded at the two hip
yaw joints and the neck pitch joint.

The physical datum is the X coordinate of the midpoint of the left and right
hip-yaw rotation axes. The clean upstream v2 URDF at commit
`b23317a485b3cec7d8417f352478778b3475173c` places both axes at X = `-0.019 m`
in `trunk_assembly`; its SHA-256 is
`a42c5ff3213b4662d81708807d698ab63d4e7432a54b4112728969d45928b54b`.
The simulator XML independently agrees and is frozen by SHA-256
`968b18de4e3f55b31252155f52779fa490989f5da92bc9b308e0bb4e81d6bb5c`.
Physical +X is the robot's forward/toe direction at home. The operator records
support coordinates relative to the hip-axis datum in that signed frame and
records one uncertainty for locating the datum on the specimen.

## Frozen specimen contract

The measurement is valid only when evidence confirms all of the following:

1. RDK-X5, exact battery arrangement, thermal stack, mounts, torso wiring,
   covers, fasteners, bus/IMU/power hardware and any ballast are installed as
   intended for deployment.
2. The robot is powered off and electrically disconnected; no software,
   serial, RDK-X5, motor or torque command is used.
3. Both complete leg chains are excluded at the left/right hip-yaw joint
   boundaries and the head/neck child assembly is excluded at the neck-pitch
   joint boundary. Torso-fixed servo portions remain with the torso.
4. No stand, cable, hand or child assembly carries specimen load during a
   reading. Supports/fixtures are tared.
5. Before/after configuration photographs and an inventory attestation make
   the measured-body boundary auditable.

Failure of any specimen predicate produces
`INVALID_DIRECT_REACTION_SPECIMEN_BOUNDARY`, never a numerical deployment
comparison.

## Frozen apparatus and trials

- Use two independently tared vertical-reaction scales or load cells under two
  transverse knife-edge supports at coordinates `x_a < x_b`.
- The complete uncertainty intervals of the support coordinates must be
  ordered and their minimum separation must be at least `0.060 m`.
- Record one conservative uncertainty for each scale/load cell, including
  resolution, calibration and repeatability.
- Unload and reload the specimen for exactly three formal trials. Record both
  positive reaction readings and immutable evidence for every trial.
- Independently weigh the complete same specimen. Every trial's reaction-sum
  interval must overlap the independent total-mass interval.
- The three trial COM intervals must share a nonempty intersection. The final
  reported interval is nevertheless the conservative union/envelope of the
  three trial intervals, not their narrower intersection.

For each trial, static moment balance gives

`x_rel = (r_a*x_a + r_b*x_b) / (r_a + r_b)`.

The deterministic calculator enumerates every endpoint of the independent
support-coordinate and reaction-load uncertainty box. It then adds the fixed
hip-axis datum `-0.019 m` and the common datum-location uncertainty once.

## Frozen comparison

The simulator torso comparator remains X =
`-0.04832589998841286 m`. The break-radius result remains SHA-256
`6b84b34e7280b0f0d92109a70444d18af7b0196cd3555530b8f42e70dea54e32`.
After reserving the unchanged `0.00078125 m` curve-resolution margin, the full
sim-to-real error interval must remain inside:

- lower: `-0.021875 m`;
- upper: `+0.0046875 m`.

No threshold is changed after measurement.

## Frozen decisions

- `PASS_REAL_BUILD_DIRECT_COM_INSIDE_CERTIFIED_RADIUS`
- `HOLD_REAL_BUILD_DIRECT_COM_OUTSIDE_CERTIFIED_RADIUS`
- `HOLD_REAL_BUILD_DIRECT_COM_INPUTS_INCOMPLETE`
- `INVALID_DIRECT_REACTION_SPECIMEN_BOUNDARY`
- `INVALID_DIRECT_REACTION_MEASUREMENT_CONSISTENCY`

A pass closes only the policy-side real-build X-COM measurement blocker. It is
not robot clearance and does not authorize Gate 5, deployment, robot/RDK-X5
access, torque, motors, training, hosted compute, GPU or iGPU use. A measured
outside result can support only a separately preregistered simulator model
correction and unchanged re-gate. No closest or nominal-value promotion exists.

## Frozen implementation artifacts

- `real_build_torso_com_direct_reaction_template.json`
- `tools/evaluate_real_build_torso_com_direct_reaction.py`
- `tests/test_evaluate_real_build_torso_com_direct_reaction.py`
- `REAL_BUILD_TORSO_COM_DIRECT_REACTION_CONTRACT_20260719.md`
- `real_build_torso_com_direct_reaction_contract.json`
- `REAL_BUILD_TORSO_COM_DIRECT_REACTION_RESULT_20260719.md`
- `real_build_torso_com_direct_reaction_result.json`

The blank-template contract may run on CPU before physical values exist. It
must execute zero robot/RDK-X5 actions, report no numerical COM estimate, and
return `HOLD_REAL_BUILD_DIRECT_COM_INPUTS_INCOMPLETE`.
