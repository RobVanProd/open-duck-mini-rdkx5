# Ground-Up Tracking-Tail Colab Launch

status: `RUNNING_FIXED_HOSTED_SCREEN`

- session: `ground-up-tracking-tail-20260714`
- accelerator: `T4`
- launch time: `2026-07-14T18:36:34Z`
- background PID: `845`
- remote asset validation: `PASS`
- arm order: `T1_QUARTER -> T2_EQUAL -> T3_FOUR`
- independent protected restore per arm: `true`
- maximum hosted wall time: `14400` seconds
- maximum compute at reported 1.07 CU/hour: `4.28` CU
- selection uses training reward: `false`
- behavior status: `UNEVALUATED`

## Mechanical schedule correction

T1 emitted steps `0`, `512000`, and `1024000`. Brax computes 25 training
updates per evaluation epoch from the frozen command, so these are the exact
quantized half/final steps. The original supervisor predicted `501760` and
`1003520` and stopped after T1 completed, before T2. No reward or behavior
result was inspected. Recovery PID `5643` validates and retains only the three
complete T1 exports, then runs unchanged T2 and T3 independently from the same
protected source.

This launch authorizes only the preregistered hosted training package. It does
not authorize local GPU/iGPU, RDK-X5, robot, deployment, torque, or motor use.
