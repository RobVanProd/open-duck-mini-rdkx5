# Ground-Up Torso-COM Full-Observation and Actor-Sensitivity Result

status: `PASS_TORSO_COM_FULL_OBS_STUDY_COMPLETE`
decode: `RESET_TRANSIENT_ONLY_UNDER_FROZEN_PROBES`
actor sensitivity: `SUBSTANTIAL_ACCEL_RESPONSE`
decision: `SUPPORT_PREREGISTERED_SIGNED_CAUSAL_RESPONSE_STUDY`

No p-value or independent-sample inference is reported. The actor forks change only `obs[3:6]` and do not establish corrective sign.

## Decode result

Both frozen feature families pass only at tick zero. Neither the instantaneous
curve nor any single predeclared local-window width passes the persistence rule.

| feature | tick 0 | tick 8 | tick 16 | tick 24 | tick 32 | tick 40 |
|---|---:|---:|---:|---:|---:|---:|
| ACCEL3 min fold accuracy | 1.000000 | .333333 | .444444 | .333333 | .333333 | .541667 |
| FULL115 min fold accuracy | 1.000000 | .500000 | .333333 | .333333 | .333333 | .333333 |

For ACCEL3, the strongest failed local window is width 16 ending at tick 16
with minimum fold accuracy .729167, below the frozen .75 accuracy boundary and
without satisfying the complete macro-F1/recall rule. At endpoints 24/32/40,
no common width greater than one passes. FULL115 has no passing local window.
This is a probe-limited `RESET_TRANSIENT_ONLY` result, not proof that the state
contains no nonlinear COM information.

## Actor-fork result

Sequential ONNX replay reproduces every recorded baseline action exactly
(maximum absolute error 0.0). The 576 fixed forks cover 144 traces at ticks
0/24/32/40, hold recurrent input and the other 112 observations identical,
and add/subtract only the preregistered measured COM direction in `obs[3:6]`.

| policy | reset RMS p95 | reset max p95 | mid RMS p95 | mid max p95 |
|---|---:|---:|---:|---:|
| A05_DIRECT_1003520 | 0.02115135 | 0.06374285 | 0.04190933 | 0.11129116 |
| A05_DIRECT_2007040 | 0.01595456 | 0.03911144 | 0.04511210 | 0.12574782 |
| U05_DIRECT_1003520 | 0.01641945 | 0.05231559 | 0.03898227 | 0.09685388 |
| U05_DIRECT_2007040 | 0.01436999 | 0.03075952 | 0.03969762 | 0.09709400 |
| U_CURRICULUM_1024000 | 0.00785669 | 0.02051156 | 0.03760864 | 0.08262180 |
| U_CURRICULUM_512000 | 0.01246701 | 0.03135245 | 0.02974990 | 0.07205755 |

Every policy exceeds the preregistered substantial-response boundary at reset
and mid-gait. Mid-gait p95 maximum action differences span .07206-.12575
normalized action, equal to about .0180-.0314 rad under the frozen .25-rad
action scale. This rejects the near-zero accelerometer-Jacobian hypothesis.

The combined evidence is specific: the policies respond materially to a local
accelerometer perturbation along the measured COM direction, while the frozen
linear probes do not recover actual COM class after the reset transient. The
response may be stabilizing, destabilizing, or state-inappropriate; this study
does not determine its sign.

Decision: preregister a read-only CPU signed causal-response study. Do not
start an objective, optimizer, memory, estimator, explicit-COM, or range-change
arm from this result alone. No implementation, training, Colab, GPU/iGPU,
runtime design, RDK-X5, robot access, deployment, torque, or motors are
authorized.
