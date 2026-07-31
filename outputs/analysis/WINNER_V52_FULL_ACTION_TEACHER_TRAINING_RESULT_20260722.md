# Winner-v52 full-action-teacher training result

- Status: `PASS_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT`
- Decision: `AUTHORIZE_FULL_ACTION_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY`
- Result SHA-256: `a964b30f7a9958a7f6ed6db209fa11da8a36a118e59ffbbf2956a67d38b208b3`
- Environment: exact Python `3.12.13`; JAX backend `cpu`
- Elapsed time: `3881.954000000027 s`
- Optimizer updates: `100` (`354` through `453`)
- Scheduled episode slots: `2,000,000`
- Formal support cells / robot or RDK access: `0 / 0`

## Contract result

All `22` result checks pass. The arm produced exactly `100` atomic snapshots,
used exactly `22` frozen configuration/plant teacher rows on every update,
excluded every held-out teacher label, kept every update finite, changed all
`12` trainable leaves cumulatively, preserved all frozen leaves, and retained
the exact action-boundary, transition, objective, hidden-replay, and snapshot
contracts.

The full-action teacher loss is evidence about the completed training arm, not
a checkpoint-selection metric. It was `0.0034417707938700914` at the frozen
half checkpoint and `0.0033936197869479656` at the frozen final checkpoint.
Neither checkpoint is selected by this result.

## Persistent artifacts

| label | update | snapshot SHA-256 | ONNX SHA-256 | JAX/ONNX max error |
|---|---:|---|---|---:|
| half | 403 | `c639b3137841f15e19c1d72c4a7be13b4afe0999800b8af7e4b096f539077a36` | `9bd297d6c1bdd4dc49801596bee12741838e8519bad9c55a98307405760ca23d` | `5.820766091346741e-11` |
| final | 453 | `b7bfd05bb8af7a1085b91495d62273f238c71fbea6e1d9c6dbd64604ff4b7b60` | `b710e8c1578d5cd7261646daa54e3b8c8565c5a84fbf9f40fcfe5e86b53b618b` | `8.731149137020111e-11` |

Both graphs expose the exact stateful ABI:

```text
obs[1,115] + previous_action[1,14] + h_in[1,64]
  -> calibration_actions[1,14] + previous_action_out[1,14] + h_out[1,64]
```

Each graph passed a `250`-tick state chain, emitted finite outputs, reproduced
`previous_action_out == calibration_actions` bit-exactly, and contained no
training-only or privileged tensors.

## Authority

This pass authorizes only a separately preregistered, unchanged half/final
support gate. It selects no checkpoint and grants no robot clearance,
deployment, X5/robot access, serial/GPIO/I2C access, torque, or motion.
