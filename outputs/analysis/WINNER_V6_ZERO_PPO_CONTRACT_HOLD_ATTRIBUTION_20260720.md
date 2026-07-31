# Winner-v6 Zero-PPO Contract Hold Attribution

Status: `PASS_HOLD_ATTRIBUTED_TO_CONTRACT_FIXTURE_SEMANTICS`

Decision: `REQUEST_RUNTIME_BOUND_SEMANTICS_REVIEW_NO_RETRY`

JSON SHA-256: `d318f2c0ef1931f30574f71e8f7f1bffd971bf16815f152c1213bc9dc4e2a3b3`

The completed formal result remains a hold and is not retried. The new adapter's enabled bound-stress graph passed, and its disabled graph preserved both protected checkpoints bit-exactly. The failed combined check applied an upstream previous-action delta rule after the protected graph's downstream actual-centered guard on independently randomized joint/action state.

The next action is a runtime semantics review only. Training, a replacement contract run, Colab, GPU, runtime implementation, robot access, torque, motion, Gate 5, deployment, and robot clearance remain blocked.
