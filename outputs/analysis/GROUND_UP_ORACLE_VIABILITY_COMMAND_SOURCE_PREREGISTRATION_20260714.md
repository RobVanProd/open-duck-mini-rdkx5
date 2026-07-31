# Ground-Up Oracle Viability/Command Source Preregistration

status: `PREREGISTERED_BEFORE_EXECUTION`

## Evidence selecting the change

The protected H16 shooting result produced body-forward travel in both seeds,
but both trajectories fell near `0.81 rad` pitch. Their final body-local x
velocities were `0.6837` and `0.6562 m/s` against a `0.074 m/s` command. The
fixed objective explicitly rewarded unbounded displacement and terminal speed,
while treating stability as a weighted tradeoff. Its horizon/weight family is
closed.

## One new structural arm

`V1_VIABILITY_COMMAND_LEXICOGRAPHIC` retains H16, population `64`, elites `8`,
iterations `4`, two-tick blocks, proposal variance `0.20/0.03`, exact-reference
proposal center, fitted bridge, rate clipping, command x=`0.074`, duration
`1.08 s`, and seeds `100/101`.

Only candidate ranking changes. It is lexicographic:

1. require predicted no-fall, absolute roll/pitch no greater than `0.25 rad`,
   minimum height at least `0.12 m`, and max action below `0.999`;
2. when no candidate is feasible, minimize the worst normalized violation;
3. among feasible candidates, minimize body-local x velocity RMSE to the
   command;
4. break ties by body-local lateral velocity RMSE, relative yaw, reference
   residual, then action delta.

The `0.25 rad` tilt and `0.12 m` height values are reused from the repository's
existing candidate gate, not selected from this probe's outcomes. No scalar
reward weights are introduced.

## Frozen advancement rule

Both seeds must complete and satisfy all of:

- mean body-local x velocity from `0.25x` through `1.35x` command;
- bilateral contact transitions;
- max absolute roll and pitch no greater than `0.25 rad`;
- minimum height at least `0.12 m`;
- max action strictly below `0.999`;
- zero measured action-rate excess.

Anything below 2/2 closes this source formulation. No parameter retry follows.
A pass authorizes only a collection-design decision, not training.

Local CPU only. No Colab, GPU, RDK-X5, robot, torque, or motor access is
authorized.
