# Phase 2 z=0.00245 Support Recovery Next Decision

status: `HOLD_Z00245_ONE_SHOT_BC_CLOSED`

## Summary

The latest z=0.00245 seed-5 recovery probes close the simple relabel-and-fit branch.

The Phase A2 gain099 candidate cannot provide positive source traces at z=0.00245: seed 5 fails quickly at both `x=0.0` and `x=0.08`, and the `x=0.08` trace records corrected-envelope velocity excess. The usable positive terrain source remains the already-recorded z=0.0024 source manifest.

Two bounded recovery fits then tried to bridge z=0.0024 source behavior into the z=0.00245 seed-5 failure:

- Iter0 copied z=0.0024 source labels into the z=0.00245 failed states and fit a contact/phase BC student.
- Iter1 softened the source copy with alpha `0.35` and increased target-rate regularization.

Both closed-loop students failed the short seed-5 gates by saturation, over-envelope target rate, fall/termination, or wrong-direction motion. The soft fit reduced supervised target rate, but closed-loop execution still saturated at `5.24 rad/s` and failed the `x=0.0` hard stop.

## Evidence

| artifact | status | key result |
|---|---|---|
| `PHASE2_Z0025_RESET_SETTLE_DIAGNOSTIC_20260702.md` | `HOLD_RESET_SETTLE_WORSE` | Reset settling worsened seed-5 support and broke `x=0.08`. |
| `PHASE2_Z00245_SOURCE_SEED5_PROBE_DECISION_20260702.md` | `HOLD_Z00245_NOT_POSITIVE_SOURCE` | z=0.00245 seed-5 traces are failed traces, not source labels. |
| `PHASE2_Z00245_SUPPORT_RECOVERY_ITER0_DECISION_20260702.md` | `HOLD_RECOVERY_ITER0_OVERDRIVES` | x=0 survives 2s but with action saturation; x=0.08 lunges and falls. |
| `PHASE2_Z00245_SUPPORT_RECOVERY_ITER1_SOFT_ALPHA035_DECISION_20260702.md` | `HOLD_SOFT_ALPHA_RECOVERY_STILL_OVERDRIVES` | Softer labels still fail x=0 by fall/termination and velocity saturation. |

## Decision

Do not promote either z=0.00245 recovery student. Do not use their ONNX files as parents. Do not run full 8-seed gates on them. Do not repeat another one-shot BC fit on the same tiny two-trace z=0.00245 recovery set.

The blocker is not missing relabel plumbing. The current recovery labels express support recovery through closed-loop saturation. The next valid branch must change the mechanism:

- train or optimize on-policy with the corrected envelope active during the update,
- or generate a structurally different intermediate support target before fitting a student,
- and require the short seed-5 `x=0.0` gate to pass before any `x=0.08`, 8-seed, Colab-scale, or promotion gate.

## Next Authorized Shape

The next offline branch may use the z=0.0024 positive source manifest only as an anchor, not as direct copied labels for failed z=0.00245 states.

Minimum gate order:

1. z=0.00245 seed 5, `x=0.0`, short gate: no fall, no action saturation, no corrected-envelope velocity excess, and `|vx|` near zero.
2. z=0.00245 seed 5, `x=0.08`, short gate: positive forward motion, no fall, no action saturation, no corrected-envelope velocity excess.
3. z=0.00245 8-seed gates at `x=0.0` and `x=0.08`.
4. Regression gates at the known z=0.0024 source rung.

If step 1 fails again by over-envelope target rate or saturation, stop and report. Do not soften/reweight the same labels again.

No robot tests, SSH, deploy, grounded replay, PPO training, or runtime behavior changes were performed for this decision artifact.
