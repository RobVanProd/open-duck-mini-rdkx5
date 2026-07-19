# Real-Build Torso-COM Direct-Reaction Contract

Status: `PASS_DIRECT_REACTION_CALCULATOR_CONTRACT_HOLD_PHYSICAL_INPUTS`

Formal physical measurements read: `0`.

Blank template: `HOLD_REAL_BUILD_DIRECT_COM_INPUTS_INCOMPLETE` with `30` missing/invalid fields and no numerical estimate.

## Checks

- `preregistration_status_exact`: `PASS`
- `zero_formal_physical_measurements_in_preregistration`: `PASS`
- `urdf_hash_exact`: `PASS`
- `sim_xml_hash_exact`: `PASS`
- `break_radius_hash_exact`: `PASS`
- `formal_result_absent`: `PASS`
- `python_compile_passes`: `PASS`
- `eight_cpu_unit_cases_pass`: `PASS`
- `blank_template_holds_incomplete`: `PASS`
- `blank_template_reports_no_numerical_estimate`: `PASS`
- `blank_template_authority_all_false`: `PASS`
- `datum_locked_to_minus_0p019`: `PASS`
- `exactly_three_formal_trial_slots`: `PASS`
- `zero_robot_rdk_gpu_actions`: `PASS`

A pass validates only the calculator and blank measurement route. It authorizes no
physical measurement by the agent, robot/RDK-X5 access, Gate 5, deployment, torque,
motors, training, hosted compute, GPU/iGPU use, or robot clearance.
