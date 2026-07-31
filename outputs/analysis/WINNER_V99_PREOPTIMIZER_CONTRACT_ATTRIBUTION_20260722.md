# Winner-v99 pre-optimizer checker-contract attribution

Status: `HOLD_WINNER_V99_PREOPTIMIZER_CHECKER_CONTRACT`

The automatic 250-tick calibration and 250-tick home return completed, but PPO never started. The three failures are checker/serialization contract errors: container type identity, a tanh representation at exact saturation, and an invalid final-rate assertion after the graph's actual-centered guard. No threshold, behavior gate, actor math, or training setting is changed.
