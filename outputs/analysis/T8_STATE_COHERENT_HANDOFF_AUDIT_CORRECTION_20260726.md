# T8 independent-audit body-frame correction

- Status: `T8_POSTOUTCOME_AUDIT_BODY_FRAME_CORRECTION`
- Contract SHA-256: `9cde95cbaced2cbbe65fe829fc4fe3576d586489319c6b30a18d3b04bbe56a0e`
- Original audit preserved: yes
- Result status/decision can change: no

The first auditor used world-X displacement in two x=.08 cells that yawed during the 12-second run. The frozen gait gate uses body-frame progress. Integrating the already-recorded local forward velocity at the frozen 20 ms step reproduces the evaluator's +1.27277/+1.26921 m.

The four x=0 rate-excess failures are unaffected, so T8 remains a 12/16 hold and direct zero-training handoff remains closed. This correction authorizes only a rerun of the independent auditor.
