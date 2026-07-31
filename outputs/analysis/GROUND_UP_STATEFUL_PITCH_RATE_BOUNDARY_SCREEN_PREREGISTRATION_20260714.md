# Ground-Up Stateful Pitch-Rate Boundary Screen Preregistration

status: `PREREGISTERED_CPU_ONLY`

## Causal question

Can a slightly lower stateful pitch-chain target-rate boundary remove the
remaining phase-local tracking occupancy without losing the complete gait?

Across all 36 frozen tail-search traces, `97.6268%` of gate-setting exceedance
ticks occur at or within two ticks after the measured target-rate boundary,
versus `79.7326%` elsewhere (odds ratio `10.4565`). At least `88.31%` of every
trace's exceedances lie in four of the 27 reference-period bins. This selects a
rate-boundary A/B, not another reward search.

## Protected policies

Use both half and final checkpoints from `T2_EQUAL` and `T3_FOUR`. The existing
unmodified 600-tick evaluations are the controls. The transform changes only
the six pitch-chain entries of the stateful ONNX `max_action_delta` initializer
at indices `2,3,4,11,12,13`. All actor weights, observations, reference,
bridge, action scale, non-pitch limits, inputs, outputs, and state feedback stay
byte-identical or numerically identical as applicable.

## Frozen multipliers

T3 final's worst p95 is `0.20410053133964537`, so its exact gate ratio is:

`r = 0.20 / 0.20410053133964537 = 0.9799092569101565`

Before transformed outcomes, freeze one, two, and four times that measured gap:

| arm | pitch-rate multiplier |
|---|---:|
| `R1_GATE_GAP` | `0.9799092569101565` |
| `R2_DOUBLE_GAP` | `0.959818513820313` |
| `R3_FOUR_GAP` | `0.919637027640626` |

No midpoint, additional multiplier, joint subset, per-joint tuning, policy gain,
reward, training, bridge, observation, reference, or reset change is allowed.

## Transform contract

Each generated ONNX must pass the original checker, preserve the exact graph
interface `obs,previous_action -> continuous_actions,previous_action_out`, keep
all non-`max_action_delta` initializers byte-identical, change only the six
pitch-chain delta values by the frozen multiplier, and prove over an eight-tick
chain that state output equals action and the new per-joint bounds have at most
`1e-6` excess.

## Frozen behavior gate

Evaluate each transformed half/final policy at x=.074/.077/.080, seeds 100/101,
deterministic home reset, fitted bridge, and 600 ticks on local CPU only. A
checkpoint passes only if all six cells pass the unchanged candidate gate,
complete 600 ticks with bilateral support, retain zero saturation/rate excess,
and have worst pitch-chain tracking p95 <=.20 rad.

A rate multiplier advances only if both half and final checkpoints of the same
tail arm pass. If multiple pass, choose the least rate reduction, then lower
worst tracking p95, then higher minimum forward velocity. Training reward is
not read or used. If none passes, close this exact stateful rate-boundary screen.

Even a nominal winner authorizes only a separately preregistered x=0 preservation
gate. This screen never authorizes local GPU/iGPU, RDK-X5, robot, deployment,
torque, or motor use.
