# Winner-v56 first-tick teacher gradient result

- Status: `PASS_WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_CPU_CONTRACT`
- Decision: `AUTHORIZE_ONE_FIRST_TICK_TEACHER_ADAM_UPDATE_PREREGISTRATION_ONLY`
- Result SHA-256:
  `6363c17ab6bcf602dff964d3770bcd8e38f73669ca4f2a521aae5c319051c1a8`.
- Loss / scaled loss: `0.004075534176081419 / 0.5557053089141846`
- Pitch / non-pitch RMS: `0.0957130640745163 / 0.01616910845041275`
- JAX/ONNX maximum action error: `2.2351741790771484e-08`
- Nonzero gradient leaves: `["action_bias", "action_weight", "hidden_bias", "obs_weight"]`
- Simulator steps / optimizer / export / robot: `0 / 0 / 0 / 0`

All nine frozen checks pass. The exact 44-row batch contains 22 raw and 22
native-quantized training reset rows, selects all 616 action elements, and
contains no held-out label. Raw and quantized reset MSE are
`0.0040754894725978374` and `0.0040755788795650005`, respectively, so the
declared physical resolution does not create a separate optimization problem.

The residual is concentrated in the causal group selected by Winner-v54:
pitch-chain RMS is `0.0957130640745163`, versus `0.01616910845041275`
off-pitch, with maximum absolute error `0.22182981669902802`.

At the frozen scale, the only nonzero gradient leaves and their maximum
absolute values are:

| Leaf | Maximum absolute gradient |
| --- | ---: |
| `action_bias` | 0.9897239804267883 |
| `action_weight` | 0.9830502271652222 |
| `hidden_bias` | 0.006736832670867443 |
| `obs_weight` | 0.24680528044700623 |

Every recurrence, predictor, value, and log-standard-deviation gradient is
exactly zero, as required by the zero-state first-tick contract. Default-off
loss and gradients are bit-exact.

This pass authorizes only a separate single CPU Adam-update preregistration
from count 453 to 454. That proof must retain the existing optimizer state,
show same-batch reset loss reduction, preserve frozen leaves, serialize and
restore the complete state, and export a non-selected stateful graph. No
continuation or support evaluation is authorized yet.
