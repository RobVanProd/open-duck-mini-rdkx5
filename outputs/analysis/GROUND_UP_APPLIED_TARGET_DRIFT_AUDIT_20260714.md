# Ground-Up Applied-Target 1M→2M Drift Audit

status: `PASS_APPLIED_TARGET_DRIFT_AUDIT`
measured mechanism: `ACTOR_PARAMETER_DRIFT_DOMINATES_NORMALIZER_DRIFT`

actor-only raw-action RMS drift: `0.09495878`
normalizer-only raw-action RMS drift: `0.01407022`
actor/normalizer ratio: `6.749`

## Contract checks

- checkpoint_structures_match_and_are_finite: `PASS`
- own_onnx_trace_replay_within_1e_5: `PASS`
- both_trace_corpora_have_162_samples: `PASS`
- one_million_full_gate_passed: `PASS`
- two_million_tracking_gate_failed: `PASS`
- training_reward_increased_while_external_gate_regressed: `PASS`

## Objective-versus-gate evidence

- hosted evaluation reward delta: `+16.73486328`
- hosted imitation component delta: `+222.71350098`
- hosted linear-velocity component delta: `+32.77563477`
- hosted angular-velocity component delta: `+552.68823242`

The optimizer improved every listed hosted objective while the frozen
hardware-oriented joint-target tracking gate worsened. The fitted bridge
error stayed effectively unchanged on the largest regressions. This is
evidence of actor/objective drift, not checksum, bridge, checkpoint-restore,
or observation-normalizer corruption.

## Per-joint evidence

Largest external joint-tracking regressions:

- left_hip_yaw: `+0.02898892 rad` (bridge delta `+0.00000000 rad`)
- left_knee: `+0.02816071 rad` (bridge delta `+0.00000847 rad`)
- right_hip_roll: `+0.01273722 rad` (bridge delta `+0.00000000 rad`)

Training remains unauthorized. This audit measures drift; it does not select a retention recipe by itself.
