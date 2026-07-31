# Viability Prevention Metric Preregistration

Status: `PREREGISTERED_BEFORE_COMPARATOR_REPLAY`

B1 uses exactly the 298 committed oracle-COM failure states. Each state is a
33-D vector: 14 actual actuator-joint positions, the corresponding 14 joint
velocities, base roll, base pitch, base height, and two contact bits.

Positions are normalized by 0.25 rad; velocities by the frozen measured
per-joint velocity limits; roll and pitch by 0.20 rad; height by 0.05 m; and
contacts by one. Distance is RMS normalized Euclidean distance.

The neighborhood radius is the 95th percentile of each frozen state's nearest
different-tick neighbor within the same condition, policy, fit and command
trajectory. Thus the radius is calibrated only from the four-tick failure
state cadence before any comparator replay. It will not be widened after B2.

X_NEG neighborhoods carry weight 3 and X_POS weight 1, reflecting the frozen
4-tick versus 12-tick recovery-window asymmetry. This phase performs no
simulation or training. Robot clearance remains `NO`.
