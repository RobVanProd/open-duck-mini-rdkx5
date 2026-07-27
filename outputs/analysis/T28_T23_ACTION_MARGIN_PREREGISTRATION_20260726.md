# T28 T23 action-margin repair preregistration

status: `PREREGISTERED_T28_T23_ACTION_MARGIN_REPAIR`

## Attribution

- T27 failed `6` of 16 condition-1 cells; `39` individual action values crossed the frozen 0.98 margin.
- Every failed cell still passed gait, tracking, duration, rate, handoff, override readback, and corrected motor-duration protection.
- Worst absolute action was `0.988259614`, below the hard normalized bound.

## Frozen transform

`L = nextafter(float32(0.98), 0) = 0.9799999595`; clip both the deployed action and its recurrent feedback to `[-L,L]` after the complete source graph.

The same transform is applied to both checkpoints. There is no joint, command, trace, or fit-specific value and no training.

Passing the asset contract authorizes only preregistration of the 16-cell floor-friction-0.5 CPU falsifier. It does not authorize training, Gate 5, RDK-X5, robot, torque, or motion.
