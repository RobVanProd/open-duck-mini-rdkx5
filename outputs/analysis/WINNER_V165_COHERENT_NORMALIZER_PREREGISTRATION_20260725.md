# Winner V165 coherent-normalizer preregistration

- Status: `PREREGISTERED_WINNER_V165_COHERENT_NORMALIZER`
- Keeps V164's fixed 28-iteration block and `1/28` alpha.
- Interpolates deployed mean/std, derives an integer count increment, and reconstructs summed variance exactly.
- No alpha, block-length, reward, or behavior-selected retry.
- Passing earns only one trainer-integration CPU smoke.
- CPU-only; no new PPO update, Colab, Gate 5, RDK-X5, or robot.
