# Ground-Up Torso-COM Crossed Phase-Localization Result

status: `PASS_TORSO_COM_CROSSED_PHASE_COMPLETE`
decision: `CROSSED_LOCALIZATION_UNRESOLVED_NO_FAMILY_SELECTED`

| policy | classification | target fraction | donor fraction | interaction fraction |
|---|---|---:|---:|---:|
| A05_DIRECT_1003520 | `DISTRIBUTED_OR_UNRESOLVED` | 0.412017 | 0.073537 | 0.514447 |
| A05_DIRECT_2007040 | `DISTRIBUTED_OR_UNRESOLVED` | 0.230653 | 0.248873 | 0.520474 |
| U05_DIRECT_1003520 | `DISTRIBUTED_OR_UNRESOLVED` | 0.333366 | 0.102615 | 0.564019 |
| U05_DIRECT_2007040 | `DISTRIBUTED_OR_UNRESOLVED` | 0.303839 | 0.230976 | 0.465185 |
| U_CURRICULUM_1024000 | `DISTRIBUTED_OR_UNRESOLVED` | 0.341252 | 0.205638 | 0.453109 |
| U_CURRICULUM_512000 | `DISTRIBUTED_OR_UNRESOLVED` | 0.282374 | 0.144672 | 0.572954 |

Validity:

- diagonal pitch maximum error: 0 rad;
- diagonal alignment maximum error: 0;
- diagonal classification mismatches: 0;
- negligible crossed cells: 0.

No p-value or training reward is used. The frozen decision authorizes at most its named next read-only preregistration.

All six policies are `DISTRIBUTED_OR_UNRESOLVED`. Interaction is the largest
descriptive fraction for every checkpoint (.453109-.572954), but none reaches
the frozen .60 dominance threshold or the required 2x separation from both
other effects. It therefore cannot be promoted as an interaction-dominant
result.

Aggregate categorical localization:

| target tick | donor 0 C/A/M | donor 24 C/A/M | donor 32 C/A/M | donor 40 C/A/M |
|---:|---:|---:|---:|---:|
| 0 | 19/7/10 | 21/12/3 | 24/9/3 | 30/3/3 |
| 24 | 14/20/2 | 21/9/6 | 19/13/4 | 24/7/5 |
| 32 | 15/14/7 | 17/13/6 | 16/15/5 | 24/9/3 |
| 40 | 25/10/1 | 10/24/2 | 13/18/5 | 11/24/1 |

`C/A/M` means corrective/amplifying/intermediate across the 36
policy/fit/command groups. The table demonstrates coupling: for example, the
donor-40 response is predominantly corrective at target ticks 0, 24, and 32,
but predominantly amplifying at target tick 40; conversely, target tick 40 is
predominantly corrective with donor 0 and amplifying with donors 24, 32, and
40. This is a deterministic localization, not permission to choose the closest
mechanism.

The complete result contains 303 corrective, 207 amplifying, 66 intermediate,
and zero negligible cells. The 144 diagonal cells reproduce the prior signed
pitch vectors, alignments, and classifications exactly (maximum error zero),
so the crossed result is valid.

The frozen decision selects no actor-action, phased-plant, joint-phase,
architecture, objective, estimator, checkpoint, policy, or training family.
A further study requires a separate preregistration. No training, Colab,
GPU/iGPU, RDK-X5, runtime, or robot work is authorized.
