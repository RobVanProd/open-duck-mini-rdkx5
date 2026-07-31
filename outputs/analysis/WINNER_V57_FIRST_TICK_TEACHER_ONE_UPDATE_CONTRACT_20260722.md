# Winner-v57 first-tick teacher one-update CPU contract

- Status: `PREREGISTERED_WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CPU_PROOF`
- Decision: `AUTHORIZE_EXACTLY_ONE_ISOLATED_ADAM_UPDATE_ONLY`
- Contract SHA-256:
  `6dbdf0ab232fa5598003ade46c7de47279cb582eed3ac5011e88189fa804cf05`.
- Optimizer count: `453 -> 454`
- Rows / elements / scale: `44 / 616 / 136.35153198242188`
- Simulator / continuation / support / robot: `0 / 0 / 0 / 0`

The proof recomputes the complete Winner-v56 reset batch, loss, metrics, and
scaled gradient bit-exactly from the V52 final snapshot. It performs one and
only one Adam update while retaining the complete count-453 first- and
second-moment state; resetting or replacing the optimizer is forbidden.

This is intentionally an isolated optimizer/state proof. It does not run a
new PPO rollout or claim to be the integrated continuation objective. The
single update must reduce total, raw, and native-quantized same-batch reset
losses; change all 12 trainable leaves through the inherited Adam state; leave
the source state unchanged; and round-trip parameters, optimizer, and
normalizers in a new count-454 snapshot.

One non-selected ONNX graph must retain the exact stateful `115+14+64 ->
14+14+64` ABI, hard action bounds, previous-action chain, and JAX agreement.
Teacher/configuration/held-out tokens are forbidden from the export. A pass
authorizes only a separately preregistered integrated continuation—not support
evaluation, checkpoint selection, deployment, or robot clearance.
