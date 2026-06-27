# PPO Behavior-Prior Plumbing Tiny CPU Smoke

status: `PASS_BEHAVIOR_PRIOR_RESTORE_PLUMBING`

## Summary

A tiny CPU training smoke verified that the RDK wrapper can restore the current
PPO warm-start checkpoint and pass the command-conditioned DAgger MLP as a
default-off Playground behavior prior.

This was a plumbing check only. It is not a candidate training result and did
not produce a deployable policy.

## Command Shape

```text
restore checkpoint:
  outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0_checkpoint

behavior prior:
  outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate_mlp.npz

behavior prior scale:
  -0.05

behavior prior huber delta:
  0.05

actuator bridge:
  enabled, fitted/stress-style randomized range

num timesteps:
  16
```

## Result

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed: 59.24 s
saved checkpoint: step 40
robot touched: false
deploy performed: false
```

The wrapper resolved both relative paths correctly:

```text
restore_checkpoint_path:
  /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0_checkpoint

behavior_prior_mlp_npz:
  /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate_mlp.npz
```

## Interpretation

The next GPU experiment can use a behavior-prior/trust-region term to keep PPO
near the DAgger policy. This directly addresses the failed A100 PPO-only run,
where reward increased while the exported ONNX regressed into standstill and
hard-seed instability.

This does not prove the behavior-prior recipe works. It only proves the
restore + behavior-prior training path is executable.
