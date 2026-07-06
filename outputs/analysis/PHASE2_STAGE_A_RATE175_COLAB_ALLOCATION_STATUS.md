# Phase 2 Stage A Rate175 Colab Allocation Status

status: `HOLD_COLAB_GPU_ALLOCATION`
generated_at: `2026-07-06T09:28:00Z`

Offline only. No robot, SSH, deploy, grounded replay, runtime behavior change, or training job was started.

## Context

The valid Phase 2 Stage A GPU job is ready to run from the true Phase 1 rate175 trainable checkpoint:

- restore checkpoint: `outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- behavior prior MLP: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- task: `flat_terrain_backlash`
- pushes: `disabled`
- corrected actuator bridge: `enabled`

The corrected CPU wiring smoke passed separately, but is not promotable. A GPU Stage A run is still required before checkpoint sweep or Stage B/C decisions.

## Allocation Attempts

| session | request | result |
|---|---|---|
| `open-duck-t4-stagea` | `colab new -s open-duck-t4-stagea --gpu T4` | `HOLD_SERVICE_UNAVAILABLE` |
| `open-duck-l4-stagea` | `colab new -s open-duck-l4-stagea --gpu L4` | `HOLD_ACCELERATOR_REJECTED` |
| `open-duck-a100-stagea` | `colab new -s open-duck-a100-stagea --gpu A100` | `HOLD_ACCELERATOR_REJECTED` |

T4 error excerpt:

```text
ColabRequestError: Failed to issue request POST ... accelerator=T4: Service Unavailable
```

L4/A100 error excerpt:

```text
[colab] Backend rejected accelerator 'L4'. You may not have quota or entitlement for this accelerator on your account.
[colab] Backend rejected accelerator 'A100'. You may not have quota or entitlement for this accelerator on your account.
```

## Decision

`HOLD_COLAB_GPU_ALLOCATION`

The valid Stage A GPU run has not started. Retry T4 later with the already validated workflow. Do not substitute the local CPU smoke for a Phase 2 gate.

Next command when T4 allocation succeeds:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-t4-stagea \
  --workflow phase2-stage-a-narrow \
  --run \
  --skip-audit \
  --exec-remote \
  --exec-remote-timeout-s 14400 \
  --phase2-skip-post-training-gates \
  --remote-artifact-interval-s 0 \
  --candidate-behavior-prior-mlp-npz outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz \
  --candidate-behavior-prior-scale -0.6 \
  --candidate-behavior-prior-huber-delta 0.05 \
  --phase2-final-training-args-json '["--restore-policy-kl-scale","4.0"]' \
  --output-root outputs/analysis/colab_cli_stage_a_rate175_prior
```
