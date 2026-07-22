# Winner-v88 flat-transport representation result

- Status: `PASS_WINNER_V88_FLAT_TRANSPORT_REPRESENTATION_DIAGNOSTIC`
- Classification: `NO_LINEAR_OBSERVABLE_REPRESENTATION_SELECTED`
- Selected checkpoint / feature family: `none / none`
- Half source RMS: `0.090443`
- Half current-observation / flat-basis heldout RMS: `0.118308 / 0.098380`
- Final source RMS: `0.094140`
- Final current-observation / flat-basis heldout RMS: `0.113438 / 0.117549`
- Rollout episodes / fits: `160 / 78`
- Optimizer updates / support cells / policy artifacts / robot access: `0 / 0 / 0 / 0`
- Result SHA-256: `adf4a892b9d19d5b5458e544b576de2188873814128f43b13c0ab232641faaae`

The causal uniform-history term from the provided equation contains useful
in-sample signal and improves the half checkpoint relative to current
observations alone. It does not clear the preregistered heldout-transfer rule:
half remains worse than the unchanged source, and final regresses relative to
current observations. Adding the frozen hidden state does not repair transfer.

The equation was therefore used as a diagnostic but is not selected as a
policy mechanism. No `rho` or `q` was chosen or searched, no architecture was
changed, no checkpoint was selected, and `robot_clearance` remains false.
