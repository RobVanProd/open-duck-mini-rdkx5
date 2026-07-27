# T27 T23 sequential R2 robustness preregistration

- Status: `PREREGISTERED_T27_T23_SEQUENTIAL_R2_ROBUSTNESS_MATRIX`
- Contract SHA-256: `e12e267ef0fbaf36ba6430db713ccd7b8a57303036f0bbe9d5331bacc85d3027`
- Matrix: 20 frozen R2 conditions × 2 checkpoints × 2 measured fits × 4 commands = at most 320 cells.
- Execution is strictly sequential and stops after the first complete failed 16-cell condition.
- Each cell uses the exact 250-tick support handoff, T5 duration protection, and unchanged behavior/quality gates.
- No training, checkpoint selection, Gate 5, RDK-X5, robot access, torque, or motion is authorized.
