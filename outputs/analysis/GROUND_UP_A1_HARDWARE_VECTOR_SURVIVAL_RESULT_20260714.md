# Ground-Up A1 Hardware-Vector Survival Result

status: `PASS_HARDWARE_VECTOR_GAIT_SURVIVAL`

| seed | duration | body dx | mean body vx | contacts L/R | saturation | rate excess | result |
|---:|---|---:|---:|---:|---:|---:|---|
| 100 | complete | +.05772 m | +.05345 m/s | 9 / 5 | 0% | 0 | pass |
| 101 | complete | +.05772 m | +.05345 m/s | 9 / 5 | 0% | 0 | pass |

The projected A1 4M behavior retains `0.7223x` command, bilateral transitions,
full duration, and finite nonsaturated actions while reducing both p95 and max
measured target-rate excess from `4.24 rad/s` to zero. The result passes the
preregistered 2/2 survival rule.

The broader candidate gate remains a narrow hold: pitch-chain tracking p95 is
`0.20246 rad` against `0.20 rad`. This is only `0.00246 rad` over the frozen
limit, but it is still a failure and is not rounded into a pass.

## Decision

The nominal reference-residual gait is transferable through the measured hard
action vector. This rejects the prior penalty-only conclusion that hardware
rate compliance necessarily collapses the gait: that earlier PPO route learned
to stand, while the hard projection preserves locomotion.

This wrapper is diagnostic evidence, not a deployable policy. The next training
recipe must incorporate the same hard vector inside the environment/policy
transition and train a nondegenerate command distribution containing x=`0.074`
and x=`0.08`. It must be CPU-smoked and ONNX-verified before any Colab job.

No training, Colab, GPU, RDK-X5, or robot access occurred.
