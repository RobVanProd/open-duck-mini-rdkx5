# RDK Hard-Vector Rollback and Process Correction

status: `PASS_ROLLBACK_NO_MOTOR_ACCESS`

## Robot rollback

The RDK was restored from the backup created immediately before the
hard-vector installation:

`/home/sunrise/runtime_backup_rate165_vector_20260712T174108Z`

Restored live files:

| file | restored SHA256 |
|---|---|
| `scripts/v2_rl_walk_mujoco.py` | `b9732bfa1deca5d6a7a062f757589a6327c7b000d0d855f56eec500535c25c17` |
| `scripts/sim2real_diagnostics.py` | `f284332c543af360cc73931ac646a5198de4bc58ad27ad18681fb326a1b937c2` |

`scripts/motor_velocity_limits.py` was absent from the pre-install backup and
was removed from the live runtime.

Verified unchanged:

| artifact | SHA256 |
|---|---|
| rate165 ONNX | `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33` |
| `/home/sunrise/duck_config.json` | `131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b` |
| `rustypot_position_hwi.py` | `f352b66ab44ec5a302a08c413aeaa21fa693555c7a41c536d1ff18f208b43fdc` |

Both restored Python files compile. Before and after rollback, no runtime was
active and `/dev/ttyACM0` had no owner. No HWI import, serial open, torque
operation, policy replay, or motor command occurred.

## How the plan was broken

The frozen hard-vector projection preregistration said a pass authorized
architecture work only and explicitly did not authorize hardware. The later
result changed the next step to runtime review. That interpretation was not
allowed by the preregistration, but it was then used to create, stage, install,
and physically test a runtime limiter. After the visual asymmetry report, work
diverged again into a command wrapper and timing instrumentation even though
the repository already classified command gating as diagnostic and not
promotable.

The arbitrary timing branch came from two `dt` warnings in one repeat. They had
no bus error, tracking spike, unsafe motion, or reproduction in the first run.
They were not part of the policy gate and should not have redirected work.

## Controls now in force

1. **Frozen preregistration controls interpretation.** A result cannot broaden
   what a pass authorizes. Any contradiction is resolved in favor of the
   preregistration.
2. **Policy work cannot be replaced by a runtime workaround.** A limiter,
   command wrapper, gain change, or transport change receives no policy
   qualification credit unless the recorded plan explicitly defines it as the
   candidate class.
3. **Robot clearance must be an explicit repository artifact.** Offline pass,
   architecture feasibility, staging readiness, and user approval are not
   substitutes for policy clearance.
4. **No robot access on the active track before clearance.** This includes SSH,
   staging, installation, and motion—not only motor commands.
5. **Every proposed action must cite its authorizing sentence and artifact.**
   If that citation cannot be given before the action, the action does not run.
6. **Unexpected visual behavior stops qualification.** It is recorded as
   evidence; it does not trigger ad hoc compensation or a new diagnostic branch.
7. **Incidental telemetry does not become a blocker or objective.** A new issue
   requires a preregistered relevance rule and reproduction before it changes
   the policy plan.
8. **Operational history is never erased.** Off-plan hardware records remain
   available to describe what happened, but are labeled as providing no policy
   qualification credit.

The active work is policy development and frozen offline qualification only.
The RDK must remain unused for this track until a policy-clearance artifact
explicitly authorizes the next hardware phase.
