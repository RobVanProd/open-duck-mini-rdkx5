# Ground-Up Nominal Horizon Gate Amendment

status: `PREREGISTERED_BEFORE_FUTURE_COMPUTE`

## Evidence requiring the amendment

The prior nominal screen used 54 ticks (1.08 seconds), while the nominal PPO
episode is 600 ticks (12 seconds). The applied-target 1M checkpoint passed all
three commands during the first 54 ticks, then crossed the unchanged 0.20 rad
pitch-chain tracking limit by cumulative tick 108 at x=.074/.080 and tick 162
at x=.077. Its 600-tick p95 is .21334-.22317 rad.

The 2M checkpoint fails at tick 54 and remains over the limit at 600 ticks.
Both checkpoints remain finite, upright, and walking for the complete horizon,
so the result is not caused by a fall or truncated trace.

`BEST_WALK_ONNX_2` also fails the 600-tick hardware-oriented gate: tracking is
.21293-.22331 rad, forward velocity is only .01443-.01749 m/s, and measured
pitch-chain rate-limit excess is 3.61-3.87 rad/s. The ground-up checkpoints
move at .09293-.11069 m/s with zero rate excess, but they are not winners
because their full-horizon tracking still fails.

## Prospective rule

For every future nominal candidate checkpoint:

1. Evaluate x=.074/.077/.080 for the complete 600-tick nominal episode on the
   frozen deterministic home-reset seeds.
2. Apply the existing finite, duration, gait, bilateral-support, saturation,
   measured-rate, posture, progress, and 0.20 rad worst pitch-chain p95 gates
   over the complete 600 ticks.
3. A 54-tick result is a startup diagnostic only and cannot advance a policy.
4. Checkpoint-to-checkpoint persistence is evaluated only after each involved
   checkpoint independently passes the complete 600-tick gate.
5. x=0, randomization, pushes, terrain, RDK runtime, and robot work remain
   blocked until the full-horizon nominal gate persists.

This amendment is prospective. It does not retroactively select a checkpoint,
weaken a threshold, or authorize training. The source evidence is
`GROUND_UP_NOMINAL_HORIZON_PERSISTENCE_AUDIT_20260714.md` and its JSON/raw
trace artifacts.

No Colab, GPU, RDK-X5, robot, motor, or torque access is authorized here.
