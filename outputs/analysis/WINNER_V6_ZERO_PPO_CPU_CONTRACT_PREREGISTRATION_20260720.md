# Winner-v6 Zero-PPO CPU Contract Preregistration

Status: `PREREGISTERED_NOT_RUN`

JSON SHA-256: `516243c1bf1a59b458686c735686b1f6839d298455e42013c73b6d39ed34db13`

This freezes one CPU-only, zero-training contract run. It uses the actual persistent G1/T2 half and final repaired ONNX checkpoints, requires bit-exact default-off action/state identity, then checks the 250-tick calibrator and handoff against a JAX reference at `1e-7`. It also proves invalid calibration cannot return an armable context.

A pass authorizes only a separate calibrator-training preregistration. No PPO step, Colab, GPU, runtime implementation, robot access, torque, motion, Gate 5, deployment, or robot clearance is authorized here.
