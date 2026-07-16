# Deployment Review Decision

Status: `PASS_REVIEW_COMPOSITE_WINNER_RETAINED`

Decision token: `ADVANCE_COMPOSITE_WINNER_TO_MEASURED_DEPLOYMENT_QUESTIONS`

## Correct project headline

The project has its first persistent full-horizon nominal winner. It is the
protected `G1_EXACT_BOUNDARY/T2_EQUAL` checkpoint pair composed with:

1. the actual-position-centered tracking guard;
2. the exact zero-command deadband; and
3. the conservative left-ankle envelope repair.

Both persistent checkpoints pass the complete 16-cell R1 matrix under the P30
and P31/34 actuator fits. The composite's recorded worst tracking p95 is
0.183170038 rad, minimum forward velocity is 0.084911748 m/s, and measured
saturation, rate excess and envelope excess are zero. Its moving support is
intentionally narrow: x=0.074, 0.077 and 0.080 m/s, plus exact stand at x=0.

The prior headline `Remediation winner: NONE` referred only to the three closed
torso-COM remediation arms. It did not erase or supersede the nominal composite
winner.

## Evidence boundary

The composite winner passes R2 floor-friction 0.5/1.0, joint-frictionloss
0.9x/1.1x and armature 1.0x/1.05x. It fails corrected
`TORSO_COM_X_NEG=-0.05 m`; the signed follow-up also fails at `+0.05 m`.
Generic torso-COM robustness is not established, and robot clearance remains
`NO`.

Corrected torso-COM exposure, three targeted-COM arms, a reset-estimator latch,
an affine oracle residual and the bounded viability funnel all failed to clear
the signed endpoint gate. This review therefore forbids automatically reopening
generic COM training.

## Authorized next work

Only these deployment-specific offline branches advance:

- preregister and execute a CPU-only signed X-axis torso-COM break-radius curve
  on the frozen composite winner;
- preregister an offline estimate of the real build's torso COM from CAD,
  measured component masses and measured placement;
- pin the winner's 115-D stateful ONNX input/state contract, specify a v2
  contract for this policy family, and prove whether a fitted-bridge forward
  observer is required before any Gate 5 planning;
- preserve the already-passing legacy `101x14.v1` golden vector as a legacy
  stack contract, not as the winner's deployment contract; and
- extract the massless-body randomizer defect and the MJX JIT/eager forward
  discrepancy as issue-ready upstream findings.

If the measured real-build model error is inside the preregistered break radius
with frozen margin, the COM question closes for this build. If it is outside,
correct the simulator torso model to the measured build and re-gate the frozen
winner. Generic COM training may not reopen unless that targeted model-correction
branch fails under a separate preregistration.

No training reward selected this decision. No training, hosted allocation,
robot, RDK-X5, local GPU/iGPU, deployment or policy overwrite is authorized.

