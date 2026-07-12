# Hardware-Vector Bridge Constrained PPO CPU Smoke

status: `PASS_CPU_SMOKE_COLAB_AUTHORIZED`

- JAX platform forced to CPU; `CUDA_VISIBLE_DEVICES` empty.
- Exact 14-element delay/tau/velocity state assertions passed.
- Per-joint excess cost was finite, zero at/below limits, and positive above.
- PPO warm start restored from the rate165 step-0 checkpoint.
- A training update completed and exported checkpoint plus ONNX at step `2048`.
- Exported ONNX: `2026_07_12_104932_2048.onnx` (`883946` bytes).
- CPU AOT loader reported host-feature warnings; execution and export completed.

This satisfies the preregistered smoke boundary and authorizes one
self-cleaning Colab T4 job with the exact frozen recipe. It does not authorize
robot access, deployment, grounded replay, local GPU use, or gate weakening.

