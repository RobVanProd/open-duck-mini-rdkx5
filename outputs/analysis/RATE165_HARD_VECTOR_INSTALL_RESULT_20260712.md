# Rate165 Hard-Vector Live Installation Result

status: `PASS_LIVE_INSTALL_NO_HWI`

The explicitly approved backup-backed installation completed on 2026-07-12.
The runner's final manifest command had a quoting defect after installation;
the live copy itself had already completed. Installation was not rerun. The
manifest was reconstructed after read-only verification, and the quoting bug
was corrected for future use.

Live hashes:

- walker: `e282f927c17bfc1c6c9fc9d958a597e2f8c1cf8733962ada3a44593a008632c5`
- parser: `dd139f1b7043a4ddbe64e5242ab8316e5a6216a6dbe2d4347a5f4c6eb3204eee`
- diagnostic: `49f4074e0f1bbfa8749a5e1af398570eab0e70d40963ba40551499b38429493b`

Backup directory:
`/home/sunrise/runtime_backup_rate165_vector_20260712T174108Z`

Verified backup hashes:

- walker: `b9732bfa1deca5d6a7a062f757589a6327c7b000d0d855f56eec500535c25c17`
- diagnostic: `f284332c543af360cc73931ac646a5198de4bc58ad27ad18681fb326a1b937c2`

The RDK Python environment compiled all three live files. Postcheck: no runtime
process, no `/dev/ttyACM0` owner, HWI not initialized, torque/motors not
engaged, and no policy replay.

The next gate is separately approved suspended x=0 for 15 seconds. x=.08 and
grounded movement remain unauthorized.

