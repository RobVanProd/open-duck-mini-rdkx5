# Winner-v3 Recurrent-Adapter Normalizer Expansion Correction — 2026-07-19

After the committed CPU topology correction, the contract restored and saved
the expanded checkpoint, completed step-zero evaluation, and saved the
step-zero export. It stopped inside the first PPO training epoch before the
first optimizer update. Brax requires the running-statistics tree to match the
complete rollout observation tree; the expansion added recurrent actor
parameters but omitted the new `policy_hidden[64]` running-statistics leaf.
No step-1024 checkpoint, trained ONNX, contract JSON, or candidate behavior
decision was produced.

Freeze the same established neutral-statistics expansion used by prior
observation additions:

- `mean.policy_hidden = zeros[64]`;
- `std.policy_hidden = ones[64]`;
- `summed_variance.policy_hidden = full[64](8048640.0)`, matching the protected
  source count;
- source count and every existing state/privileged statistic remain exact.

This changes neither step-zero normalized state features nor the protected
actor output; the policy network normalizes only `state`, while the complete
statistics tree now matches the recurrent rollout observation. No architecture,
parameter seed, PPO setting, reward, threshold, domain, command, or decision
rule changes. This correction authorizes only rerunning the still-incomplete
CPU contract. It authorizes no candidate curriculum, GPU/iGPU, hosted/Colab,
RDK-X5, runtime, robot, torque, motion, Gate 5, deployment, or clearance.
