# Winner V159 cadence-screen invalidity

- Status: `PASS_WINNER_V159_CADENCE_INVALIDITY_ATTRIBUTION`
- The CPU run stopped before behavior because the policy's 14-D reference-action observation is integer-phase indexed.
- The RDK winner-v2 adapter independently requires one integer phase step per tick and rejects fractional phase.
- Interpolation was not added because it would alter the frozen policy observation contract.
- Decision: `CLOSE_POSTEXPORT_CADENCE_MECHANISM_AS_NONDEPLOYABLE_UNDER_FROZEN_CONTRACT`
- Selection weight zero; no training, Colab, runtime change, deployment, Gate 5, or robot.
