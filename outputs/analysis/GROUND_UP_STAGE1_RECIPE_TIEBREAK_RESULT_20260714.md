# Ground-Up Stage-One Recipe Tie-Break Result

status: `NO_RECIPE_WINNER`

The equal-window 10,035,200/12,042,240-step tie-break is complete. Training
reward was excluded. All evaluation ran locally on CPU with
`CUDA_VISIBLE_DEVICES=''` and `JAX_PLATFORMS=cpu`.

| rank | recipe | full checkpoint passes | finite x=0 runs | moving passes | persistent moving seeds | hard failures |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `S1ENT_LO` (entropy `0.001`) | 0 | 4 | 0 | 0 | 0 |
| 2 | `S1IMIT_HI` (imitation `2.0`) | 0 | 4 | 0 | 0 | 1 |
| 3 | `S1C` (center) | 0 | 3 | 1 | 0 | 2 |

`S1ENT_LO` is merely the safest non-gait result. At both checkpoints its two
positive-command rollouts fail positive local forward velocity. `S1IMIT_HI`
also has no moving pass and falls at 10,035,200 steps on seed 100. The center's
single moving pass at 12,042,240 steps is not persistent and is preceded by two
hard failures at 10,035,200 steps.

No candidate satisfies the preregistered condition for
`BEST_RECIPE_TESTED`: two consecutive full checkpoint passes reproduced across
training seeds. Retraining these candidates with seed 101 would replicate a
behavior that has not emerged on seed 100, so no recipe is promoted to that
rung.

The preregistered local-search amendment permits a new pre-compute search over
discount and unroll length after the first ring fails persistence. That bounded
second ring is the next scalar-recipe test. If it also fails to produce
persistent gait without hard failures, scalar recipe tuning closes; no
post-hoc combination is synthesized.

This result does not clear a policy, the RDK-X5, or the robot.
