# Ground-Up Actor-SWA Screen Preregistration

status: `PREREGISTERED_CPU_ONLY`

## Why this mechanism is next

The project evidence now rejects additional scalar reward tuning, the exact
squared tail objective, three smooth occupancy surrogates, and a stateful
pitch-rate screen as persistent solutions. The read-only drift audit measured
actor-only raw-action drift at `0.09495878 RMS`, 6.749 times the normalizer-only
effect, while hosted reward improved and the external gate regressed.

The two retained tail trajectories have identical ONNX graphs and initializer
interfaces, share an identical mature step-0 policy, and were trained with the
same constant learning rate. This makes cumulative actor-only averaging a
testable stabilization mechanism. The SWA paper reports that weight averaging
along an optimization trajectory can reach flatter solutions
([Izmailov et al., 2018](https://arxiv.org/abs/1803.05407)); applying that result
to this PPO trajectory is an inference, not evidence of success.

## Frozen transform

Only the eight actor weight/bias initializers are averaged:

- cumulative half = arithmetic mean of mature step 0 and half;
- cumulative final = arithmetic mean of mature step 0, half, and final.

Each transformed policy retains the current half/final checkpoint's own
`obs_mean`, `obs_std`, graph, constants, and state interface. Observation
statistics are never averaged. The frozen factorial has T2/T3 trajectories and
two rate variants: unchanged, and the already preregistered R3 multiplier
`0.919637027640626`. This produces exactly eight ONNX policies and 48 CPU
behavior cells.

## Frozen advancement

The same rate/tail combination must pass the unchanged six-cell, 600-tick gate
at both cumulative half and cumulative final checkpoints. Selection prefers
unchanged rate, then lower worst tracking p95, then higher minimum forward
velocity. Training reward cannot select a result. A nominal winner authorizes
only a separately preregistered x=0 preservation gate.

No training, Colab, local GPU, RDK-X5, robot, deployment, torque, or motor
access is authorized by this preregistration.
