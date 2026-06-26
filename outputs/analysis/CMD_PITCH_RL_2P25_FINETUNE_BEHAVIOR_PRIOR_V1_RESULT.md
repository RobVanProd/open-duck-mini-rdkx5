# Command Pitch RL 2.25 Behavior-Prior Fine-Tune V1

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

This run tested whether a state-conditioned teacher-action behavior prior could
preserve the x=0.08 walking behavior during PPO fine-tuning from the current
step-0 warm start.

## Inputs

- warm start checkpoint: `outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint`
- behavior prior: `outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate_mlp.npz`
- recovered ONNX: `outputs/analysis/cmd_pitch_rl_2p25_finetune_behavior_prior_v1/candidate_92160.onnx`
- ONNX sha256: `3165738b2a8ba991714c0117ff1276acd9ce724944b3dd981fd578405fa469b8`

## Training

Training completed on the A100 Colab/CUDA path:

```text
status: PASS_SMOKE_RUN
timesteps exported: 92160
restore checkpoint: ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
behavior prior scale: -0.2
behavior prior huber delta: 0.05
learning rate: 3e-5
clipping epsilon: 0.05
max grad norm: 0.2
ppo updates per batch: 1
target rate scale: -0.0005
actuator tracking scale: -0.005
```

The Colab workflow disappeared during the post-training x=0 gate before writing
its normal exit sentinel. The training artifact tarball was still readable, so
the final ONNX and training summary were recovered. The candidate gates below
were rerun locally on CPU with `JAX_PLATFORMS=cpu`.

## Gate Results

### x=0.0

```text
gate: PASS_CANDIDATE_SIM_GATE
duration: 15 s / 750 samples
max pitch tracking p95: 0.0618 rad
max sent target velocity p95: 0.2775 rad/s
max abs body pitch p95: 0.0235 rad
min base height: 0.1536 m
action saturation: 0.0%
```

The candidate preserves a clean zero-command stand.

### x=0.08

```text
gate: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
duration: 15 s / 750 samples
fitted mean local vx: 0.0001 m/s
fitted command tracking ratio: 0.0015
stress command tracking ratio: 0.0029
max sent target velocity p95: 0.4586 rad/s
max pitch tracking p95: 0.0772 rad
max abs body pitch p95: 0.0103 rad
min base height: 0.1536 m
action saturation: 0.0%
```

The behavior-prior fine-tune is stable and actuator-safe, but it erased the
forward gait. It performs worse on x=0.08 forward progress than the previous
conservative preservation run, whose fitted command tracking ratio was `0.0045`.

## Interpretation

The state-conditioned behavior prior, as implemented here, was not sufficient
to preserve the warm-start walking behavior during PPO. PPO again improved
stability and tracking by collapsing the forward command into low-rate
standstill.

This rules out a weak version of the "just add a teacher-action regularizer"
hypothesis. The remaining issue is not basic x=0 stability, target-rate margin,
or a too-large PPO step. The deployable network still needs a training method
that preserves the closed-loop walking mechanism while optimizing fitted-bridge
tracking.

The next offline branch should not be another scalar PPO sweep. It should use
the working selector/teacher behavior to generate broader on-distribution
rollouts, then either:

```text
1. BC-pretrain on that expanded selector dataset and PPO fine-tune from the
   resulting walking network, or
2. add a stronger, better-matched behavior objective that anchors the actual
   walking manifold rather than the weak MLP prior used here.
```

No robot test, SSH, deployment, runtime behavior change, or policy overwrite was
performed.
