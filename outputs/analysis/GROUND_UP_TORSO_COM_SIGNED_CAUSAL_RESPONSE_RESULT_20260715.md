# Ground-Up Torso-COM Signed Causal-Response Result

status: `PASS_TORSO_COM_SIGNED_RESPONSE_COMPLETE`
decision: `MIXED_SIGN_NO_POLICY_FAMILY_SELECTED`

| policy | classification | corrective | amplifying | mixed | negligible |
|---|---|---:|---:|---:|---:|
| A05_DIRECT_1003520 | `MIXED_POLICY_RESPONSE` | 14 | 7 | 3 | 0 |
| A05_DIRECT_2007040 | `MIXED_POLICY_RESPONSE` | 13 | 7 | 4 | 0 |
| U05_DIRECT_1003520 | `MIXED_POLICY_RESPONSE` | 10 | 11 | 3 | 0 |
| U05_DIRECT_2007040 | `MIXED_POLICY_RESPONSE` | 11 | 8 | 5 | 0 |
| U_CURRICULUM_1024000 | `MIXED_POLICY_RESPONSE` | 10 | 9 | 5 | 0 |
| U_CURRICULUM_512000 | `MIXED_POLICY_RESPONSE` | 9 | 13 | 2 | 0 |

All six checkpoints fail both frozen systematic-sign rules. Consequently no
arm has two systematically classified siblings, and no memory/estimator,
objective-sign, or actuator-effect family is selected.

Aggregate localization:

| slice | cells | corrective | amplifying | mixed | negligible |
|---|---:|---:|---:|---:|---:|
| all | 144 | 67 | 55 | 22 | 0 |
| tick 0 | 36 | 19 | 7 | 10 | 0 |
| tick 24 | 36 | 21 | 9 | 6 | 0 |
| tick 32 | 36 | 16 | 15 | 5 | 0 |
| tick 40 | 36 | 11 | 24 | 1 | 0 |
| P30 | 72 | 31 | 28 | 13 | 0 |
| P31/34 | 72 | 36 | 27 | 9 | 0 |
| x=.074 | 48 | 20 | 17 | 11 | 0 |
| x=.077 | 48 | 23 | 20 | 5 | 0 |
| x=.080 | 48 | 24 | 18 | 6 | 0 |

The strongest aggregate localization is temporal: corrective cells are the
plurality at ticks 0 and 24, while amplifying cells are the majority at tick
40. This is descriptive only and does not replace the frozen policy-level
rule. The machine-readable artifact records every policy/fit/command/tick
cell and its full eight-tick signed trajectories.

All 144 cells have non-negligible physical and actor pitch vectors. Physical
norms span .141763-.193862 rad and actor-effect norms span
.000244-.023726 rad. Maximum bridge, sent-target, and applied-target
reconstruction error remains 5.1498413089490214e-08 rad.

No p-value or training reward is used. Under the frozen decision, the result
permits a separately preregistered localization study but selects no policy,
architecture, objective, estimator, or training family. It authorizes no
training, Colab, GPU/iGPU, RDK-X5, runtime, or robot work.
