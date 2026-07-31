# Phase 2 B0E A100 Corrected-Task Hold

status: `HOLD_B0E_A100_TRACKING_REGRESSION`

## Purpose

Run the corrected Phase 2 `b0e` workflow on the `open-duck-a100` CUDA session
after fixing the terrain task mismatch. This was an offline-only robustness
training run from the existing Phase 2 terrain candidate with corrected actuator
bridge, mild domain randomization, mild pushes, observation noise, and rough
terrain `z=0.002`.

No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or policy
overwrite were performed.

## Run

```text
session: open-duck-a100
hardware: A100
jax/jaxlib: 0.7.2 / 0.7.2
brax: 0.14.2
mujoco/mujoco-mjx: 3.9.0 / 3.9.0
backend/device: gpu / cuda:0
task: rough_terrain_backlash
num_timesteps: 160000
ppo_num_envs: 128
ppo_num_evals: 4
episode_length: 750
elapsed_s: 716.064
```

The training process returned `0` and produced three ONNX exports:

| step | sha256 |
|---:|---|
| 81920 | `3cd7a83b10ec843a02483b5931ff492b2dd7ee0301f20d0ee37acc2e135660ad` |
| 163840 | `9c5f115bca70bb5516beffcd222b1be3cd6483b9f90e999be010ee4ba15ca359` |
| 245760 | `3ed9ec4550071632284ad86ea6a1c3ce4ff1500243ae4e0eeb9cabe4e57a5eee` |

The remote driver became idle without writing its exit sentinel during the
checkpoint sweep. A manual salvage bundle was created and downloaded:

```text
local bundle:
  outputs/analysis/colab_cli/open-duck-a100-phase2-b0e-20260629T092705Z/open_duck_colab_cli_phase2-b0e_20260629T092941Z_manual_salvage.tar.gz
sha256:
  e683711390fa0997ee3a77970e342981b27c4981d7b7316244eaed2b9f3272c4
```

## Gate Triage

The remote sweep completed the first checkpoint at `x=0.0` and `x=0.08`.
The local CPU sweep completed the missing one-second triage gates for the later
two checkpoints using the same corrected bridge and candidate gate.

| step | x command | status | track ratio | pitch tracking p95 | sent vel p95 | velocity excess | body pitch p95 | base height min |
|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 81920 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.1943 | 1.2312 | 0.0000 | 0.0326 | 0.1536 |
| 81920 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 0.3493 | 0.2208 | 1.5536 | 0.0000 | 0.0575 | 0.1536 |
| 163840 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.1946 | 1.2272 | 0.0000 | 0.0312 | 0.1536 |
| 163840 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 0.3402 | 0.2209 | 1.5695 | 0.0000 | 0.0553 | 0.1536 |
| 245760 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.1948 | 1.2334 | 0.0000 | 0.0310 | 0.1536 |
| 245760 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 0.3117 | 0.2208 | 1.5582 | 0.0000 | 0.0533 | 0.1536 |

## Decision

Do not promote B0E.

B0E is stable and in-envelope in the short gate, but it regresses the moving
`x=0.08` corrected-bridge tracking margin to a repeatable `~0.221 rad`, above
the `0.20 rad` threshold, and later checkpoints reduce forward command tracking
rather than recover it.

The next run should not continue longer from B0E. The useful baseline remains
the previous B0C terrain candidate; the next robustness attempt should apply a
smaller, more conservative perturbation adaptation from B0C with stronger
behavior preservation, or run eval-only perturbation diagnostics to isolate the
specific push/terrain events that break B0C.
