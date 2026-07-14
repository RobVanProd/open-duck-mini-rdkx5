# Ground-Up Stage-One Recipe Local Search Preregistration

status: `PREREGISTERED_BEFORE_LOCAL_SEARCH_COMPUTE`

## Why this search exists

`STAGE1MIX4` established a more stable training scaffold than the earlier
canonical runs, but it did not establish an optimal PPO recipe. The longer
`STAGE1MIX20` trajectory also does not establish a winner: the 8,028,160-step
checkpoint improved only one of two moving development rollouts, and the
10,035,200-step checkpoint regressed to a zero-command fall plus failure of the
second moving rollout. The center recipe is therefore a search control, not a
selected policy.

This amendment reopens a bounded local recipe search at the corrected
reference-velocity frame and frozen stage-one command mixture. It supersedes
the earlier decision to begin mechanism-family comparison before establishing
whether the transient center-point behavior can be made persistent.

## Frozen invariants

- pinned Open Duck Playground commit: `b9be205ac64488c23504ca42e5ec790337adeec3`;
- reference, projected-reference table, observation/action ABI, actuator fit,
  task, command mixture, environment count, episode length, network topology,
  and evaluator are unchanged;
- local evaluation is CPU-only; local accelerators, the RDK-X5, and the robot
  are out of scope;
- training reward is recorded but is never a ranking input.

## Center and first-ring candidates

The center is learning rate `3e-4`, entropy cost `0.005`, discount `0.97`,
unroll length `20`, and imitation scale `1.0`. First-ring candidates change one
variable at a time:

| ID | Learning rate | Entropy cost | Imitation scale |
|---|---:|---:|---:|
| S1C | `3e-4` | `0.005` | `1.0` |
| S1LR_LO | `1e-4` | `0.005` | `1.0` |
| S1LR_HI | `1e-3` | `0.005` | `1.0` |
| S1ENT_LO | `3e-4` | `0.001` | `1.0` |
| S1ENT_HI | `3e-4` | `0.01` | `1.0` |
| S1IMIT_LO | `3e-4` | `0.005` | `0.5` |
| S1IMIT_HI | `3e-4` | `0.005` | `2.0` |

Discount and unroll length remain frozen in the first ring. They may be
searched only if no first-ring candidate improves persistence, under a new
pre-compute amendment. This keeps the first comparison interpretable and
avoids an unsupported Cartesian search.

## Rungs and selection

### Broad rung

- Reuse the already-produced seed-100 center checkpoints.
- Train each non-center candidate from scratch with seed `100` to `8,028,160`
  steps and export checkpoints at approximately 2M-step intervals.
- Evaluate the 6M and 8M checkpoints at x=`0.00` and x=`0.08` on development
  rollout seeds `100` and `101`, each for `1.08 s`.

Candidates are ordered lexicographically by:

1. number of checkpoints satisfying the full frozen emergence gate;
2. number of finite zero-command rollouts;
3. number of moving rollouts with positive displacement and positive local
   forward velocity;
4. persistence of those outcomes across both evaluated checkpoints;
5. frozen safety/behavior margins.

A fall, NaN, ABI/export failure, or constant saturated action is always worse
than a finite result. Training reward cannot break a tie. An isolated passing
rollout is evidence of partial emergence, not a policy pass.

### Replication rung

At most two non-dominated recipes, including the center if tied, advance. Each
is retrained from scratch with training seed `101` to `12,042,240` steps.
Checkpoints at 8M, 10M, and 12M receive the same frozen evaluation. A recipe can
be called `BEST_RECIPE_TESTED` only if it produces a full emergence-gate pass
at two consecutive checkpoints and this is reproduced across the two training
seeds. Otherwise the result is `NO_RECIPE_WINNER`.

Search-validation and final-held-out seeds remain untouched until a recipe
meets that replication condition.

## Compute stop rules

- Each candidate is archived independently so a later session loss cannot
  erase completed evidence.
- No candidate may silently receive more timesteps, seeds, or favorable
  evaluator conditions than another candidate at the same rung.
- The search stops immediately if the conservative total ledger would exceed
  the original 94-unit hard limit.
- Exact Colab compute-unit consumption is not exposed by the CLI; recorded
  charges remain conservative planning charges, not claims about the account
  balance.
- If the broad rung cannot be completed fairly, candidates are not ranked.

