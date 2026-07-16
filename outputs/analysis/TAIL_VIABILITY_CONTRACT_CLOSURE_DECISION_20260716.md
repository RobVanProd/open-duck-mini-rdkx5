# Tail, Viability-Prevention and Contract-Closure Decision

Status: `PROGRAM_COMPLETE_STOP_FOR_REVIEW`

Final decision token: `STOP_FOR_REVIEW_NO_NEW_FORMULATION`

## Decision tree outcome

1. Phase A failed. T1/T2/T3 were fully recovered and evaluated, but no scale
   passed the persistent six-cell gate. The family is closed and a fourth
   scale is forbidden.
2. C1 found a definite contract mismatch: training obs[83:97] contains the
   measured bridge's realized applied target, while the native runtime contains
   the prior slew-limited sent target. The runtime was not changed.
3. C2 completed 24/24 cells. Both phase orderings passed; 0/12 pairs were
   material and the largest absolute tracking-p95 delta was 0.007245467 rad.
   Keep the deployed and training-matched observe-then-advance ordering.
4. C3 mined and verified the June 21 adjacent tick-0/1 legacy golden vector.
   Previous sent target and phase chaining are exact; no new capture is needed.
5. B1 froze a 33-D metric and radius 0.695473201359 from all 298 failure
   states, with X_NEG weighted 3x X_POS. The radius was not widened.
6. B2 ran all 18 comparator cells. Applied-target 1M and tail T2 failed on
   tracking; BEST failed on forward progress. Every run completed 600 ticks,
   so there were zero actual falls and zero routed fall labels. B3 is negative:
   `CLOSE_VIABILITY_PREVENTION_NO_ROUTED_FALL_CORPUS`. No hosted session or
   training was started.
7. C4 adds default-off, guarded one-servo-per-logged-tick current/voltage/
   temperature telemetry. Mock coverage is 14 ticks; incremental mock p95 is
   0.000001994 s against a 0.005 s budget. RDK API binding and serial timing
   remain unverified and were not inferred from the mock.
8. Phase D records seven closed formulations. Future preregistrations must cite
   the ledger and prove they are not a closed branch in new packaging.

## What remains supported

- The protected nominal G1/T2 checkpoint pair remains the nominal walking
  winner. This program did not weaken or promote it.
- The signed torso-COM failure is not repaired by exposure alone, a reset
  scalar, the frozen affine oracle residual, or the bounded six-joint
  receding-horizon formulation.
- C1 is a real runtime contract defect and must be resolved and independently
  contracted before Gate 5 readiness. It is not evidence that changing the
  slot will solve torso-COM robustness.
- A materially new adaptation or gait formulation may still exist, but the
  A-fail/B3-negative stop rule prohibits opening it automatically. Review must
  choose it explicitly and cite the closed-branches ledger.
- C4's RDK Rustypot temperature binding and real bus-time margin await a
  separately authorized read-only hardware contract.

No training reward selected any outcome. No Colab session, local GPU/iGPU,
RDK-X5, robot, motor, torque, deployment or policy overwrite was used in this
program. Robot clearance remains `NO`.
