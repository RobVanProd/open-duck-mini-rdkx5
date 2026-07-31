# Winner-v41 first-attempt failure receipt

- Status: `INVALID_WINNER_V41_FIRST_ATTEMPT_NO_RESULT`
- GitHub run: `29901924055`, attempt `1`
- Head: `cd89be92cdd3b669cdb8ec5a50486dcc65484ca8`
- Artifact count: `0`
- Candidate / plant cells executed: `0 / 0`

The runner passed its tests, frozen source manifest, and environment preparation,
then failed while expanding the first three-coordinate static target. It called
the Winner-v38 block-sequence helper with shape `(1,3)` although that helper is
frozen to accept exactly four blocks `(4,3)`. No candidate reached MuJoCo and no
result JSON existed to classify.

The only admissible correction is a versioned wrapper that replaces this helper
call with the same reviewed `3 -> 6 -> 14` mirror-matrix multiplication. It may
not alter the 729 coordinates, plant pair, 250-tick gate, selection rule, target
semantics, action boundary, or authority. The failed workflow is not rerun.
