# Ground-Up Dual-Fit Conservative-Envelope Repair Preregistration

status: `PREREGISTERED_CPU_ONLY`

R1 did not expose a gait, x=0, tracking, posture, or saturation failure. It
exposed one invariant mismatch in all six P31/34 moving cells: the guarded
policy reaches `1.750001 rad/s` at the left ankle, while the independently
measured P31/34 fit limits that joint to `1.50 rad/s`.

Before spending Colab credit, this screen changes exactly one stored graph
constant: `max_action_delta[0,4]` from `.14` to `.12` normalized action per
tick (`1.50 * .02 / .25`). Every node, interface, other initializer, deadband,
and actual-position guard remains unchanged.

The transform must first prove graph identity, exact zero-command behavior,
finite CPU inference, the new chained left-ankle bound, and unchanged bounds
for the other five pitch joints. Only then may the same frozen 16 R1 cells run
under both P30 and P31/34 fits.

Both checkpoints must pass x=0 and all three moving commands under both fits,
including zero envelope excess against each fit. A pass only repairs and
re-enters R1 and authorizes the R2 contract. A failure closes this inference-
only repair and permits preregistration—not execution—of a bounded dual-fit
training search. No training, Colab, local GPU, RDK-X5, or robot access is
authorized by this preregistration.
