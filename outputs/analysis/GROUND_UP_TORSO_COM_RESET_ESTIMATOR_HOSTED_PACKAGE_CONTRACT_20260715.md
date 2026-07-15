# Ground-Up Torso-COM Reset-Estimator Hosted Package Contract

status: `PASS_RESET_COM_ESTIMATOR_HOSTED_PACKAGE_CONTRACT`

The single-arm hosted package passes all 17 frozen CPU checks. This result
executed zero training steps and opened zero Colab sessions.

## Contracted job

- Arm: `RESET_EST_LATCH_U05` only.
- One uninterrupted 2,000,000-step continuation from the protected T2 source.
- Expected actual exports: 0, 1,003,520, and 2,007,040.
- One session, one training process, no resume, no retry.
- Wall ceiling: 2,400 seconds.
- Compute ceiling: 2.0 Colab compute units.
- Behavior status after hosted completion: `UNEVALUATED`.
- Training reward used for selection: false.

All seed, optimizer, command, bridge, randomizer, estimator, observation,
velocity-envelope, episode, and export values match the frozen
preregistration. Asset-only validation passes every exact hash and finds the
protected raw checkpoint member in the source archive.

## Hosted-topology expansion equivalence

The exact expansion function intended to run after CUDA verification was
executed here on CPU against the protected CPU-remapped source:

- source shapes: 115-D state, 226-D privileged, `(115,512)` actor first
  kernel, `(226,512)` critic first kernel;
- expanded shapes: 116-D state, 227-D privileged, `(116,512)` actor first
  kernel, `(227,512)` critic first kernel;
- inserted normalizer coordinate and zero rows: exact;
- every other value: bit-exact;
- save/restore: bit-exact;
- actor and critic output error at `z=-1,0,+1`: zero;
- final 14-D reference-action tail: exact.

This matches the previously passing local expansion contract. The hosted job
does not assume that the CPU Orbax directory is GPU-portable: it restores,
expands, saves, and verifies the protected raw checkpoint on the hosted CUDA
topology before PPO. Any topology or equality failure stops before training.

## Artifacts and failure handling

The job requires the hosted expansion report/checkpoint, all three Orbax and
ONNX exports, full training log, exact manifest, and an atomically replaced
compressed archive. Missing exports, timeout, expansion failure, or excess
budget fails the arm without resume or retry.

Contract JSON SHA-256:
`96144a54c880a18e83e459a83e0eed771b1bc9bb55c8f147e7efc725cf4fc9c4`.

## Execution and authority

The contract used CPU `TFRT_CPU_0`, zero dynamic behavior cells, zero training
steps, zero Colab sessions, no local GPU/iGPU, no RDK-X5, and no robot.

This passing package still does not authorize the hosted run. A separate
explicit hosted-run authorization is required. Behavior evaluation, graph
promotion, R2/R3, runtime work, deployment, RDK-X5, torque, motors, and robot
access remain unauthorized.
