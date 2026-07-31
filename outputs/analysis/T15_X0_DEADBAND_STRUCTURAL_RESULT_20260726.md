# T15 x=0 deadband structural audit result

- Status: `PASS_T15_X0_DEADBAND_STRUCTURAL_CONTRADICTION`
- Decision: `REOPEN_X0_BRANCH_FOR_CONFIGURATION_AWARE_SUPPORT_RETENTION`
- T6 x=0 cells / unique behavior signatures: `16` / `1`
- T7 negative-COM universal-support passes: `4/4`
- New behavior cells / optimizer steps: `0 / 0`
- Hosted compute / robot access: `0 / 0`
- Result SHA-256: `3aa9368cbc668d4720754a45b2cc71093d370c40538035826b1c00a36dd83889`

The negative-COM x=0 failure is invariant to policy family, checkpoint, and actuator fit because the unconditional deadband forces exact-zero action. The already-reviewed universal support action holds the same negative-COM condition. Therefore the x=0 clearance failure is caused by the branch contract, not by a missing optimizer objective.
