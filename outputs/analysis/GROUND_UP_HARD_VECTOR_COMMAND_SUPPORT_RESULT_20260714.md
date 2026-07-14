# Ground-Up Hard-Vector Command-Support Result

status: `REJECT_NO_PERSISTENT_CANDIDATE_GATE_PASS`

## Frozen decision

The continuation solves the command-support and target-rate problems but fails
the unchanged fitted actuator-tracking gate at both post-update checkpoints.
The preregistered route therefore closes without tuning.

Both seeds are identical under the intended deterministic home reset and were
still executed and recorded separately. Every one of the 12 post-update runs
completed 1.08 seconds, moved body-forward, retained bilateral contact
transitions, and had zero p95/max target-rate excess.

| checkpoint | x | mean vx m/s | command ratio | pitch tracking p95 rad | saturation | candidate gate |
|---:|---:|---:|---:|---:|---:|---|
| 1,003,520 | .074 | .07467 | 1.0090 | .22243 | 0% | hold tracking |
| 1,003,520 | .077 | .09291 | 1.2067 | .21449 | 0% | hold tracking |
| 1,003,520 | .080 | .09769 | 1.2211 | .21235 | 0% | hold tracking |
| 2,007,040 | .074 | .06841 | .9244 | .21897 | 0% | hold tracking |
| 2,007,040 | .077 | .09068 | 1.1777 | .22539 | 0% | hold tracking |
| 2,007,040 | .080 | .09746 | 1.2182 | .23868 | 1.8519% | hold saturation |

The fixed candidate thresholds remain pitch-chain tracking p95 `<=0.20 rad`
and action saturation `<=1%`. Neither checkpoint passes all commands, and the
preregistered rule required both checkpoints to pass. There is no rounding or
single-checkpoint promotion.

## Control and mechanism

The step-zero stateful ONNX exactly matches the CPU-smoke hash and reproduces
the earlier hard-vector survival result: both x=.074 seeds walk at `.05363 m/s`
with zero saturation/rate excess. Its tracking p95 is `.20205 rad`, confirming
the evaluator/state feedback while retaining the original narrow hold.

The new continuation changes the previous failure mode materially:

- fixed-command normalization collapse is gone;
- x=.074/.077/.080 all produce command-consistent gait;
- the 14-joint hard vector is obeyed throughout;
- locomotion does not collapse to standing, unlike the earlier penalty-only
  constrained PPO route;
- fitted actuator tracking does not improve below the frozen limit and trends
  worse by 2M.

The remaining digital mismatch is structural: this training environment
enforces target slew but does not expose the fitted per-joint delay/tau actuator
transition used by the candidate gate. The next evidence task is a read-only
integration audit of the already validated measured actuator bridge against the
ground-up stack. It may determine whether one separately preregistered causal
arm is technically coherent; it does not authorize another training run.

## Authority boundary

Training reward was not used. No x=0, randomization, delay/noise curriculum,
pushes, terrain, `BEST_WALK_ONNX_2` comparison, RDK-X5 work, deployment, or
robot test is authorized. No local GPU, iGPU, onboard GPU, RDK-X5, robot,
torque, or motor access occurred.

There is still no offline winner and no robot clearance.
