# Ground-Up Torso-COM Decode Worktree Isolation

status: `PASS_CLEAN_WORKTREE_ISOLATION`

The source worktree on `codex/live-oracle-dagger-phase-student` contains
pre-existing changes from closed historical workstreams: eight tracked files,
large untracked experiment archives, and local smoke outputs. The tracked
changes include stale Colab/runtime snapshots and unfinished behavior-prior
and Colab transport changes. They are neither validated by nor relevant to a
torso-COM observability probe.

Those files are deliberately preserved in place because silently deleting
them would destroy user evidence, while committing them with the decode probe
would misstate provenance. New work is isolated in the clean linked worktree:

- path: `/home/lsd/robots/open-duck-mini-rdkx5-com-decode`
- branch: `codex/torso-com-decode-probe`
- source commit: `0d34c34`
- source decision commit: `493341c`

The decode branch reads the existing trace corpus without modifying it. It may
commit only its preregistration, probe implementation, contracts, and result
artifacts. No historical dirty file is part of its evidence set.

