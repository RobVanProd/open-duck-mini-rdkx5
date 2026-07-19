# Winner-v2 Action-History Semantics Correction Preregistration

Status: `PREREGISTERED_METADATA_ONLY_HISTORY_ORDER_CORRECTION`

Corrected package files written: `0`

## Defect

Runtime review commit `679bc10912d63d8ae7c23ccb5d2e55ad45f7d6cb`
independently constructed the winner-v2 observation and found that the handoff
metadata labels `obs[41:55]`, `obs[55:69]`, and `obs[69:83]` one transition too
new. The package's frozen golden tensors and evaluator source agree with each
other and contradict the labels.

In `tools/closed_loop_sim_eval.py`, the post-transition observation is built
before the action-history variables shift. Therefore observation used for
control tick `t` contains:

- `obs[41:55]`: final action from `t-2`;
- `obs[55:69]`: final action from `t-3`;
- `obs[69:83]`: final action from `t-4`.

The separate stateful input remains:

- `previous_action[t]`: final action from `t-1`.

All histories are zero when their referenced tick is before reset. This is a
metadata/generator/checker defect, not a policy-weight or trace defect.

## Frozen correction scope

Only the following may change:

1. the three action-history names/timing/delay descriptions emitted by
   `tools/build_winner_v2_runtime_handoff.py`;
2. the matching table/prose in the package `README.md`;
3. package `observation_map.json` and `policy_contract.json` metadata;
4. package `inspect_and_smoke.py` so it validates the corrected history rows
   and the already-selected checkpoint;
5. `manifest.json`, regenerated after the above files are final; and
6. policy handoff/status prose and one explicit correction contract.

The package schema advances from `winner_v2_rdkx5_native_handoff.v1` to
`winner_v2_rdkx5_native_handoff.v1.1`. The selected checkpoint metadata is
updated from the now-superseded `NOT_READY` value to the already-preregistered
selection result:

- step: `512000`;
- SHA-256:
  `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`.

The 1024000 graph remains an audit/persistence sibling, not a selected runtime
binary.

## Frozen identity requirements

The correction is valid only if all of these remain byte-identical:

- both ONNX policies;
- all four 600-tick NPZ golden packs;
- all four lossless full-trace archives;
- compact golden vectors;
- P30 fit and observer source;
- projected reference table;
- golden evidence and environment lock; and
- every external behavior/transform artifact other than the handoff builder
  source whose metadata literals are corrected.

The selected 512000 ONNX hash must remain exact. No behavior cell, simulator
step, selection rule, tracking threshold, COM result, training run or reward is
read or changed by this correction.

## Frozen checks

Across every tick in all four 600-tick NPZ packs:

1. `obs[41:55]` equals zero for `t<2`, else `final_action[t-2]`;
2. `obs[55:69]` equals zero for `t<3`, else `final_action[t-3]`;
3. `obs[69:83]` equals zero for `t<4`, else `final_action[t-4]`;
4. `previous_action_in[t]` equals zero at `t=0`, else
   `final_action[t-1]`;
5. corrected builder output matches the committed observation map;
6. package smoke passes on CPU; and
7. all frozen identities above match their pre-correction hashes.

Any identity or semantic failure yields
`INVALID_WINNER_V2_ACTION_HISTORY_CORRECTION`. A complete pass yields
`PASS_WINNER_V2_ACTION_HISTORY_SEMANTICS_CORRECTED`.

## Authority

This correction may unblock continued offline runtime-v2 review only. It does
not decide the separately held recursive cross-CPU tolerance, complete runtime
acceptance, real-build COM, Gate 5, deployment, robot/RDK-X5 access, torque,
motors, training, hosted compute, GPU/iGPU use, or robot clearance.
