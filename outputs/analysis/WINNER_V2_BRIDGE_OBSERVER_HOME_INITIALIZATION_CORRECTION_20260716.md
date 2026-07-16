# Winner v2 Bridge-Observer Home Initialization Correction

Status: `PREREGISTERED_IMPLEMENTATION_CORRECTION`

The first formal replay reconstructed the configured home vector by inverting
float32 trace values (`sent - 0.25*action`). That inverse is not bit-exact across
commands: maximum disagreement is 3.725290298461914e-9 rad. The observer itself
reproduced all 9,600 recorded applied targets with zero error when initialized
from each inverse-recovered vector.

This correction replaces only inverse-derived initialization with the
authoritative `home_target_rad` already frozen in
`ground_up_actual_centered_guard_screen_preregistration.json`, converted once to
float32 exactly as in the simulator. The inverse-recovered vectors remain an
audit and must lie within 5e-9 rad of the authoritative vector. The 16 traces,
9,600 rows, fits, transition formula, 0.02 s timestep and 1e-12-rad applied-
target tolerance do not change.

A pass authorizes only the same offline v2 semantics conclusion. It does not
authorize runtime integration, hardware-fit selection, Gate 5, RDK-X5, robot
access or deployment.

