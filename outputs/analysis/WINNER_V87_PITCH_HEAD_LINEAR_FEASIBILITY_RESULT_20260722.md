# Winner-v87 linear pitch-head feasibility result

- Status: `PASS_WINNER_V87_PITCH_HEAD_LINEAR_FEASIBILITY_AUDIT`
- Classification: `FROZEN_HIDDEN_LINEAR_PITCH_HEAD_INSUFFICIENT`
- Selected source for a fitted-head proof: `none`
- Half source / full-fit / heldout RMS: `0.090443 / 0.085178 / 0.124209`
- Final source / full-fit / heldout RMS: `0.094140 / 0.083779 / 0.121843`
- Design rank: `65 / 65` at both endpoints
- Rollout episodes / least-squares fits: `160 / 26`
- Optimizer updates / snapshots / ONNX / support cells / robot access: `0 / 0 / 0 / 0 / 0`
- Result SHA-256: `c54bbad33bffec85d7ddafb6ccb45231f83929eadae8c5eb2fb9edb1f94298ac`

The existing affine-plus-tanh pitch head is not the remaining bottleneck. A
full fit on each endpoint's frozen hidden states lowers in-sample bounded pitch
error only modestly, while leaving one complete configuration out makes error
substantially worse than the unchanged source. Both design matrices have full
rank and repeat solves are bit-exact, so this is not a rank or solver failure.

The result rejects a fitted-head proof and selects only a separately
preregistered recurrent-representation diagnostic. It writes no policy
artifact, selects no checkpoint, and leaves `robot_clearance: false`.
