# Winner-v3 Recurrent-Adapter CPU Restore Correction — 2026-07-19

The first post-implementation contract invocation stopped before checkpoint
expansion, actor inference, PPO training, export, or candidate behavior. Raw
Orbax restore tried to resolve the protected archive's recorded `cuda:0`
sharding on a CPU-only JAX process and rejected the topology. It produced no
contract JSON and no policy outcome.

Freeze the established topology-remap method already used by this project:

- restore the verified CPU template at
  `/home/lsd/robots/open-duck-mini-rdkx5/outputs/ground_up_torso_com_cpu_smoke/2026_07_14_180720_0`,
  directory SHA-256
  `b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a`;
- derive restore arguments with
  `flax.training.orbax_utils.restore_args_from_target`;
- restore the archive-extracted protected T2_EQUAL 512K checkpoint into that
  CPU target tree;
- require identical tree structure, CPU-only leaves, exact expected
  115/226 observation shapes, and source-directory SHA-256
  `311ce59807ad872795dd95e4a30c626f11d3d80f1b3f78c5b2b997639da4d67e`.

No architecture, parameter initialization, observation, threshold, PPO
setting, training step, domain, command, or decision rule changes. This
correction authorizes only rerunning the still-unexecuted CPU contract. It
authorizes no GPU/iGPU, Colab/hosted allocation, candidate curriculum,
behavior evaluation, RDK-X5, runtime, robot, torque, motion, Gate 5,
deployment, or robot clearance.
