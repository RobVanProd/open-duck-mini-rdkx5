# Ground-Up A1 Hardware-Vector Survival Preregistration

status: `PREREGISTERED_BEFORE_EXECUTION`

## Protected control

A1 reference-residual at 4M, deterministic home reset, x=`0.074`, seeds
`100/101`, 1.08 seconds, projected reference phase 0, and fitted bridge. The
corrected unprojected result passes gait emergence 2/2 with mean body velocity
`0.06398 m/s`, but its target-rate excess reaches `4.24 rad/s`.

## One diagnostic arm

Change only the policy-output projection. Starting from home action zero, bound
each action delta by the measured 14-joint velocity vector times `dt / 0.25`:

`[5.24,5.24,1.5,1.5,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.0,1.25] rad/s`.

The values come from the frozen reference-feature hardware contract. The
reference cycle itself has zero vector excess. No gain, phase, action, model,
bridge, command, reset, seed, or threshold changes.

The diagnostic passes only if both seeds complete, retain positive body-forward
gait and bilateral transitions, have no constant saturation, and reduce maximum
rate excess to numerical zero (`<=1e-5 rad/s`). A pass means the nominal gait
survives hardware-feasible projection; it does not make the wrapper a final
policy or authorize robot use. A failure closes A1 as a transferable bootstrap.

Local CPU only. No training, Colab, GPU, RDK-X5, robot, torque, or motor access.
