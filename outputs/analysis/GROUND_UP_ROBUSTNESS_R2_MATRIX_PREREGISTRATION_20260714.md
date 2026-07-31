# Ground-Up Robustness R2 Matrix Preregistration

status: `PREREGISTERED_CONTRACT_REQUIRED_CPU_ONLY`

R1 now passes both measured actuator fits. R2 isolates the dynamics ranges
already declared by the pinned repository rather than activating its coupled
randomizer. Twenty conditions are frozen in the original source order:

- floor friction, joint friction loss, and armature endpoints;
- six single-axis torso COM offsets at `±.05 m`;
- all-link mass scale and torso-added-mass endpoints;
- deterministic home joint-offset corners at `±.03 rad`;
- actuator KP endpoints.

Each condition contains both repaired checkpoints, both measured actuator
fits, commands `0/.074/.077/.080`, one hash-derived seed, and 600 ticks: 16
cells per condition, 320 maximum. Conditions run strictly in order and stop at
the first failed condition. This is deliberately not a smaller final-only or
single-fit screen.

Before behavior, the evaluator contract must prove one-axis-only mutation,
exact endpoint values, field/index readback, propagation of joint offsets into
the deterministic home-support reset, default-off reproduction, and CPU-only
execution. Passing the contract authorizes R2 behavior only. It does not
authorize R3+, training, Colab, local GPU, RDK-X5, or robot access.
