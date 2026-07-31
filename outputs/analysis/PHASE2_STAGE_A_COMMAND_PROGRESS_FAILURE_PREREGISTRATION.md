# Stage A Command-Progress Failure Preregistration

Date: 2026-07-11

Status: **COMPLETED; NO CHECKPOINT PASSED BOTH COMPACT GATES; BRANCH CLOSED**

Replay the original authoritative prior-enabled Stage A recipe from the same
rate175 step-0 checkpoint with one change only:

- enable positive-command progress-failure termination;
- minimum progress ratio: `0.25`;
- warmup: `30` control ticks (`0.60 s`).

Preserve behavior prior `-0.6`, restore KL `4.0`, requested timesteps 163,840,
PPO settings, all reward scales, reset distribution, bridge, noise, domain
randomization, and push-disabled setting. The termination has no effect for
zero commands.

Apply the same staged gates as the no-prior experiment: all emitted checkpoints
must first run compact x=0 and x=0.08 corrected-bridge gates. If none passes
both, stop. If multiple pass, select highest x=0.08 velocity, then lower
tracking p95, then earlier step. Only a selected compact-pass checkpoint may
run seeds 40-71.

Final expanded pass rule remains: falls <=5/32, passes >=4/32, mean velocity
>=-0.0185 m/s, no pitch-chain velocity violation, and x=0 compact pass.

Failure closes this exact termination setting without threshold/warmup tuning.
Colab CUDA only; no local GPU, robot, or deployment.
