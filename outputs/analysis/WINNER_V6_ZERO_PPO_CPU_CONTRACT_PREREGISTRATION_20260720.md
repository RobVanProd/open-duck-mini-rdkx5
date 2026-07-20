# Winner-v6 Zero-PPO CPU Contract Preregistration

Status: `PREREGISTERED_NOT_RUN`

JSON SHA-256: `aa3b847fc80a30501afdaa10f5f332ff9426166e425763bc36a4ecc67db40544`

This freezes one CPU-only, zero-training contract run. It uses the actual persistent G1/T2 half and final repaired ONNX checkpoints, requires bit-exact default-off action/state identity, then checks the 250-tick calibrator and handoff against a JAX reference at `1e-7`. It also proves invalid calibration cannot return an armable context.

A pass authorizes only a separate calibrator-training preregistration. No PPO step, Colab, GPU, runtime implementation, robot access, torque, motion, Gate 5, deployment, or robot clearance is authorized here.
