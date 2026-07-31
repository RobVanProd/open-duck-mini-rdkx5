# Winner V144 shadow-oracle reporting correction

- Status: `PASS_WINNER_V144_SHADOW_ORACLE_REPORTING_CORRECTION`
- The frozen shadow trace is bit-exact to V141.
- Physical failure: torque only; four extra flags came from applied-oracle prediction checks that are intentionally invalid when the teacher action is not applied.
- One right-ankle event at tick 397 has a safe, non-empty oracle label at tick 394.
- Decision: `EARN_ONE_V145_ON_POLICY_DAGGER_CPU_PREREGISTRATION`
- Read-only correction; no rerun, training, behavior, Colab, or hardware.
