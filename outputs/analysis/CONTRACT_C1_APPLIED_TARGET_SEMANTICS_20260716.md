# C1 Applied-Target Slot Semantics

Status: `MISMATCH_TRAINING_APPLIED_VS_RUNTIME_SENT_TARGET`

## Training contract

The enabled training observation patch selects
`ground_up_actuator_bridge_applied_targets`, not `motor_targets`, for actor and
critic indices 83:97 (`patches/ground_up_applied_target_observation.patch`,
lines 11-21). The bridge implementation constructs that value from the delayed
target, the previous bridge output, first-order lag, and a per-joint velocity
clip (`tools/prepare_training_actuator_wrapper_patch.py`, lines 114-138).

Therefore the slot means: **the bridge's realized delayed/lagged/velocity-
limited plant target from the preceding transition**. It is not merely the
slew-limited commanded/sent target.

## Native runtime contract

The runtime observation concatenates `self.motor_targets` at indices 83:97
(`runtime/scripts/v2_rl_walk_mujoco.py`, lines 362-375). At the beginning of a
tick this is the prior tick's sent target. The runtime then computes a new
target, clips it against `self.prev_motor_targets`, optionally filters it,
copies it into `prev_motor_targets`, applies the head overlay, and sends it
(`runtime/scripts/v2_rl_walk_mujoco.py`, lines 526-558). There is no modeled
delay/lag bridge output in this loop.

Therefore native "previous motor target" means: **the prior slew-limited sent
target, including the prior head overlay**. This matches the legacy 101-D
sent-target contract, but it does not match the applied-target training arm.

## Decision

The semantics do not match exactly. A runtime intended to execute an
applied-target-state policy would need a separately reviewed contract defining
how an online applied/realized actuator target is obtained. Options include a
validated actuator-state estimator or a runtime bridge state proven equivalent
to the training bridge. Re-labeling the existing sent target as "applied" is
not acceptable.

Per the C1 stop rule, this artifact flags the mismatch for review and does not
edit the frozen runtime contract. Robot and Gate 5 readiness remain blocked.

