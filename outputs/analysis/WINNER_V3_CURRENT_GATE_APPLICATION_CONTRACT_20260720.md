# Winner-v3 Prospective Current-Gate Application Contract — 2026-07-20

status: `PASS_PROSPECTIVE_CURRENT_GATE_APPLICATION_CONTRACT`

decision: `AUTHORIZE_AUTOMATIC_RESPONSE_CONDITIONING_INTERFACE_PREREGISTRATION_ONLY`

JSON SHA-256: `17e841450a2dde66182c3d41a06abf8d14366011f811bcde20adb1f1c8f68ddb`

## Correction without reclassification

The completed winner-v3 result remains unchanged. This prospective contract corrects one
source interpretation in the later failure audit: Feetech's detailed 2020-04-10 STS3215
specification explicitly reports `Kt = 8 kg.cm/A`, which converts exactly to
`0.784532 N.m/A`. The simulator's torque-to-current conversion therefore has primary-source
support. The source audit and all 1,024 completed cell classifications remain preserved.

The same specification reports `0.65 A` rated current, `2.5 A` stall current, and electronic
protection that disables output when current is greater than `2 A` for `2 s`. It also reports
`19.5 kg.cm` stall torque and torque shutdown above `70 C`.

Primary specification: https://www.feetechrc.com/Data/feetechrc/upload/file/20200611/6372749961523760249976542.pdf

Catalog corroboration: https://www.feetechrc.com/Data/feetechrc/upload/file/20240706/2024%E9%A3%9E%E7%89%B9%E5%AE%A3%E4%BC%A0%E5%86%8C.pdf

## Prospective offline rule

For every joint and every recorded 50 Hz simulator tick:

1. estimate current as `abs(actuator_force_Nm) / 0.784532`;
2. reject demand above the documented `19.5 kg.cm` / `2.5 A` stall envelope;
3. reject any run of `100` consecutive ticks with current strictly greater than `2 A`;
4. evaluate the complete recorded prefix of an early-terminated cell; and
5. require all 14 joints to pass.

The old `p95 <= 0.65 A` quantity remains reported as a rated-duty diagnostic, but it is not a
prospective pass/fail gate. Feetech defines `0.65 A` as a rated operating point; it does not
define p95 over a 600-tick rollout as a protection or thermal rule. No replacement duty-cycle
or thermal threshold is invented.

## Runtime application

Runtime must retain the servo's own over-current/overload protection, record timestamped raw
current, temperature, and device protection status, and torque off on a device protection or
temperature fault. Round-robin current telemetry cannot prove continuous sub-sample current,
so it is evidence and trend monitoring rather than a replacement for servo firmware protection.

## Authority

This contract authorizes only the automatic-response interface preregistration and its CPU-only
contract. It does not authorize training, Colab, GPU/iGPU use, runtime implementation, X5 or
robot access, torque, motion, Gate 5, deployment, or robot clearance.
