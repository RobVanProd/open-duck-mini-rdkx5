# Ground-Up Torso-COM Matched Accelerometer-Map Contract

status: `PASS_TORSO_COM_MATCHED_ACCELEROMETER_CONTRACT`

The frozen CPU-only contract passes every check. It executed zero formal sensor
cells, zero dynamic steps, and zero actor calls.

- Exact source traces/states: 36/144.
- JAX device: `TFRT_CPU_0` only.
- Sensor: name `accelerometer`, ID 2, address 6, dimension 3, attached to site
  `imu`.
- All source `qpos`, `qvel`, controls, and 115-D observations have exact schemas
  and finite values.
- COM branches mutate only `trunk_assembly` `body_ipos[2,0]` by -.05/+ .05 m;
  the nominal model remains unchanged.
- Preregistration, crossed result, signed result, evaluator, trace, model,
  scene, reference, fit, and graph sources are hash locked.

The contracted tool SHA-256 is
`de5dfe61c939d68d962f134449722fb3e1400b75bef1f16c35948768e9f4c08b`.
Only that exact tool may read the 144 frozen static sensor cells. The formal
result remains invalid unless native nominal readback and the tick-zero frozen
direction both pass their preregistered 1e-3 m/s^2 tolerances.

This authorizes no dynamic simulator step, actor fork, training, Colab,
GPU/iGPU, RDK-X5, runtime, or robot work.

Machine-readable record:
`ground_up_torso_com_matched_accelerometer_contract.json`.
