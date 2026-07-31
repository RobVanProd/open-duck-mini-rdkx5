# T178 analysis-field provenance correction

- Status: `INVALIDATED_T178_HANDOFF_CLASSIFICATION_FIELD_PROVENANCE`
- Original T178 result SHA: `425d9035...ba78e24e`
- Invalidated claim: `HANDOFF_STATE_MISMATCH`
- Preserved evidence: trace integrity, midpoint analysis, and failure-signature analysis
- Next authority: preregister one saved-trace-only T178B pre-action field correction

The evaluator captures `actual_position_pre_rad` before the policy action at
`closed_loop_sim_eval.py:2770`. It then computes the current command's
`applied_target_rad`, advances the simulator at line 3006, and records `qpos`
and `qvel` at lines 3081–3082. Those three latter fields are outputs of the
current action and are expected to differ across commands. They cannot
establish a handoff mismatch.

T178B must compare only the pre-action calibration context, recurrent inputs,
`actual_position_pre_rad`, and the pre-action bridge-applied observation in
`obs_state[83:97]`. It may not change any threshold, read any new behavior, run
simulation, train, use Colab, or access the robot.
