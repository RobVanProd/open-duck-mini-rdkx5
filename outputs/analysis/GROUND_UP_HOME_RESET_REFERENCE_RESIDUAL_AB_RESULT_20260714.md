# Ground-Up Home-Reset Reference-Residual A/B Result

status: `NOMINAL_GAIT_FOUND_NO_HARDWARE_READY_WINNER`

## Corrected frozen evaluation

| arm | checkpoint | x | moving passes | body dx | mean body vx | contacts L/R | saturation | result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| A0 current ref-conditioned | 3M | .074 | 2/2 | +.05006 m | +.04635 m/s | 8 / 7 | 0% | emergence pass |
| A0 current ref-conditioned | 4M | .074 | 2/2 | +.04359 m | +.04036 m/s | 10 / 7 | 0% | emergence pass |
| A1 reference residual | 3M | .074 | 2/2 | +.05599 m | +.05185 m/s | 4 / 5 | 0% | emergence pass |
| A1 reference residual | 4M | .074 | 2/2 | +.06910 m | +.06398 m/s | 2 / 3 | 0% | emergence pass |
| all four | any | .080 | 0/8 | negative | negative | present | up to 100% | hard failure |

Home reset is deterministic, so seeds 100 and 101 correctly produce identical
nominal trajectories. All four saved checkpoints complete and pass the frozen
gait-emergence classifier at their exact training/reference command x=`0.074`.
The strongest is A1 at 4M, reaching `0.8646x` command with bilateral contact
transitions and no action saturation.

None is hardware-ready. At x=`0.074`, A1 4M exceeds the fitted per-joint target
rate limits by as much as `4.24 rad/s` and has pitch-chain tracking p95
`0.3574 rad`, so its candidate gate remains `HOLD_CANDIDATE_TRACKING`.

## x=.08 failure mechanism

The ONNX normalizer proves the command-generalization failure is structural.
Training fixed command x=`0.074`, so command observation indices have standard
deviation `1e-6`. Changing x by only `.006` therefore creates a normalized
input shift of approximately `6000`; every A1 4M action becomes a constant
`+/-1` vector. The x=`0.08` gate was not testing a learned command distribution
because no command distribution was trained.

## Decision

The earlier claim that no nominal gait policy exists is superseded. A valid
home-reset nominal gait bootstrap exists at x=`0.074`, but there is still no
full checkpoint winner and no robot clearance. Evidence selects two coupled
contract defects before more accelerator compute:

1. constant-command normalization makes the required x=`0.08` generalization
   mathematically out of distribution;
2. the training action-rate contract uses the generic `5.24 rad/s` limit rather
   than the measured per-joint hardware vector.

The next bounded CPU diagnostic is to apply the measured vector projection to
A1 4M at x=`0.074` and determine whether the discovered gait survives. A new
training recipe may be designed only after that result; it must train a real
command distribution and enforce the measured vector inside the learning
loop. No Colab, GPU, RDK-X5, or robot access occurred.
