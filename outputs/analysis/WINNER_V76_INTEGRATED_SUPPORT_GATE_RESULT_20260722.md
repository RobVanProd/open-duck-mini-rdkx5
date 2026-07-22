# Winner-v76 integrated support-gate result

- Status: `HOLD_WINNER_V76_INTEGRATED_SUPPORT_GATE`
- Decision: `DO_NOT_SELECT_WINNER_V75_DEPLOYMENT_POLICY`
- Main cells / heldout repeats: `248 / 64`
- Half failures: `10`, all roll/pitch
- Final failures: `9`, all roll/pitch
- Half predictor advantage: passes both plants
- Final predictor advantage: fails both plants (`0.48976/0.49075` learned versus `0.22134/0.22116` constant MSE)
- Action chain / JAX-ONNX / repeatability / context separation: all pass
- Selected checkpoint: none
- Robot clearance: `false`
- Result SHA-256: `19e71696f223b2585f80457095cbdf577d91846c6cf16c2bb739c0ef5fa44737`

The functional numeric guard allowed training to reach both endpoints without
changing the learned update, but the unchanged persistence rule still rejects
the arm. The half and final checkpoints both retain roll/pitch failures, and
the final checkpoint additionally loses the frozen learned-predictor advantage.
No closest endpoint is promoted.
