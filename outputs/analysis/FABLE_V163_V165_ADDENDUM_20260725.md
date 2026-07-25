# Fable addendum: V163 through V165

The feasibility-preserving continuation proposed in the V127-V162 handoff was
tested through its cheapest falsifier and then through the state-coherence
boundary. It is now closed under its preregistered rules. No Colab training was
run.

## V163: the graph-level falsifier passed, narrowly

V163 reused the already hash-frozen V127 CPU smoke proposal, which aggregates
exactly 32 PPO iterations from the green V121-half source. It introduced no
training. The preregistered dyadic ladder was:

```text
alpha = 1, 1/2, 1/4, 1/8, 1/16, 1/32
```

`1/32` was the derived nontrivial floor: one average-iteration displacement
from the 32-iteration proposal. Fractions ran in descending order, the
tightest source-margin cell ran first, and every failed fraction stopped on
its first failed cell.

Observed:

- `1`: P31/34 x=.080 failed at `2.21268272 N.m`.
- `1/2`: same cell failed at `2.05772877 N.m`.
- `1/4`: same cell failed at `2.04931831 N.m`.
- `1/8`: same cell failed at `1.95769691 N.m`.
- `1/16`: P31/34 x=.080 passed, but P31/34 x=.074 failed at
  `1.91299820 N.m`.
- `1/32`: all six moving cells passed; the two x=0 cells remained exact by the
  unchanged deployment deadband. Worst torque was `1.90521049 N.m`, improving
  the green source's `1.90963745 N.m`.

The result hash is
`df771a2ad5343e1ed54b1229fb4600fc7e9e3b6cd5cfd3d0f63dacdf24a6960c`.
This earned only a trainable-state coherence test.

The run also measured the naïve exact-acceptance cost: 12 moving cells took
`708.8 s` locally. Repeating the unbatched evaluator inside every one of 392
PPO iterations would be computationally unacceptable.

## Why the trainable block was fixed at 28 iterations

The frozen V127 continuation has 196 PPO iterations at the half export and 392
at the final export:

```text
196 = 7 * 28
392 = 14 * 28
```

Therefore V164/V165 fixed:

- block length: 28 PPO iterations;
- blocks to half/final: 7/14;
- accepted fraction: `1/28`, one average-iteration displacement;
- no alternate alpha, block length, export spacing, or retry.

This was the only equal-block construction that landed exactly on both frozen
exports while preserving the nontrivial-step derivation.

## V164: actor-only with frozen normalization failed

V164 built a coherent checkpoint boundary:

- mature source observation normalizer frozen exactly;
- actor `source + (proposal-source)/28`;
- proposal reward critic retained;
- proposal cost critic and dual state retained;
- Adam moments reset to exact zero after backtracking;
- environment reset required at the future integration boundary.

Restore, optimizer, export, ABI, and x=0 contracts passed far enough to run
behavior. P31/34 x=.080 passed at `1.88710594 N.m`, but P31/34 x=.074 failed
at `1.91642570 N.m`. Actor-only/frozen-normalizer state was closed without an
alpha or block retry.

Result hash:
`0247a88fe1567a0b8f28dbe7fe53481fb9327b9c0a9b4fd97a8722001d0cf1ac`.

## V165: mathematically coherent normalization also failed

V165 kept the exact same `1/28` alpha and 28-iteration block. It changed only
the state representation needed to reproduce the graph-level normalizer
movement:

```text
mean = mean_source + alpha * (mean_proposal - mean_source)
std  = std_source  + alpha * (std_proposal  - std_source)
count increment = round(alpha * (count_proposal - count_source)), min 1
summed_variance = max(std^2 - std_eps, 0) * accepted_count
```

This makes the deployed mean/std exact while leaving a valid Welford state for
future updates. There was no new coefficient.

After one pre-outcome import-path correction, V165 reached behavior and failed
the first cell: P31/34 x=.080 peaked at `1.91443348 N.m` versus the unchanged
`1.91229675 N.m` limit. The preregistered decision is:

```text
CLOSE_FEASIBILITY_PRESERVING_BLOCK_CONTINUATION_NO_RETRY
```

Result hash:
`a9f310b641dd96b23bd96487140bd474fa92bc5c4acd5445faf16c3900c3e2cc`.

## Updated causal conclusion

A safe graph-level point exists along one 32-iteration constrained direction
at exactly `1/32`. That fact does **not** produce an export-aligned trainable
continuation:

- the equal-block, one-average-step displacement is `1/28`;
- actor-only state fails;
- a fully coherent interpolated normalizer state also fails;
- the margin is only `0.00265930 N.m` at the source;
- exact closed-loop acceptance is expensive and cannot safely be reduced to
  one plant/command cell because V163 and V164 set their failures on different
  cells.

This closes the premise that the current V127 optimizer can be made persistent
by deterministic parameter backtracking under the existing frozen schedule.
Changing to 32-step blocks, using `1/32`, shifting export points, taking a
smaller fraction, or trying a different batch would be a retry of the closed
class, not a new mechanism.

## Decision now required

Select one mechanically distinct next class with a CPU-only falsifier, or
state the minimum reviewed contract expansion now justified by the evidence.
In particular:

1. Is there a constrained optimizer whose first nontrivial step can be
   certified without behavior-gate backtracking and without another reward or
   dual scalar?
2. If not, which exact contract expansion is causally indicated: continuous
   reference/phase interpolation, reference geometry, command support,
   architecture, or another named quantity?
3. What is the cheapest CPU falsifier for that expansion before training?
4. What evidence would distinguish a genuine larger feasible policy class
   from merely relaxing the torque gate?

Do not propose:

- another reward scale, hinge, peak, dual law, eta, or PPO-Lagrangian retry;
- a different alpha, block length, batch, export spacing, or checkpoint
  selection;
- post-hoc projection, runtime torque enforcement, local residuals, sparse
  distillation, DAgger variants, or phase-only triggers;
- long-range transport or a larger recurrent state without a new causal link.

No hosted run is currently earned. Gate 5 remains closed.
