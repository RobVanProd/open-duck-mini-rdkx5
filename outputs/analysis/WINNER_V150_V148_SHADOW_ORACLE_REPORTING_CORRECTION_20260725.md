# Winner V150 shadow-oracle reporting correction

- Status: `PASS_WINNER_V150_V148_SHADOW_ORACLE_REPORTING_CORRECTION`
- The frozen shadow trace is bit-exact to V149.
- Physical failure: torque only; four extra flags are invalid for a deliberately unapplied shadow action.
- The new right-ankle event at tick 586 has a safe, non-empty oracle label at tick 583.
- Decision: `EARN_V151_BOUNDED_TWO_CENTER_CONTRACT_PREREGISTRATION`
- Read-only correction; no rerun, policy change, training, Colab, or hardware.
