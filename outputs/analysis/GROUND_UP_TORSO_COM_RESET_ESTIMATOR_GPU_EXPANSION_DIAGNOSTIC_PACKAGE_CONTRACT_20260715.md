# Ground-Up Torso-COM Reset-Estimator GPU Expansion Diagnostic Package Contract — 2026-07-15

## Result

`PASS_RESET_COM_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_PACKAGE_CONTRACT`

All frozen package checks pass with zero Colab sessions, remote bytes, training
processes, or PPO steps. The package contains exactly the prior 19 assets, the
hash-locked hosted source, and one diagnostic wrapper.

Deterministic pass and fail fixtures both prove that the wrapper copies and
hashes the original expansion report, emits one marker, and terminates before
the training boundary. The three frozen result classes pass their controls.
The short launcher preserves named T4 cleanup and atomic recovery while
enforcing 300 seconds, .25 compute units, a 60-second stop reserve, and a
60-second live rate handshake.

Hashes:

- launcher: `655e3d34d86bd8f28cd147342f84230ba71eb1426e9ff90b4aa706d58fa7312b`
- wrapper: `68a6f8c3001bfdce74346a02533ca76e9e122d0a5ea325c827625e6293fe14e4`
- contract JSON: `231458e681c36b717c34ce653cd73b4b94da32d5c491242a499dc75bf7765e27`

## Authority

This contract authorizes no allocation. One new explicit approval is required
for the short T4 diagnostic. After allocation, the operator need provide only
the live UI rate and available-unit values. The diagnostic cannot start PPO or
select a policy. No behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or
robot action is authorized.
