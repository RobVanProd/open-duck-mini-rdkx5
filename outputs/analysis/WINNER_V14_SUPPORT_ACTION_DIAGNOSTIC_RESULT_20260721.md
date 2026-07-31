# Winner-v14 support-action diagnostic result

- Status: `PASS_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC`
- Decision: `NO_SCALE_PASSES_PREREGISTER_SUPPORT_OBJECTIVE_REPAIR`
- Selected / passing scales: `None / []`
- GitHub run / artifact: `29834084968` / `8496883752`
- Artifact ZIP SHA-256: `a638437b3da6700527f0c1b9aa98226bb9d983fa6f58d4ca58b23da1b141b61b`
- Raw result SHA-256: `cc7bc883d0672a72d66851c96b82c2de4e14ec8b7bb15cd87ccabc8a37a418c6`
- Main / repeat cells: `1,240 / 320`
- Optimizer / locomotion / robot access: `0 / 0 / 0`

No candidate scale passed the unchanged gate. Every nonzero scale
preserved heldout response context and beat the corrected constant
predictor baseline, but every scale retained early pitch-only support
failures. Inference amplitude scaling is closed; only a separately
preregistered support-objective repair is authorized next.

The 6.17 MB raw cell result remains hash-bound in the downloaded
GitHub artifact; this repository stores the strictly rederived compact
summary rather than duplicating the raw result.
