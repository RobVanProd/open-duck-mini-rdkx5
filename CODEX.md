# Codex Notes

Use `AGENTS.md` as the authoritative instruction file for coding agents working
in this repository.

Current project mission:

```text
Build a robust reference-motion walking policy for Open Duck Mini through
frozen, evidence-selected offline gates. Do not substitute training reward,
visual preference, or robot improvisation for preregistered behavior evidence.
```

Current next step:

```text
The G1/T2 composite remains the first persistent full-horizon nominal/R1
winner, and the selected 512K graph plus P30 observer retain their completed
offline asset freeze. That graph is not robot-ready under the current product
requirement: its verified X-COM failure bracket lies well inside the required
[-.05,+.05] m supported-configuration range. Do not emit a passing runtime
envelope for it and do not waive the failure with per-unit COM measurement.

The powered-off direct-COM packet is superseded as an advancement requirement.
The policy-side CPU audit now passes
PASS_VARIABLE_CONFIGURATION_DOMAIN_BASIS_CURRENT_CANDIDATE_HELD. It derives
the prospective replacement domain from the frozen R2 evidence and compiled
trunk_assembly model: X/Y/Z COM each +/-.05 m; torso mass
.5286734-.8683786 kg (scale .7568414-1.2431586); and evidence-derived principal
inertia scales with positive-definite, triangle-valid coupled sampling.
Optional non-locomotion configurations are represented by aggregate dynamics,
not operator-entered component inventories.

The replacement study is now prospectively frozen before new candidate
outcomes. Its single candidate is R64_ZERO_INIT_RECURRENT_ADAPTER: restore the
protected T2_EQUAL 512K PPO checkpoint, add a 64-state recurrent adapter with
an exactly zero action head so step-zero actions preserve the base, then allow
the base actor and adapter to train together without oracle/configuration
inputs. Reward, privileged critic, commands and the baked hard-vector,
actual-centered guard, conservative envelope and x=0 deadband remain fixed.

The CPU contract now passes. It proves exact CPU remap/restore, 64/64 bit-exact
step-zero actor logits, evolving recurrent state, finite 1,024-step updates to
the protected base and both adapter families, zero initial ONNX action/hidden
error, the exact three-input/three-output ABI, and a finite 256-tick state
chain. Its initial one-check hold was a stale sibling-checkpoint count literal;
a committed read-only audit corrected it to the protected 512K source count
without rerunning the smoke.

The coupled configuration/actuator/sensor curriculum implementation is now
hash-frozen before outcome work. It targets named inertial body 2, represents
the full torso inertia tensor through principal inertia plus inertial-frame
quaternion, uses one all-link mass scale, crosses the measured P30/P31-34
actuator interval with fixed episode delays/noise/native quantization, records
exact per-model and per-episode readback, and exposes no true configuration
field to the actor. Its development checker passed bit-exact residual-off
behavior plus 4,096 model and episode samples at each of 0/25/50/100% scale;
formal PPO steps and behavior cells remain zero.

Next, compose fresh independent baseline and winner-v3 trees from the pinned
control commit and run the hash-locked formal CPU implementation contract. Only
a formal pass may start the single seed-100 no-retry CPU curriculum. Preserve
the preregistered 25%/50%/100% schedule and export only the two full-domain
checkpoints at 1,003,520 and 2,007,040 relative steps. After its artifact
contract passes, run the exact 1,024-cell CPU matrix. Both checkpoints must pass
nominal, 24 fixed anchors, 16 discovery coupled samples, 16 independent heldout
samples and six sensor/transport conditions under both actuator plants and
x=0/.074/.077/.080. No closest result advances.

Only a complete pass may begin the selected-policy commit, later clearance
artifact commit, and still-later supported_configuration_envelope.v2 commit
under the runtime Git-ancestry contract. Physical calibration may compare with
that envelope but may never widen it.

There is currently no passed supported-configuration envelope. Runtime's
pending sentinels must remain. No robot, RDK-X5, serial, torque, motion,
automatic calibration, X5 preflight, Gate 5, deployment, local GPU/iGPU,
hosted training, or robot clearance is authorized by the preregistration.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live
robot loop, preserve frozen inspectable deployment code, and accept changes
only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current
with the latest robot state. Do not let important state live only in chat.
```
