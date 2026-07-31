# Ground-Up Oracle Viability/Command Source Result

status: `NO_VIABILITY_COMMAND_SOURCE_WINNER`

| seed | duration | body dx | mean body vx | contacts L/R | max roll | max pitch | min height | max action | rate excess | result |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 100 | complete | +0.00875 m | +0.00810 m/s | 4 / 6 | 0.2002 | 0.2347 | 0.1517 m | 0.8152 | 0 | hold: below 0.25x command |
| 101 | fall at tick 37 | -0.08730 m | -0.11487 m/s | 1 / 1 | 0.8000 | 0.3079 | 0.1621 m | 0.8270 | 0 | hold: reverse/roll fall |

The preregistered arm passed zero of two source gates. Seed 100 remained inside
all viability, action, and rate bounds and ended near the requested instantaneous
velocity, but its full-window mean velocity was only `0.1095x` command. Seed 101
had no feasible sampled horizon at any controller tick: its lowest recorded
predicted viability violation was `0.6959`, it continued backward, and it rolled
through the fall threshold.

## Decision

This formulation is closed without a parameter retry. Making viability
lexicographically dominant removed the H16 propulsion exploit in seed 100, but
did not produce command-consistent gait and did not expose a recovery sequence
for seed 101. It is not a teacher, and it authorizes neither collection nor
training.

The remaining uncertainty is now narrower: the current two-tick leg-action CEM
proposal does not demonstrate a viable recovery sequence for seed 101. Before
any further source implementation, a read-only feasibility audit should compare
fixed home, exact-reference, and bounded direct-trajectory candidates from the
same reset. That audit must distinguish an infeasible reset/bridge contract from
insufficient proposal support. No numeric retry of this controller is allowed.

No Colab, GPU, RDK-X5, or robot access occurred.
