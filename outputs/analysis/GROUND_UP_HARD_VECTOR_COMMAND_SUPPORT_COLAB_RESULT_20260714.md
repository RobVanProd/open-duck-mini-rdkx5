# Ground-Up Hard-Vector Command-Support Colab Result

status: `PASS_TRAINING_ARTIFACT_CONTRACT_ONLY`

The one preregistered A1 continuation completed on one Colab T4 and produced
exactly the frozen export steps:

| continuation step | ONNX SHA-256 |
|---:|---|
| 0 | `67c0984ff13d8c24e2094fb2c757d32dc567ea13d57091effca8b7ff04d77f49` |
| 1,003,520 | `f583377fef75e90f93380b9f4bf971f664f484629193a0e58ae6f466c3bad2be` |
| 2,007,040 | `1af12814b8f92f4c367b1af3e248dc77aae7cd7a5b89c7d2daa8d604f73c82b3` |

The step-zero ONNX hash exactly matches the local CPU restore smoke. This is an
independent artifact-level confirmation that the protected A1 4M checkpoint was
restored before continuation.

## Execution contract

- versions: JAX/JAXlib `0.8.2`, MuJoCo `3.9.0`, Playground `0.0.5`;
- device: one JAX CUDA T4;
- requested continuation: 2,000,000 steps;
- actual rounded exports: 1,003,520 and 2,007,040;
- training time: `859.8518 s`;
- total hosted job time: `909.5039 s`;
- recovered archive SHA-256:
  `cfc895aca4ddf4ffb0eabf0ca338cd7dd03b19cc7d32125c53ad7ce36bb9ab83`;
- recovered archive size: `8,161,171` bytes;
- all three checkpoints, all three ONNX files, the training log, event file,
  job metadata, and manifest were recovered before shutdown;
- Colab reported zero active sessions after shutdown.

Every input patch/source/table/archive hash was checked remotely before the job
ran. Training reward is excluded from selection. This result proves only the
training artifact contract; behavior remains unevaluated until the frozen local
CPU home-reset sweep at x=`0.074/0.077/0.080`, seeds `100/101` completes.

No local GPU, iGPU, onboard GPU, RDK-X5, robot, torque, or motor access occurred.
There is no offline winner or robot clearance from this result.
