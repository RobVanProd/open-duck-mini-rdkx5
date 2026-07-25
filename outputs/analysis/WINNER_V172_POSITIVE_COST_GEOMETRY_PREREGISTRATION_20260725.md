# Winner V172 first-positive-cost geometry preregistration

- Status: `PREREGISTERED_WINNER_V172_POSITIVE_COST_GEOMETRY`
- Corrects V171's zero-realized-cost sufficiency gap by capturing only the first strictly positive raw-cost rollout batch.
- Runs one 1,024-step instrumented CPU smoke and reuses the already frozen V127 smoke as its bit-exact control.
- The tangent must remain first-order cost-nonincreasing and retain at least `1/32` of the reward direction.
- Passing earns only V173 CPU implementation work. No hosted run, candidate, robustness matrix, Gate 5, RDK-X5, or robot.
