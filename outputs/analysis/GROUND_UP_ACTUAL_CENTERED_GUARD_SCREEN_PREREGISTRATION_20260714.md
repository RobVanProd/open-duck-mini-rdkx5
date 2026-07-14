# Ground-Up Actual-Centered Guard Screen Preregistration

status: `PREREGISTERED_CPU_ONLY`

## Causal basis

All 3,329 tracking-boundary events across the TAIL, RATE, and SWA families are
compound. The bridge and servo components are each below `0.20 rad` alone,
have the same sign in every event, and cross the boundary only when summed.
That selects a missing absolute invariant: a commanded pitch target must not
accumulate farther than a fixed margin from measured joint position.

## Frozen stateful transform

The 115-D actor observation already contains measured joint-position offsets at
indices `13:27`. For the six pitch joints only, the source ONNX velocity-bounded
target is additionally clamped around `home + obs[13:27]`. Nonpitch outputs are
unchanged. The guarded action becomes both `continuous_actions` and
`previous_action_out`, so the next tick's state describes the realized command.

The existing per-joint velocity boundary remains first in the chain. A CPU
contract must prove both bounds along reachable chained inputs; it must reject
any candidate for which the intervals conflict.

## Frozen margins

The hardware threshold is `0.20 rad`, control period is `0.02 s`, and the
largest pitch target-rate boundary is `1.75 rad/s`, or `0.035 rad/tick`.

| arm | margin |
|---|---:|
| `G1_EXACT_BOUNDARY` | 0.2000 rad |
| `G2_HALF_TICK_BUFFER` | 0.1825 rad |
| `G3_FULL_TICK_BUFFER` | 0.1650 rad |

T2 and T3 half/final sources produce 12 ONNX policies and exactly 72 CPU
behavior cells. The same margin/tail combination must pass both checkpoints.
Selection prefers the largest margin, then lower worst tracking, then higher
minimum velocity. Training reward cannot select a result.

A nominal winner authorizes only a separately preregistered x=0 preservation
gate. No training, Colab, local GPU, RDK-X5, robot, deployment, torque, or motor
access is authorized.
