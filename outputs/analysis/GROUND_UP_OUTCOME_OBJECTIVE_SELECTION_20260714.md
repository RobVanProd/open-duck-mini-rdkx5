# Ground-Up Outcome Objective Selection

status: `SELECT_SIGNED_COMMAND_PROGRESS_ONE_FACTOR`

The completed scalar, architecture, and nominal-reference bootstrap screens
all fail to produce persistent gait. The shared-setup audit explains why the
existing forward term is weakly discriminative: at positive commands,
stationary behavior receives a Gaussian tracking score of 0.852 at x=.04,
0.578 at x=.074, 0.527 at x=.08, and 0.237 at x=.12. The score is never
negative for reverse motion.

The next causal change is therefore the geometry of the forward term, not its
scale. For positive x commands, replace the Gaussian score with:

`clip(body_local_vx / abs(command_x), -1, 1)`

This directly uses the frozen behavior gate's command-normalized local forward
velocity. At reverse-command speed, standing, half speed, target speed, and
overspeed it yields `-1, 0, 0.5, 1, 1`. The existing reward scale remains
exactly `2.5`; x=0 retains the canonical Gaussian score. No threshold, warmup,
termination, scale, or extra reward is introduced.

Alternatives are not mixed into this test:

- command-progress termination has previously failed as an exact route and
  introduces a warmup and threshold;
- forward-shortfall costs require both a ratio and scale choice;
- increasing tracking scale would reopen the closed scalar-search problem;
- changing alive reward or reward clipping would be separate objective
  mechanisms.

The signed-progress implementation passes its CPU curve, one-step finite,
observation/action-dimension, default-off, and canonical-x=0 contracts. This
selection authorizes only a separately preregistered causal training arm.

No robot, RDK-X5, local GPU, iGPU, or onboard GPU access occurred.
