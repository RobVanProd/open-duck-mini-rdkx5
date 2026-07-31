# Winner V167b reference-amplitude reporting correction

- Status: `PASS_WINNER_V167B_REFERENCE_AMPLITUDE_REPORTING_CORRECTION`
- V167's auxiliary reproduction check compared ONNX actions to a boolean trace flag instead of the trace's final `action` field.
- The fixed scale, 12 events, oracle alignment/error rules, and decision rule are unchanged.
- The invalid run already aligned only 3/12 events and improved 2/12; those mechanism counts are unaffected by this correction.
- Authorizes one corrected CPU shadow rerun; no simulation, training, contract change, Gate 5, or robot.
