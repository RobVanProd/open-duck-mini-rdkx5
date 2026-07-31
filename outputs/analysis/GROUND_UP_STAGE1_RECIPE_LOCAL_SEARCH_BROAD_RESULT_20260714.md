# Ground-Up Stage-One Recipe Local Search Broad Result

status: `NO_BROAD_WINNER_THREE_WAY_TIE`

## Result

All six one-factor variants completed 8,028,160 training steps from seed 100.
Their 6M and 8M checkpoints were evaluated at x=`0.00` and x=`0.08` with
rollout seeds 100 and 101 for 1.08 seconds. The center used its pre-existing,
same-seed checkpoints. Training reward was excluded.

| rank | recipe | hard failures | finite x=0 runs | moving-pass runs | persistent moving seeds | full checkpoint passes |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `S1C` | 0 | 4 | 1 | 0 | 0 |
| 1 | `S1ENT_LO` | 0 | 4 | 1 | 0 | 0 |
| 1 | `S1IMIT_HI` | 0 | 4 | 1 | 0 | 0 |
| 4 | `S1LR_LO` | 0 | 4 | 0 | 0 | 0 |
| 5 | `S1IMIT_LO` | 1 | 4 | 1 | 0 | 0 |
| 6 | `S1ENT_HI` | 1 | 4 | 0 | 0 | 0 |
| 7 | `S1LR_HI` | 2 | 3 | 2 | 1 | 0 |

No recipe passed a full checkpoint. Lowering learning rate removed the only
moving pass. Raising learning rate produced more seed-100 motion but introduced
two falls and did not solve seed 101. Raising entropy and lowering imitation
also introduced falls. Lower entropy and higher imitation tied the center, but
neither improved persistence or the full gate.

## Artifact evidence

| candidate | artifact SHA-256 | training seconds |
|---|---|---:|
| `S1LR_LO` | `48adf00ee5bc2b0ca83ab9191cddd47618861ef34d9a5b780abc78ce4da5eacf` | 1416.415229113 |
| `S1LR_HI` | `d11f90ae7f57dc0ad07703971c7590a0afe6b280d7465828968b1ac1230cf900` | 936.193219022 |
| `S1ENT_LO` | `5bf5bcc64e22cda0f0a0bb325975416ad6a48f9a847ada1f40d55a00f7b1087b` | 933.083859140 |
| `S1ENT_HI` | `4e78f848ca2d227c653033b7421aadccea54168665001373f3d7e1787440c5fd` | 1394.796561624 |
| `S1IMIT_LO` | `ec7e0782e79c40b4e9bfb075f25f6c3ac3fddb8d2aee410aed6c39f4f58cc68a` | 1205.225217164 |
| `S1IMIT_HI` | `ab2e83692668da7dd714de244a849486b884a32470e1931f963a2d06c89857ab` | 1370.002761212 |

Two Colab runtimes lost `/content`; completed per-candidate artifacts had
already been recovered, and unfinished candidates were resumed without
rerunning completed work. All sessions are stopped.

## Decision

The broad rung eliminates `S1LR_LO`, `S1LR_HI`, `S1ENT_HI`, and `S1IMIT_LO`.
It cannot choose among `S1C`, `S1ENT_LO`, and `S1IMIT_HI` without inventing a
tie-break. An equal 10M/12M extension is preregistered separately. This result
is recipe-search evidence only and does not clear a policy, RDK-X5, or robot.

