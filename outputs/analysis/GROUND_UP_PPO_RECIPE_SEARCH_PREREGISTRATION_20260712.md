# Ground-Up PPO Recipe Search Preregistration

status: `PREREGISTERED_BEFORE_RECIPE_SEARCH_COMPUTE`

## Question

The canonical Berkeley humanoid PPO recipe is a runnable control, not proven
optimal for Open Duck Mini V2. This search asks which bounded PPO recipe learns
the strongest policy under the already-frozen environment, reference, hardware
model, evaluation gates, and policy architecture.

No recipe may be called globally optimal. The strongest result may only be
called the best recipe tested under this manifest and the frozen held-out
evaluation.

## Canonical center

The pinned Playground dependency resolves the canonical center to:

- learning rate: `3e-4`;
- discount: `0.97`;
- entropy cost: `0.005`;
- PPO clipping epsilon: `0.2`;
- unroll length: `20`;
- updates per batch: `4`;
- policy/value MLP: `[512,256,128]`;
- static imitation scale: `1.0`.

The successful 256-environment T4 probe measured 1,003,520 environment steps
in 794.54 seconds of training, but did not prove gait emergence. Training
reward from that probe is not used for selection.

## Search variables

The first recipe search changes one variable at a time around the canonical
center so causal effects remain interpretable:

| ID | Changed variable | Value |
|---|---|---:|
| R00 | canonical center | unchanged |
| R01 | learning rate | `1e-4` |
| R02 | learning rate | `1e-3` |
| R03 | discount | `0.99` |
| R04 | entropy cost | `0.001` |
| R05 | entropy cost | `0.01` |
| R06 | unroll length | `10` |
| R07 | unroll length | `40` |
| R08 | static imitation scale | `0.5` |
| R09 | static imitation scale | `2.0` |

Clipping, update count, minibatch geometry, and network size remain frozen in
this screen. They are not searched simultaneously because the remaining
compute budget cannot support an interpretable full Cartesian product.
Network topology is handled by the architecture-family search, and imitation
decay remains its separately preregistered mechanism.

The numeric levels are symmetric or near-symmetric bounded perturbations around
the canonical center on their natural linear or logarithmic scale. They are
hypotheses to test, not claimed improvements.

## Measured gait-emergence window

Recipe ranking cannot begin at an arbitrary timestep. Starting from scratch,
R00 is trained in one-million-step increments. Each checkpoint is evaluated on
the frozen development conditions. The emergence window is the first checkpoint
at which all of the following are true on two consecutive evaluations:

1. finite rollout with no standing-collapse termination;
2. positive-command forward displacement is positive;
3. both feet exhibit contact transitions and each receives nonzero support;
4. the policy does not emit a constant saturated action vector;
5. x=0 evaluation is finite and recorded.

This is an emergence measurement, not a policy-clearance gate. The measurement
stops at the first qualifying pair or at the recipe-search compute cap. If no
pair is found, recipe comparison is `NO_RESULT`; the window is not shortened to
force a ranking.

## Successive halving

All R00-R09 recipes receive the same measured emergence window and the same two
development seeds. A recipe is immediately removed for NaN, repeated early
termination, export/ABI failure, constant saturation, or failure to show
bilateral contact transitions.

Survivors are ranked on the already-preregistered behavior and safety metrics,
never training reward. The canonical R00 is protected into the medium rung.
The best three noncanonical survivors plus R00 receive twice the emergence
window on four disjoint search-validation seeds.

After the medium rung, at most two recipes advance to the policy-family search.
A noncanonical recipe advances only if its paired validation evidence is better
than R00 without worsening a hard gate. Ties retain R00. No untested combination
of one-factor changes is synthesized during this search.

## Compute and execution boundary

- recipe-search allocation: at most `15` of the `35` broad/medium search units;
- remaining mechanism-family allocation: at least `20` units unless recipe
  search uses fewer than 15;
- all failed setup or interrupted accelerator time counts;
- jobs run sequentially and the ledger is updated before another job starts;
- the overall consumed total may never exceed 94 units;
- local execution is CPU-only; local iGPU and onboard GPU are prohibited;
- no RDK access, deployment, torque, or motor activity is authorized.

If the equal-window comparison cannot be completed inside 15 units, the result
is `NO_RECIPE_WINNER_WITHIN_BUDGET`; incomplete candidates are never ranked
against completed ones.
