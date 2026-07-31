# Ground-Up Command-Deadband Repair Preregistration

status: `PREREGISTERED_CPU_ONLY`

The nominal G1/T2 winner was trained only on `x=.074–.080`. Direct `x=0`
saturates 87.67–95.73% of actions and falls, while the guard, rate, and tracking
metrics remain causal non-failures. The repair is therefore command support,
not another gait or actuator change.

For raw observation command index 6:

- `|x| <= .01`: output 14 normalized zeros (home targets), and return the same
  zero vector as `previous_action_out`;
- `x >= .074`: preserve both source outputs bit-exactly;
- `.01 < |x| < .074`: outside this repair's authority and not evaluated.

Both selected half/final policies must first pass a CPU graph contract. The
behavior matrix then contains x=0 and x=.074/.077/.080, seeds 100/101, 600
ticks, for both checkpoints: exactly 16 cells. Both checkpoints must pass the
frozen x=0 standstill gate and the unchanged six-cell nominal gate.

Passing advances only to a separately preregistered robustness ladder. It does
not authorize training, Colab, local GPU, RDK-X5, robot, deployment, torque, or
motor access.
