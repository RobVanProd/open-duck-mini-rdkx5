# Ground-Up Progress-Conditioned Survival Result

status: `NO_PROGRESS_CONDITIONED_SURVIVAL_WINNER`

## Decision

`O2_PROGRESS_CONDITIONED_SURVIVAL` does not advance. It ties the protected O1
control on every frozen ranking field and fails the preregistered all-run gate.

| candidate | moving passes | persistent moving seeds | hard failures | full checkpoint passes | decision |
|---|---:|---:|---:|---:|---|
| `O1_SIGNED_PROGRESS` | 2/8 | 1 | 6 | 0/2 | protected control; no advance |
| `O2_PROGRESS_CONDITIONED_SURVIVAL` | 2/8 | 1 | 6 | 0/2 | eliminate |

O2 passed only x=`0.074`, seed `100` at both 3,010,560 and 4,014,080.
Seed `101` collapsed at x=`0.074` and x=`0.08` at both checkpoints. Both
x=`0.08`, seed `100` runs completed with no positive displacement and a
constant saturated action vector. The x=`0.08` traces reproduce O1's failed
values, so the new reward conditioning did not alter that failure mode.

## Frozen causal comparison

O2 retained O1 signed linear progress and changed only one structural
mechanism for positive commands: the existing alive and yaw-tracking rewards
were multiplied by `clip(body_local_vx / abs(command_x), 0, 1)`. Their scales
remained `20` and `6`; x=0 behavior remained canonical. All other reward terms,
total clipping, architecture, PPO values, phase, reset, command, and horizon
were unchanged.

## Artifact record

- archive SHA-256:
  `5591b1775b3d6bc56560343726be13ffd88a79631c20746e2434ffda09478679`;
- 3M policy SHA-256:
  `2ed8eca1ac1df24f61136e8caa668d32dcd5fbce3bfacf5ae8cf4fe194721118`;
- 4M policy SHA-256:
  `969382d1f82bdaef5bb2e3d1ce14f95f5a6450a437bdb78383a722340e73881e`;
- training seconds: `999.319271011`;
- hosted-job seconds: `1049.442961685`;
- command-conditioned-survival patch SHA-256:
  `b00d78a3a7c6f15562cdb14ccfd9129ce0001845bbbca8c343965f98a054dc7f`.

The archive and every ONNX export were downloaded and hash-verified. The T4
session was terminated before behavior evaluation; Colab reported zero active
sessions.

## Interpretation and next boundary

The completed scalar, architecture, bootstrap, signed-progress, and
progress-conditioned-survival screens have not produced a nominal gait winner.
Per preregistration, do not tune the O2 gate, scales, command, phase, or horizon.
Close this reward-objective family.

The next authorized work is a read-only audit of a materially different
reference-learning formulation: determine whether the supplied reference
motion can provide a deterministic action/observation teacher for supervised
policy initialization before PPO, rather than acting only through an imitation
reward. No accelerator run is authorized until the teacher target, observation
contract, actuator semantics, causal control, and frozen stop rule are measured
and preregistered.

No policy, Stage-2 continuation, baseline comparison, offline clearance, RDK
runtime work, deployment, or robot validation is authorized. Training reward
was excluded. Evaluation used local CPU only; no local GPU, iGPU, onboard GPU,
RDK-X5, robot, motor, or torque access occurred.
