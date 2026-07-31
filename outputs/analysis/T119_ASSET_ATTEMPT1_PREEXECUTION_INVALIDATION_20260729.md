# T119 asset attempt 1 pre-execution invalidation

- Status: `INVALID_T119_ASSET_ATTEMPT1_RATE_VECTOR`
- Cause: asset exporter received the obsolete 5.24 rad/s vector instead of T100C's exact measured vector
- Router parameters and recurrent hidden state matched; only the output limiter differed
- Optimizer / simulator / behavior / Colab / robot: `0 / 0 / 0 / 0 / 0`
- Decision: rebuild zero-update assets with the exact source initializer vector
