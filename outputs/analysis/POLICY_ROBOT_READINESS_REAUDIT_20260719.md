# Policy Robot-Readiness Re-audit

Status: `HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`

Decision: `MEASURE_BUILD_SPECIFIC_MASS_AND_X_PLACEMENT`

Robot clearance: `NO`

## Question

Does the current artifact record establish that the protected composite policy
is ready to run on Rob's assembled robot?

## Evidence rechecked

The 2026-07-19 re-audit used policy source HEAD `c86c3c9` on branch
`codex/torso-com-decode-probe`. It did not access the robot, RDK-X5, a GPU,
an iGPU, hosted compute, or the separate native-runtime working repository.

The protected `G1_EXACT_BOUNDARY/T2_EQUAL` composite remains the persistent
offline nominal winner. Both checkpoints pass the complete measured-actuator
R1 matrix. The P30 observer also passes the frozen 32-cell observer-by-plant
cross-fit at worst tracking p95 0.183170038 rad and minimum moving mean
velocity 0.084084972 m/s, with zero rate or actuator-envelope excess.

The policy's deployment-specific signed torso-COM curve remains sharply
asymmetric. After the preregistered one-step margin, an as-built sim-to-real
torso-COM error interval must fit completely inside:

- lower bound: -0.021875 m;
- upper bound: +0.0046875 m.

The frozen calculator was rerun against the committed untouched physical
measurement template. It reports exactly 46 missing or invalid fields,
`numerical_estimate_reported=false`, and no estimate object. All five CPU unit
contract cases pass. A workspace search found no later source-backed as-built
mass, placement, datum, or uncertainty evidence that can populate those
fields.

## Decision

The policy is an offline hardware candidate, not a robot-cleared policy. The
missing evidence is physical, not another policy hyperparameter: the assembled
torso's build-specific mass/X ledger and frame mapping have not been measured.
No nominal web weight, stock Pi geometry, Frank Fu software article, image
scale inference, or unmeasured point estimate may replace it.

Populate `real_build_torso_com_measurement_template.json` from the powered-off
physical build, then rerun the frozen calculator. A passing COM comparison may
close only this model-specific policy question; it does not itself authorize
motor engagement or a deployment run. An outside result selects a separately
preregistered simulator torso-model correction and frozen offline re-gate.

## Frozen evidence hashes

- break-radius result:
  `6b84b34e7280b0f0d92109a70444d18af7b0196cd3555530b8f42e70dea54e32`;
- measurement template:
  `d9abf072ec2e9123f5214c8678860a7e043e83d4fd6a0400f49c98e2f6f21137`;
- measurement calculator:
  `6c43b34a4fb1ffb9f9d84619e1c5c53d7812ecda0050e76bf4d98505b90a213a`;
- winner-v2 observer cross-fit result:
  `804165bd1fdf45fdb1ab8369617e460d65de60a9f6f0ced90337429b56162231`;
- winner-v2 P30 observer pin:
  `6b8587ef86759c2c3918ad34ff0898203170fe57277f644fdf5fc96a687567c3`.

No training reward was used. No threshold, policy, transform, fit, command,
reset, horizon, actuator model, or authority boundary changed.
