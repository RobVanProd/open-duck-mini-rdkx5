# Ground-Up Robustness R2 Torso-Body Index Correction

status: `INVALIDATE_FIRST_TORSO_COM_X_NEG_RESULT_AND_RERUN`

## Evidence

- The compiled MuJoCo model identifies body 1 as `base`, with mass `0.0 kg`.
- The intended inertial torso is body 2, `trunk_assembly`, with mass `0.698526 kg`.
- The first implementation mutated `body_ipos[1]`. Its 16 condition-7 traces are byte-for-byte identical to the 16 default-armature traces. The resulting formal pass is invalid evidence and does not authorize condition 8.
- The evaluator now resolves `trunk_assembly` by name, rejects invalid or massless torso targets, and records body name, body ID, and mass in each readback.
- The corrected contract requires both exact body identity and a paired rollout whose simulated dynamics change under the COM shift.

## Corrected contract

- Contract status: `PASS_ROBUSTNESS_R2_EVALUATOR_CONTRACT`
- Named torso: `trunk_assembly`
- Compiled body ID: `2`
- Compiled torso mass: `0.698526 kg`
- Requested X endpoint readback: `-0.0483259 -> -0.0983259 m`
- Named massive-body check: `True`
- COM dynamics-sensitivity check: `True`
- Default-off 600-tick reproduction: `True`
- CPU-only check: `True`

Only an identical rerun of `TORSO_COM_X_NEG` is authorized. No condition 8+, R3+, training, Colab, local GPU, RDK-X5, or robot access is authorized.
