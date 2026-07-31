# T14 domain-gradient geometry result

- Status: `HOLD_T14_DOMAIN_GRADIENT_GEOMETRY`
- Decision: `CLOSE_WORST_DOMAIN_OBJECTIVE_FROM_V121_HALF`
- Broad vs negative-COM gradient cosine: `0.035354406958875095`
- Negative-COM loss derivative along broad descent: `-0.08069995045661926`
- Harm-sign minibatches: `0/4`
- Failed checks: `['at_least_three_of_four_minibatches_show_harm', 'formal_dimensions_exact', 'primary_broad_and_negative_gradients_conflict', 'primary_broad_descent_strictly_harms_negative_com', 'source_normalizer_sensitivity_preserves_harm_sign']`
- CPU-only; zero optimizer steps, behavior cells, hosted compute, hardware, torque, or motion.
