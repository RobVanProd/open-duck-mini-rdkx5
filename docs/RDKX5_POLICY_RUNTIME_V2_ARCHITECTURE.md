# RDK-X5 Policy Runtime V2 Architecture

status: `DESIGN_FROZEN_FOR_GROUND_UP_SEARCH`

## Policy ABIs

ABI v1 baseline:

`obs[1,101] -> final_action[1,14]`

ABI v2 reference-conditioned feed-forward:

`obs[1,101], projected_reference_action[1,14] -> final_action[1,14]`

ABI v2 recurrent:

`obs[1,101], projected_reference_action[1,14], state_in[1,N] -> final_action[1,14], state_out[1,N]`

The policy always returns final normalized actions. The RDK never blends,
gates, scales, limits, or otherwise reinterprets policy output as part of
policy qualification.

## Reference feature

The reference generator is a versioned input feature. It uses the frozen
polynomial reference, command, phase, home pose, action scale, and measured
per-joint velocity envelope to produce a projected 14-action feature. Simulator
and RDK implementations must pass hash and numeric equivalence tests over the
complete command grid and all 27 phases.

At zero locomotion command, the projected locomotion reference is zero. Head
commands remain explicit canonical observation fields.

## Runtime components

1. `transport`: sole serial owner; deterministic ID13-last reads, CRC checking,
   bounded retries, counters, and explicit fault returns.
2. `sensors`: validates complete position/velocity/IMU/contact frames and never
   silently substitutes stale partial data.
3. `observation`: constructs the canonical versioned 101-vector.
4. `reference`: constructs the ABI-v2 projected reference feature.
5. `policy`: validates manifest, hashes, tensor names/shapes/dtypes, state size,
   and inference deadline before arming.
6. `control`: monotonic fixed-period loop; sends final policy actions unchanged
   through canonical home/action conversion.
7. `supervisor`: `OFF -> SELF_TEST -> READY -> ARMED -> ACTIVE -> FAULT`; only
   this component can enable torque.
8. `telemetry`: bounded queue outside the control deadline; dropped logs are
   counted and never block control.

## Safety and deployment

- Every build carries source, dependency, policy, reference, config, and ABI
  hashes in one manifest.
- Startup runs transport, joint-map, observation, reference, ONNX, timing, and
  torque-off self-tests before `READY`.
- Any incomplete sensor frame, persistent CRC failure, missed deadline,
  non-finite tensor, ABI mismatch, or supervisor heartbeat loss enters `FAULT`
  and disables torque.
- Deployment is side-by-side and atomic with a verified previous-version
  rollback. Runtime files are never assembled ad hoc over SSH.
- Production has one serial owner and one policy instance.

This defines the software target. It does not authorize RDK access, deployment,
or motor tests.
