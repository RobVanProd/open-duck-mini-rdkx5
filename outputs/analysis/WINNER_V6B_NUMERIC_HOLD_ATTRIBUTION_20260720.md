# Winner-v6b Numeric Hold Attribution

Status: `PASS_V6B_HOLD_ATTRIBUTED_TO_FLOAT32_BOUNDARY`

Decision: `PREREGISTER_DISTINCT_V7_INWARD_PROJECTION_TRANSFORM_ONLY`

JSON SHA-256: `eb3ed6a951b76e4c88b9adcbb52de3b3a6a84719f469ebfcd788dcef65ee879c`

Both protected checkpoints missed the frozen `1e-7` delta assertion by `1.2665987014770508e-07` normalized action, or `1.0625` float32 epsilon. Every other v6b check passed. The v6/v6b route remains closed and is not retried.

The next hypothesis changes the protected graph itself: a final inward-rounded projection with a fixed analytic margin of four float32 epsilons. It must pass a new graph contract and later full behavior revalidation before any calibrator work. No training, Colab, GPU, runtime, or robot action is authorized.
