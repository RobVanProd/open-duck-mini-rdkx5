# Stage A No-Behavior-Prior Direct-Outcome Preregistration

Date: 2026-07-11

Status: **PRE-REGISTERED; NOT LAUNCHED**

## Single training change

Replay the authoritative `phase2-stage-a-narrow` Colab CUDA recipe from the
same rate175 step-0 checkpoint, changing only:

- behavior-prior loss: enabled at `-0.6` -> disabled

Keep restore KL `4.0`, requested timestep setting, PPO parameters, reward
scales, canonical `0.5-1.5` reset multiplier range, actuator bridge, noise,
domain randomization, and push disabled. Do not add teacher corrections,
diagnostic pseudo-labels, phase deltas, reset alignment, or new rewards.

## Staged gates

1. Train and preserve every emitted checkpoint. Because PPO rollout geometry
   can overshoot requested timesteps, use actual emitted step numbers.
2. Run the existing compact corrected-bridge x=0 and x=0.08 gates on each
   checkpoint. A checkpoint must pass both before expanded evaluation.
3. If multiple pass, choose the one with highest x=0.08 mean velocity; tie-break
   by lower pitch-chain tracking p95, then earlier step.
4. Evaluate only that selected checkpoint on CPU seeds 40-71, x=0.08, one
   second, canonical reset, corrected fitted bridge, existing 2.0 rad/s
   pitch-chain policy limiter, and full traces.

## Final pass rule

All are required relative to the saved baseline:

- falls <= 5/32, versus 11/32 baseline;
- candidate passes >= 4/32;
- mean velocity >= -0.0185 m/s, at least 0.01 m/s better than baseline -0.0285;
- no pitch-chain target-velocity limit violation;
- x=0 compact gate remains passed.

If no checkpoint passes both compact gates, stop without the 32-seed sweep. If
the expanded rule fails, close this no-prior branch without tuning KL, rewards,
timesteps, or adding another loss in the same experiment.

Colab CUDA is authorized only for this preregistered training job. Local iGPU
and onboard GPU use remain prohibited. No robot access or deployment is
authorized.
