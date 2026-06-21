# Roboticist Playbook

This playbook adapts useful ideas from RHO and HELIX to this specific Open Duck Mini sim-to-real bridge.

RHO's core lesson for this project is not to put an LLM in the live robot loop. It is to move expensive search and debugging out of deployment, keep the shipped artifact as readable code, and accept changes through evaluation gates.

References:

- RHO project page: https://rho-robotics.github.io/
- HELIX repository: https://github.com/KE7/HELIX

## Principles To Adopt

### 1. Frozen Code At Deployment

The robot should run a known, inspectable runtime and policy. Do not let an agent generate or revise control code while the robot is walking.

For this repo:

- Live robot code is captured under `runtime/`.
- Additive diagnostics live under `instrumentation/`.
- Behavior changes require reviewed PRs.
- Deployment should use explicit commands and backups.

### 2. Repository As The Candidate

RHO and HELIX treat the whole codebase as the thing being improved, not a single magic prompt or isolated function.

For this repo, the candidate state includes:

- RDK runtime files.
- Board config snapshots.
- Policy hash and ONNX contract.
- Telemetry schema.
- Analyzer tools.
- Evidence summaries.
- Safety and deployment docs.

If one of those changes, update the docs and evidence trail.

### 3. Evidence Gates Before Acceptance

RHO keeps candidates only after evaluation gates. This project uses hardware-safe diagnostic gates instead of blind trial-and-error.

Current gates:

1. Config snapshot.
2. Home pose observation truth.
3. IMU tilt axis/sign mapping.
4. Foot contact polarity.
5. Joint identity and home pose verification.
6. Suspended policy replay.
7. Grounded replay only after low-risk gates pass.

Do not accept a fix because it sounds plausible. Accept it because a failed gate improved and no earlier gate regressed.

### 4. No Robot Search Without A Harness

RHO can run many candidates because the evaluation environment is isolated. The real Duck is not that environment.

For this repo:

- Use simulation, analysis tools, and non-moving logs for iteration.
- Run moving tests only with Rob present and explicit approval.
- Keep movement amplitudes small.
- Do not run repeated exploratory walking attempts as "search."

### 5. Keep A Decision Trail

HELIX emphasizes state, lineage, and evaluation logs. This project needs the same discipline in a lighter form.

For every meaningful result, record:

- evidence file path
- command or test mode
- key metric
- pass/fail decision
- next gate or patch recommendation

Use:

- `docs/EVIDENCE_FLOW.md`
- `docs/EVIDENCE_MANIFEST.md`
- `SIM2REAL_RESULTS_SUMMARY.md` when logs are collected
- PR descriptions

## Project-Specific Roboticist Checklist

### Observation Contract

Before blaming policy quality, verify:

- gyro units and sign
- accelerometer axis order and sign
- upright gravity vector
- command vector ordering
- joint position error ordering
- joint velocity scaling
- action history values
- motor target history
- foot contact polarity
- gait phase values

### Action Contract

Before changing gains or training, verify:

- action index to joint name
- joint name to servo ID
- command units
- home pose
- live offset compensation
- software sign convention
- physical positive direction
- target-vs-actual tracking

### Timing Contract

Before changing phase timing, verify:

- control dt
- inference frequency
- IMU update frequency
- servo read/write reliability
- skipped ticks
- dt jitter under logging

### Contact And Dynamics

Only after observation/action/timing contracts pass, investigate:

- foot contact sensor reliability
- foot slip
- toe catches
- actuator lag under load
- COM and shell mass
- TPU/contact friction
- sim contact parameters

## How Future Fixes Should Work

Each fix should be a small branch:

```text
failed gate -> one hypothesis -> one minimal patch -> rerun same gate -> compare metric
```

Examples:

- If IMU upright accel is on the wrong axis, patch IMU remap and rerun home pose plus IMU tilt.
- If left knee readback is wrong at home, patch calibration or mechanical setup and rerun home pose plus joint identity.
- If bus errors appear while stationary, patch bus reliability and rerun home pose before policy replay.

Do not combine IMU, offsets, gains, phase, and contact changes in one branch.

## Documentation Freshness Rule

When any of these change, update docs in the same PR:

- board IP or access method
- runtime path
- policy file or hash
- `duck_config.json`
- IMU calibration status
- telemetry schema
- diagnostic command
- test order
- current next gate
- root-cause ranking

If the docs are stale, the robot state is stale.
