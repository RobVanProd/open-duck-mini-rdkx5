# Ground-Up Torso-COM Full-Observation Replay and Sensitivity Contract

status: `PASS_TORSO_COM_FULL_OBS_STUDY_CONTRACT`

All 15 frozen checks pass with zero simulator behavior cells executed.

- The 36 source matrices, six contracted policy graphs, both actuator fits,
  reference table, transform record, correction record, evaluator, and
  closed-loop evaluator match their preregistered hashes and counts.
- Every matrix preserves the exact policy/fit/reference hashes, four commands,
  seed, deterministic home reset, 600-tick request, and per-run dynamics
  readback. Both COM endpoints numerically change only torso body 2
  `trunk_assembly` X by exactly +/-0.05 m; nominal is exact default-off.
- All six ONNX graphs use only `CPUExecutionProvider`, retain the contracted
  `obs[1,115], previous_action[1,14]` interface and two 14-D outputs, and
  produce finite outputs.
- JAX reports CPU only with `CUDA_VISIBLE_DEVICES=""` and
  `JAX_PLATFORMS=cpu`.
- Static source inspection confirms full-observation tracing appends only the
  declared observation/state trace fields. The frozen comparison normalizer
  removes only reporting paths, the full-observation flag, and wall time; its
  refusal fixture preserves and detects a 1e-9 behavior-metric mutation.
- Device, manifest, and torso-readback mutations are refusal-tested.
- The replay and analysis tools were present before this contract. Their exact
  SHA-256 hashes are recorded in the JSON contract and must match at execution.

Decision: `AUTHORIZE_EXACT_144_CELL_CPU_REPORTING_REPLAY`

This pass authorizes only the preregistered full-observation reporting replay,
then the already-frozen decode and identical-state actor forks if all replayed
behavior reproduces exactly. It does not authorize retries after outcomes,
training, Colab, GPU/iGPU, policy or simulator behavior changes, R2/R3,
runtime design, RDK-X5, robot access, deployment, torque, or motors.
