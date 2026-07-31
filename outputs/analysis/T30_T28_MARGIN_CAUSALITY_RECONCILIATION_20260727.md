# T30 T28 margin-causality reconciliation

status: `PASS_T30_MIXED_OUTCOME_RECONCILIATION`

decision: `CLOSE_T28_POSTHOC_MARGIN_TRANSFORM`

The preregistered binary rule omitted the observed mixed case. The unwrapped source walks all 600 ticks but fails the 0.98 margin; the wrapped policy removes that margin crossing but falls at tick 331. T28 is closed as a post-hoc repair, and the unwrapped source remains non-green.

This reporting reconciliation authorizes mechanism-contract review only. It does not authorize training, Gate 5, RDK-X5, robot, torque, or motion.
