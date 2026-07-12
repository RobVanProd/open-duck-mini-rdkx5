# Rate165 Hard-Vector Runtime Approval Packet

status: `READY_FOR_SEPARATE_STAGE_APPROVAL`

## Evidence basis

- fixed-target actuator model cross-validates across P30/P31-34
- penalty BC rejected twice; penalty PPO rejected at all checkpoints
- exact projection passes x=.08 `8/8` and x=0 `8/8`
- projected x=.08: vx `0.0291`, ratio `0.3635`, single support `22.93%`,
  p95/max velocity excess `0/0`
- projected x=0: still, max pitch-chain p95 `0.0642 rad/s`

## Default-off runtime candidate

The rate165 ONNX, offsets, gains, phase timing, action scale, bus read order,
and EEPROM remain unchanged. The only candidate is a 14-value target slew
vector:

`5.24,5.24,1.50,1.50,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25`

Omitting the new argument preserves the prior scalar `5.24 rad/s` runtime.
Invalid vectors fail before HWI construction.

Local artifact hashes:

- walker: `e282f927c17bfc1c6c9fc9d958a597e2f8c1cf8733962ada3a44593a008632c5`
- parser: `dd139f1b7043a4ddbe64e5242ab8316e5a6216a6dbe2d4347a5f4c6eb3204eee`
- diagnostic: `49f4074e0f1bbfa8749a5e1af398570eab0e70d40963ba40551499b38429493b`
- rate165 ONNX remains `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`

## Required physical gates

1. Separate approval: stage the three code files only, with no HWI import or
   motor initialization; capture fresh snapshot and verify hashes/idle port.
2. Separate approval: suspended x=0 for 15 s with the exact vector, automatic
   torque-off, unchanged analyzer, and visual symmetry review.
3. Only if x=0 passes, separate approval: suspended x=.08 once for 15 s.
4. Stop. Grounded replay remains blocked unless separately reviewed after the
   numeric and visual suspended gate.

Abort on unexpected motion, wrong side/sign, jerk, asymmetry, timing overrun,
CRC/write burst, tracking spike, or operator concern. No current approval to
stage, deploy, initialize HWI, or move motors is inferred from offline results.

## Stage runner readiness

`scripts/stage_rate165_hard_vector_runtime.sh` is syntax-checked and
refusal-tested. It requires `--run`, `--i-approve-stage-only`, a fresh snapshot,
the exact local/live hashes, an idle runtime, and an unowned serial port. It
copies only into a side-by-side stage directory and verifies the result. It
cannot replace live files, import HWI, open serial, enable torque, or run a
motor command.
