# Winner V171 actor-gradient geometry preregistration

- Status: `PREREGISTERED_WINNER_V171_GRADIENT_GEOMETRY_AUDIT`
- V127's PPO-Lagrangian is not retried. V171 observes a mechanically distinct cost-tangent geometry on one frozen V121/V127 batch.
- Control and audit each run exactly one 32-environment-step CPU iteration; the audit must remain bit-exact to the control.
- The projected reward direction must be first-order cost-nonincreasing and retain at least `1/32` of its norm.
- Passing earns only a V172 CPU implementation contract. No behavior cell, hosted run, candidate, Gate 5, RDK-X5, or robot is authorized.
