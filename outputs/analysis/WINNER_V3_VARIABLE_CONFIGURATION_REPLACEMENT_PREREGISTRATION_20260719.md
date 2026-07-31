# Winner-v3 Variable-Configuration Replacement Preregistration — 2026-07-19

Status: `PREREGISTERED_CPU_CONTRACT_FIRST`

## Frozen decision

The current `99d3afce…304de` graph is held by its already-hashed X-COM failure
bracket and is not rerun. The single prospective replacement is
`R64_ZERO_INIT_RECURRENT_ADAPTER`: a 64-state deployable recurrent adapter on
the protected T2_EQUAL 512,000 checkpoint. Its action head begins at exact
zero, so step-zero deterministic actions equal the protected base while the
hidden state can evolve. The protected actor, adapter, and unchanged privileged
critic may then train together. There is no oracle or true configuration input.

The choice is causal, not a search: memoryless exposure, the reset latch, and
frozen-base oracle correction have already failed, while a zero-head adapter
tests whether deployable history plus base-policy adaptation can use the
time-varying signal without discarding the verified gait at initialization.

## Frozen domain and training

Training is CPU only, seed 100, one process, no retry. It restores the protected
T2_EQUAL archive `ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f` and preserves the PPO recipe and
training reward. Domain deviations run at 25% for 245,760 steps, 50% for
245,760, then the full domain for 2,007,040 steps. Formal checkpoints are
1,003,520 and 2,007,040 steps into the full-domain stage. No training reward is
used for selection.

The full stage samples the basis' independent ±0.05 m torso COM axes,
0.5286734–0.8683786 kg resulting torso mass, full positive-definite and
triangle-valid inertia tensors, passed friction/frictionloss/armature ranges,
both measured actuator configurations, declared sensor noise, native
quantization, and zero-to-two-tick additional action/IMU delay.

## Frozen evaluation

Exactly 1,024 CPU cells are frozen: 32 nominal; 384 over 24 fixed aggregate
anchors; 256 over 16 discovery coupled samples; 256 over a separately seeded
16-sample heldout set; and 96 native-quantization/noise/delay cells. Every set
crosses both full-domain checkpoints, both actuator plants, and commands
`0/.074/.077/.080`; every cell is 600 ticks with exact per-run readback.

The existing gates remain unchanged. Moving commands require complete duration,
bilateral transitions, positive command-consistent motion, the candidate gate,
tracking p95 <=.20 rad, and zero saturation/rate/envelope excess. At x=0,
absolute mean local vx must be <=.02 m/s, pitch p95 <=.25 rad, base height
>=.12 m, and the same tracking/safety limits. All-joint current p95 must also be
<=.65 A, derived from simulated torque using the STS3215 8 kg.cm/A constant.

Both checkpoints must pass all 1,024 cells. There is no closest-policy
promotion and no post-outcome change. A pass only permits the ordered policy
asset/clearance/envelope commits and a new two-repository runtime freeze; it is
not X5 execution, robot use, motion, Gate 5, or deployment clearance.

## Authority

This preregistration authorizes the CPU implementation contract, and only after
that contract passes, the single CPU training process and frozen CPU evaluation.
It authorizes no Colab/hosted allocation, GPU/iGPU, RDK-X5, robot, serial,
GPIO/I2C, torque, motion, runtime execution, Gate 5, or deployment.
