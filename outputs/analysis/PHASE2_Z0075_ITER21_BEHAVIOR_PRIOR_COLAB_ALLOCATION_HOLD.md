# Phase 2 z=0.0075 Iter21 Behavior-Prior Colab Allocation Hold

status: `HOLD_COLAB_GPU_ALLOCATION_UNAVAILABLE`

Offline launch attempt only. No robot tests, SSH, deploy, grounded replay,
runtime behavior change, or local training was performed.

## Intended Run

- recipe: `outputs/analysis/PHASE2_Z0075_ITER21_BEHAVIOR_PRIOR_POST_PUSH_RECIPE.md`
- workflow: `phase2-b0g`
- session: `open-duck-phase2-a100`
- candidate_name: `phase2_z0075_iter21_behavior_prior_post_push_recovery`
- restore_checkpoint: `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint`
- behavior_prior_mlp_npz: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz`
- behavior_prior_sha256: `71f520712a10613d3e2304a33cbcd641f6bb59fb0d5c1dc3e34a5c8fe93569b2`

## Attempt Log

1. `python3 tools/run_colab_cli_cuda_workflow.py ... --run`
   - result: `HOLD_SESSION_MISSING`
   - evidence: `colab console -s open-duck-phase2-a100` returned `Session 'open-duck-phase2-a100' not found.`
2. `colab new -s open-duck-phase2-a100 --gpu A100`
   - result: `HOLD_ACCELERATOR_REJECTED`
   - evidence: backend rejected accelerator `A100`.
3. `colab new -s open-duck-phase2-a100 --gpu L4`
   - result: `HOLD_ACCELERATOR_REJECTED`
   - evidence: backend rejected accelerator `L4`.
4. `colab new -s open-duck-phase2-a100 --gpu T4`
   - result: `HOLD_COLAB_SERVICE_UNAVAILABLE`
   - evidence: Colab assignment POST returned `Service Unavailable`.

`colab sessions` then reported no active server sessions.

## Local Backend Check

ROCm was checked before considering local fallback:

- GPU0: `AMD Radeon RX 7900 XTX`, gfx1100, about `18%` busy and `12%` VRAM allocated.
- GPU1: integrated `AMD Radeon Graphics`, gfx1036, about `73%` busy and `95%` VRAM allocated.
- active unrelated process: `/home/lsd/robots/envs/lerobot-so101/bin/python train_dreamer.py ...`

Because local GPU resources were already active and this branch needs a clean
training/eval backend, no local ROCm Phase 2 training was launched.

## Decision

The behavior-prior post-push recipe is ready, committed, and synced, but the
training run did not start because no Colab GPU session could be allocated.

next_action: `retry the committed behavior-prior Colab recipe when a GPU session is available, or explicitly stop/finish the unrelated local GPU workload before using the local ROCm fallback`
