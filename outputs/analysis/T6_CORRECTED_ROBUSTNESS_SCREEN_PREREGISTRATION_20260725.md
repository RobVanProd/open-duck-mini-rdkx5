# T6 corrected-gate robustness screen preregistration

- Status: `PREREGISTERED_T6_CORRECTED_ROBUSTNESS_SCREEN`
- Contract SHA-256: `522226c7e79d95f6e7f61b073a060fa77b8c6540ff5907d08e1979512e96c6fe`
- Population: `V121`, `V123`, `V128`, and `V177`; both frozen checkpoints, both measured fits, four commands.
- Frozen condition: `TORSO_COM_X_NEG`, torso COM x offset `-0.05 m`.
- Matrix: `64` CPU-only cells in `16` resumable blocks.
- Protection: strict `>2 A` and strict `>1.5298374 N.m`, each passing only below `100` consecutive 50 Hz ticks.
- T4-baseline failures are explicitly replacement-quality stretch goals, not generic feasibility claims.
- No training, hosted compute, policy selection, robot access, Gate 5, torque, or motion is authorized.
