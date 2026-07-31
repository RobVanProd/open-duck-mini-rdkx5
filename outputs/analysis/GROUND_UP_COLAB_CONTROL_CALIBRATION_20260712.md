# Ground-Up Colab Control Calibration

status: `HOLD_CANONICAL_T4_NO_CHECKPOINT_WITHIN_CAP`

One self-cleaning T4 calibration was run against pinned upstream commit
`b9be205ac64488c23504ca42e5ec790337adeec3` with the frozen dependency
contract. The session was created at `22:46:47 UTC`, terminated at
`23:07:33 UTC`, and `colab sessions` confirms no active session remains.

- total session wall time: `20 min 46 s`
- requested training steps: `1,000,000`
- training timeout: `900 s`
- result: timeout before any checkpoint/ONNX result was returned
- exact compute units: not exposed by the installed Colab CLI
- conservative project ledger charge: full calibration allowance, `3 units`

The accelerator contract completed far enough to enter the training subprocess;
the failure occurred inside canonical training. Inspection of the canonical PPO
configuration identifies `8,192` parallel environments, network
`512/256/128`, 32 minibatches, and 15 evaluations. This configuration is not a
usable T4 search calibration under the frozen time cap.

Do not repeat the same run or extend its timeout. The next CPU work is an
explicitly hashed control patch that exposes PPO scale parameters while leaving
the environment, reference, rewards, observations, actions, and dynamics
unchanged. A smaller T4 calibration must account against the search allocation,
not reopen the spent calibration category.

No robot, local GPU, deployment, or hardware action occurred.
