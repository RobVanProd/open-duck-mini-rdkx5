# Ground-Up Offline Robustness Ladder Preregistration

status: `PREREGISTERED_SEQUENTIAL_CPU_ONLY`

The command-deadband candidate passed both half/final x=0 and nominal gates.
The next work follows the robustness order frozen in the original ground-up
search: measured actuator variation, isolated declared dynamics, isolated
sensor/transport variation, minimum declared pushes, and rough terrain last.

## Evidence controls

- Candidate: guarded/deadband `G1/T2` at steps `512000` and `1024000`.
- Commands: `0`, `.074`, `.077`, `.080`; duration: `600` ticks.
- Both checkpoints must retain every earlier stage. Training reward is never a
  selection metric.
- Held-out seeds are derived mechanically from the committed repair-result
  SHA-256, not selected after looking at behavior.
- A tooling contract is required before every stage. Stop at the first failed
  stage; do not tune a perturbation after seeing its outcome.

## Frozen stages

| stage | isolated question | evidence source |
|---|---|---|
| `R1` | Does the policy survive both independently measured P30 and P31/34 actuator fits? | fixed-target hardware fits |
| `R2` | Does it survive each declared dynamics axis at its frozen endpoints? | pinned `randomize.py` |
| `R3` | Does it survive declared sensor noise and 0/1/2-tick additional delays when tested separately? | pinned `joystick.py` |
| `R4` | Does it recover from the declared minimum `0.1 m/s` push every 5 s? | pinned push config |
| `R5` | Does it retain x=0 and gait on the established first rough rung `z=.002`? | existing repository terrain ladder |
| `R6` | Does it retain both after combining only the independently passed `z=.002` and `.1 m/s` push? | prior two stages |

The current evaluator already supports R1, pushes, and terrain. It deliberately
disables noise and extra action/IMU delay and does not expose isolated dynamics
overrides, so R2/R3 require a separately checked evaluator extension. That
limitation is recorded here rather than silently bypassed.

Passing R6 authorizes only preregistration of an identical-suite comparison
with `BEST_WALK_ONNX_2`. It does not itself establish “more robust,” grant
offline clearance, authorize training or Colab, or permit RDK-X5/robot access.
