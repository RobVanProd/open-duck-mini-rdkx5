# Winner-v56 first-tick teacher gradient CPU contract

- Status: `PREREGISTERED_WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_CPU_CONTRACT`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_FIRST_TICK_GRADIENT_PROOF_ONLY`
- Contract SHA-256:
  `84774c59f55ab13dc9c17c74c7e1529cab85ac0eb6c04a7a14cf8eb37c0adca7`.
- Rows / elements: `44 / 616`
- Scale: `136.35153198242188` (equal frozen V52 term weight)
- Simulator steps / optimizer / export / robot: `0 / 0 / 0 / 0`

The proof uses the exact V52 final count-453 snapshot. It builds reset inputs
for the 11 frozen training configurations and both measured plants, once raw
and once after native quantization. Held-out teacher labels are explicitly
forbidden. Every row starts from zero previous action and zero hidden state,
and all 14 bounded V42 target actions are supervised.

The reset loss is a mean over exactly 616 action elements. Its coefficient is
not searched: it equals the existing frozen full-action teacher coefficient,
so the complete reset mapping receives one objective-term weight instead of
being diluted across the 250-tick horizon.

Because previous action and hidden input are both zero, the preregistered
gradient locality is exact. Only `obs_weight`, `hidden_bias`, `action_weight`,
and `action_bias` may have nonzero gradients. Recurrence, predictor, value,
and log-standard-deviation leaves must remain zero. Default-off loss and
gradients must be bit-exact, and JAX actions must match the unchanged ONNX
graph within `1e-7`.

A pass authorizes only preregistration of one CPU Adam update from count 453
to 454. It does not itself mutate or export a policy, run behavior cells, or
grant robot clearance.
