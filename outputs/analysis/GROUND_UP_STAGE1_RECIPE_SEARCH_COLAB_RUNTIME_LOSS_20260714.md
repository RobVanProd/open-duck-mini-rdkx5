# Ground-Up Stage-One Search Colab Runtime Loss

status: `RECOVERED_COMPLETED_EVIDENCE_RESUME_UNFINISHED_ONLY`

The first broad-rung Colab session completed and independently archived
`S1LR_LO`, `S1LR_HI`, and `S1ENT_LO`. Each artifact was downloaded, matched its
remote SHA-256, and received the frozen 6M/8M CPU evaluation.

After the runner announced the start of `S1ENT_HI`, Colab session metadata
continued to report `BUSY`, but the file API consistently reported that
`/content` did not exist. No `S1ENT_HI` artifact or checkpoint was recovered,
so it has no result and cannot be ranked. The inconsistent session was stopped;
`colab sessions` then reported no active sessions. The blocked local CLI process
was terminated after the remote stop.

A frozen resume matrix contains only `S1ENT_HI`, `S1IMIT_LO`, and `S1IMIT_HI`.
The three completed candidates are explicitly excluded so compute is not spent
rerunning valid evidence. All recipe values, seed, horizon, patches, and gates
remain identical to the original preregistration.

This is an infrastructure interruption, not policy evidence. It does not
authorize RDK-X5 or robot access.

## Second runtime loss

The first resume session subsequently completed and archived `S1ENT_HI` and
`S1IMIT_LO`; both artifacts were downloaded, hash-verified, and evaluated. It
then lost `/content` while `S1IMIT_HI` was between its 2M and 4M checkpoints,
again while session metadata still reported `BUSY`. No high-imitation artifact
was recovered, so that partial attempt has no rankable result. The session was
stopped and the local CLI process was terminated.

A final one-candidate resume matrix contains only `S1IMIT_HI`. This avoids
rerunning any of the five completed variants and keeps the final attempt well
inside the observed hosted-runtime lifetime.
