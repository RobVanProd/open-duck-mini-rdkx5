# Phase 2 Stage A Rate175 Bounded-Continuity Result

Date: 2026-07-11

Status: **HOLD — branch closed; no promotion or further training**

This was an offline Colab T4 causal smoke. No robot, deployment, grounded
replay, local iGPU, or local onboard GPU was used. The Colab session was stopped
after artifact download and `colab sessions` reported no active sessions.

## Registered change

The run restored the original rate175 policy and froze the Stage A recipe except
for the pre-registered behavior teacher:

- pitch-chain joint weights: `0.25,0.5,1,2,2,0.25,0.25,0.25,0.25,0.25,0.5,1,2,2`
- temporal ceiling: `2.0 rad/s`
- limited joints: `2,3,4,11,12,13`
- requested `num_timesteps`: `40,960`

The trainer exported checkpoints at 40,960, 81,920, and 122,880 despite the
40,960 request. The installed Brax implementation explains the expansion:

```text
environment steps per PPO training step = batch_size * unroll_length * num_minibatches
                                        = 512 * 20 * 4
                                        = 40,960
post-initial epochs = num_evals - 1 = 3
training steps per epoch = max(ceil(40,960 / (3 * 40,960)), 1) = 1
actual steps = 3 * 1 * 40,960 = 122,880
```

Thus the run was not an exact 40,960-step causal smoke. All emitted checkpoints
are still reported below. A future exact 40,960-step run would require at most
two evaluations or a smaller rollout quantum, but no future run is authorized
by this result.

## Compact corrected-bridge evidence

Pre-registered x=0.08 acceptance thresholds were:

- tracking p95 `<= 0.20 rad`
- mean forward velocity `>= 0.0298 m/s`
- command tracking ratio `>= 0.3724`
- fitted velocity envelope respected and action saturation zero

| checkpoint | x=0 status | x=.08 status | x=.08 mean vx | x=.08 ratio | x=.08 tracking p95 | target-rate p95 | saturation |
|---:|---|---|---:|---:|---:|---:|---:|
| 40,960 | PASS | HOLD low progress | 0.00755 | 0.09439 | 0.20206 | 1.09449 | 0% |
| 81,920 | PASS | HOLD low progress | 0.01280 | 0.15999 | 0.21226 | 1.54228 | 0% |
| 122,880 | PASS | HOLD tracking | 0.02118 | 0.26476 | 0.21599 | 1.55164 | 0% |

The later checkpoints improved forward progress monotonically, but even the best
checkpoint missed the velocity floor by 0.00862 m/s, missed the ratio floor by
0.10764, and exceeded the tracking ceiling by 0.01599 rad. Improvement with
training step is not a pass and does not justify extrapolating beyond measured
data.

## Decision

The bounded teacher did not produce a checkpoint that met the registered causal
acceptance gate. Therefore:

1. Do not promote any checkpoint.
2. Do not run the 15-second eight-seed suite; its prerequisite compact gate
   failed.
3. Do not continue training this branch.
4. Diagnose the saved learner and closed-loop traces before proposing another
   hypothesis. Any new training must be separately pre-registered and
   authorized.

Primary machine-readable evidence:

- `outputs/analysis/colab_cli_stage_a_rate175_bounded_continuity/open-duck-t4-continuity-phase2-stage-a-narrow-20260711T151905Z/artifact/open_duck_colab_cli_phase2-stage-a-narrow_20260711T151930Z/phase2_stage_a_narrow_rate175_cuda_checkpoint_sweep/candidate_checkpoint_sweep.json`
- `outputs/analysis/colab_cli_stage_a_rate175_bounded_continuity/open-duck-t4-continuity-phase2-stage-a-narrow-20260711T151905Z/artifact/open_duck_colab_cli_phase2-stage-a-narrow_20260711T151930Z/phase2_stage_a_narrow_rate175_cuda_selected_checkpoint.json`
- `outputs/analysis/colab_cli_stage_a_rate175_bounded_continuity/open-duck-t4-continuity-phase2-stage-a-narrow-20260711T151905Z/artifact/open_duck_colab_cli_phase2-stage-a-narrow_20260711T151930Z/phase2_stage_a_narrow_rate175_cuda_training_run_summary.json`
