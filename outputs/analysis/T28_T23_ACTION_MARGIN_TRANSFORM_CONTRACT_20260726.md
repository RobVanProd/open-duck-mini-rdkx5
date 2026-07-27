# T28 T23 action-margin transform contract

status: `PASS_T28_T23_ACTION_MARGIN_TRANSFORM_CONTRACT`

- preregistration_hash_exact: `True`
- exactly_two_policies: `True`
- all_policy_contracts_pass: `True`
- both_checkpoints_uniform_limit: `True`
- half_is_interior_on_frozen_samples: `True`
- final_transform_activates_on_frozen_samples: `True`

Both policies use `L=0.9799999595`, strictly below the frozen `0.98` saturation margin.

Passing authorizes only preregistration of the 16-cell CPU floor-friction-0.5 falsifier. It does not authorize training, Gate 5, RDK-X5, robot, torque, or motion.
