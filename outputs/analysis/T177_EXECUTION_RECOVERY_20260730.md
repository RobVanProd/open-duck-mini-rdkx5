# T177 execution interruption and cache-safe recovery

T177 reached a valid sealed failure in the positive-Z `Half/P30` block, then
the following `Half/P31/34` worker exited with Windows return code
`3221226505`. The interrupted block produced no evaluation, manifest, or trace
rows. Its only file was a 217-byte JAX warning log at SHA-256
`8059bd2e847284f04aa0648d7c436b04ddcb71fddfa9a6489dc0769af9416764`.

The unsealed directory was moved intact to:

`D:\CodexArtifacts\open-duck-policy\t177_infrastructure_interruptions\20260730T010546_TORSO_COM_Z_POS_HALF_P31_34`

The repository remained at policy commit
`3188951819cf8361267192ebfc371864a9db6a86`. No source, threshold,
preregistration, graph, fit, seed, or condition changed.

One initial resume command omitted the mandatory `--execute` assertion and was
rejected by argument parsing before cache or evaluator access. The corrected
resume loaded all 45 already sealed blocks from their verified manifests,
including the positive-Z `Half/P30` failure, and executed only the three
previously unsealed blocks. Zero completed behavior blocks were rerun.

The resumed sequence completed with empty stderr and produced the terminal
result:

- status: `HOLD_T177_HEAD_PREFIX_MEAN_FULL_R2`;
- decision: `CLOSE_HEAD_PREFIX_MEAN_AT_FIRST_FAILED_R2_CONDITION`;
- completed conditions: `12`;
- cells: `187/192` green;
- first failed condition: `TORSO_COM_Z_POS`;
- canonical result SHA-256:
  `59d0d3c73d808ff258e73f9cef0d0ff1734900776ab58c22d59e4ae8ae9219b2`.

`tools/verify_t177_terminal.py` independently verifies all 48 block manifests,
their 192 nested evaluation/log/trace receipts, the preregistered block
contracts, the recomputed condition summaries, the first-failure stop, and the
zero hosted/hardware authority boundary.

This recovery changes no scientific result and authorizes no retry of the
closed head-prefix-mean formulation, training, deployment audit, Gate 5,
RDK-X5/robot access, torque, or motion.
