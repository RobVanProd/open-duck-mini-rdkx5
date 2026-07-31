# Winner-v12 full calibrator-training preregistration

- Status: `PREREGISTERED_WINNER_V12_FULL_CALIBRATOR_TRAINING`
- Decision: `AUTHORIZE_FULL_CALIBRATOR_RUNNER_AND_CPU_CONTRACT_ONLY`
- Training authorized now: `false`
- Stage 1 / Stage 2 scheduled tick capacity: `2,000,000 / 2,000,000`
- Training population: `40 configurations x 2 hidden plants`
- Persistent checkpoints: `Stage-2 updates 50 / 100`
- Future support gate: `124 cells per checkpoint; both must pass`
- Robot clearance: `false`

This freezes the full automatic-calibrator design before implementation.
It deliberately does not train or enable the locomotion adapter. A
calibrator pass can authorize only a separate response-conditioned
locomotion-training preregistration.
