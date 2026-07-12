# Ground-Up Control CPU Contract

status: `PASS_GROUND_UP_CONTROL_CPU_CONTRACT`

The detached upstream control commit is
`b9be205ac64488c23504ca42e5ec790337adeec3`. Its reference file matches the
frozen SHA256 `5850c061...7a25`.

The upstream `pyproject.toml` specifies broad minimum versions. The existing
local environment resolved `playground 0.0.3`; environment construction emitted
overflow warnings and the reset/step contract did not complete. This
combination is rejected for the rebuild.

The same pinned source passes a reset plus zero-action step on CPU with:

- Python `3.12.13`
- JAX/JAXLIB `0.8.2/0.8.2`
- Mujoco `3.9.0`
- Playground `0.0.5`
- observation `101`, privileged observation `212`, action `14`
- control period `0.02 s`
- finite post-step observation, reward `0.1319203`, done `0`

No GPU, robot, network, training, or Colab resource was used. These exact
dependency versions are now the control contract for the throughput
calibration. A different accelerator dependency set must pass the same test
before training.
