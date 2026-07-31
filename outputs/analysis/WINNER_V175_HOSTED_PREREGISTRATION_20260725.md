# Winner V175 hosted preregistration

- Status: `PREREGISTERED_WINNER_V175_HOSTED_CONTINUATION`
- Run budget: one 2,007,040-step hosted continuation, no retry or resume.
- Source: exact V121-half raw checkpoint.
- Actor: reward-only before cost, cost-only on violating batches, cost-tangent reward updates afterward; no actor Adam or dual.
- Required exports: 0, 1,003,520, 2,007,040.
- Both post-update checkpoints must pass all 16 nominal cells before the full robustness matrix.
- Robot, RDK-X5, Gate 5, and motion authority: absent.
