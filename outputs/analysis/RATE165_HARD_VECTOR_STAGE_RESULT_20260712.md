# Rate165 Hard-Vector Side-by-Side Stage Result

status: `PASS_STAGE_ONLY`

The explicitly approved stage-only deployment completed on 2026-07-12. The
first attempt stopped during preflight because of local shell quoting and
copied nothing. The quoting defect was corrected, syntax checked, and the same
approved stage was rerun.

Verified staged files in
`/home/sunrise/rate165_hard_vector_stage_20260712`:

- walker: `e282f927c17bfc1c6c9fc9d958a597e2f8c1cf8733962ada3a44593a008632c5`
- parser: `dd139f1b7043a4ddbe64e5242ab8316e5a6216a6dbe2d4347a5f4c6eb3204eee`
- diagnostic: `49f4074e0f1bbfa8749a5e1af398570eab0e70d40963ba40551499b38429493b`

Post-stage live files remain unchanged:

- live walker: `b9732bfa1deca5d6a7a062f757589a6327c7b000d0d855f56eec500535c25c17`
- live diagnostic: `f284332c543af360cc73931ac646a5198de4bc58ad27ad18681fb326a1b937c2`

The postcheck found no runtime process and no `/dev/ttyACM0` owner. HWI was not
imported or initialized; torque and motors were not engaged. No policy replay
occurred.

The next gate is a separately approved backup-backed live installation with no
HWI or movement. Suspended x=0 remains a later separate approval.

