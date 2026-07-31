# Ground-Up Reset-Estimator Action-Distribution ULP Restore Correction — 2026-07-15

The first audit invocation stopped before actor restoration, perturbation
construction, or outcome computation because raw Orbax restore attempted to
resolve the protected checkpoint's recorded `cuda:0` sharding on the CPU-only
host. It produced no audit JSON and no numerical sensitivity result.

Freeze the established topology-remap method already used by this project:

- restore the verified CPU template at
  `/home/lsd/robots/open-duck-mini-rdkx5/outputs/ground_up_torso_com_cpu_smoke/2026_07_14_180720_0`,
  directory SHA-256
  `b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a`;
- derive CPU restore arguments from that target tree with
  `flax.training.orbax_utils.restore_args_from_target`;
- restore the exact archive-extracted protected checkpoint into that template;
- require identical tree structure, exact expected source shapes, finite CPU
  leaves, and the archive-extracted source-directory hash
  `05c0c08468f02b96d7e4316fdae6527c6ee223fba507ce3f6a3221b2561a920e`.

No perturbation, threshold, input observation, distribution calculation, or
decision rule changes. This correction authorizes only rerunning the already-
preregistered CPU audit. It authorizes no GPU, Colab, training, behavior,
RDK-X5, runtime, or robot action.

