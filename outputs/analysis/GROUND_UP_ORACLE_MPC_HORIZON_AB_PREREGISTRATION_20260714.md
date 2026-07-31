# Ground-Up Oracle MPC Horizon A/B Preregistration

status: `PREREGISTERED_BEFORE_CORRECTED_HORIZON_PROBE`

## Protected control

`C0_H8` is the completed corrected body-frame probe: horizon 8 ticks,
population 64, elites 8, iterations 4, action block 2, and the frozen objective.
It passes zero of two source gates: seed 100 moves robustly but touches
saturation; seed 101 falls and reverses.

## New causal arm

`C1_H16` changes only prediction horizon from 8 (`0.16 s`) to 16 ticks
(`0.32 s`). It retains:

- the exact same objective and weights;
- population `64`, elites `8`, iterations `4`;
- standard deviations `0.20` / `0.03`;
- two-tick action blocks;
- exact reference proposal center;
- fitted bridge and measured action-rate clipping;
- command x=`0.074`, seeds `100/101`, duration `1.08 s`;
- body-local progress/lateral terms and relative-yaw term.

C1 advances only if both seeds complete, have positive body-forward progress
and mean velocity, bilateral contact transitions, max absolute action below
`0.999`, and zero rate excess. A one-seed improvement is not a source pass.

If C1 fails, do not tune horizon or weights again. Close this fixed shooting
formulation and audit whether action-sequence parameterization—not scoring—is
the remaining limitation.

Local CPU only. No Colab, GPU, RDK-X5, robot, torque, or motor access is
authorized.
