# Ground-Up Torso-COM Reset-Estimator Input Package Contract

status: `PASS_RESET_COM_ESTIMATOR_INPUT_CPU_PACKAGE_CONTRACT`

The preregistered CPU package contract passes with no failed checks. This is a
zero-training, zero-dynamic-step package result; it is not behavior evidence.

## Checkpoint expansion

- Protected source directory SHA-256:
  `b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a`.
- Expanded checkpoint directory SHA-256:
  `9f9b540435013d1eaf29450f3fcf1e6127fc7a80ac25b073026d1a49d221d6f5`.
- Policy observation: 115 -> 116.
- Privileged observation: 226 -> 227.
- Actor first kernel: `(115,512)` -> `(116,512)`.
- Critic first kernel: `(226,512)` -> `(227,512)`.
- New normalizer coordinate at index 101: mean `0`, standard deviation `1`,
  summed variance `8,048,640` in both streams.
- New actor and critic rows at index 101: exactly zero.
- All other checkpoint values: bit-exact.
- Expanded save/restore: bit-exact.
- Actor distribution and critic value maximum error at `z=-1,0,+1`: exactly
  zero in all six comparisons.
- The raw 14-D reference action remains exactly the final 14 policy inputs.

Expansion JSON SHA-256:
`e5e7a3e8e34e7cc2ed511828d0e5323aed44d5e2d384082d31718ebb0a42b09c`.

## Reset-latch contract

| torso X-COM | max anchor error (m/s^2) | normalized latch | independent latch error | state / privileged |
|---:|---:|---:|---:|---:|
| -.05 m | .0000758171 | -1.000000000 | 0 | 116 / 227 |
| 0 m | .0000801086 | -.0000445114 | 1.57e-12 | 116 / 227 |
| +.05 m | .0001299381 | +.999988556 | 4.19e-8 | 116 / 227 |

All three models change only `body_ipos[2,0]`. The latched values are finite,
bounded, strictly ordered, and match an independent implementation of the
frozen estimator. In both policy and privileged observations the latch is
exactly coordinate 101. Static source inspection finds one reset assignment
and no step-time write.

With the feature disabled, the latch key is absent and the environment remains
exactly 115-D policy / 226-D privileged. The feature and CLI flag default off.

Contract JSON SHA-256:
`00e152e469e8fdeba49d7031c259b688f722ea75764297cb7ea51431d9fc2914`.

## Execution and authority

Execution used CPU `TFRT_CPU_0`, three reset cells, zero dynamic steps, zero
training steps, no Colab, no local GPU/iGPU, no RDK-X5, and no robot.

The passing contract supports only a separate hosted-training
preregistration. It does not authorize training or a Colab session now, does
not provide behavior clearance, and does not authorize R2/R3, runtime,
deployment, RDK-X5, or robot access.
