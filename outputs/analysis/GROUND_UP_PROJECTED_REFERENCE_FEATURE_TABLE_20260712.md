# Ground-Up Projected Reference Feature Table

status: `PASS_PROJECTED_REFERENCE_FEATURE_TABLE`

One deterministic float32 table was generated from the frozen polynomial
reference for all `240` command cells, all `27` phases, and all `14` actions.

- source SHA256: `5850c0610ed89e2860e7047f9ee27d8412462e1199752952c3c2a0efd2cb7a25`
- table shape: `[240,27,14]`
- artifact SHA256: `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`
- maximum absolute action: `1.0`
- pitch-chain maximum rates: `1.50,1.50,1.75,1.25,1.00,1.25 rad/s`
- zero-command runtime rule: all-zero reference feature

The generator was run twice and produced the identical artifact hash. Training
and RDK runtime will consume this same table; neither independently evaluates
the polynomial source. This prevents reference-math or packaging drift.

This is a feature-contract pass, not evidence that open-loop reference playback
walks. The policy must learn closed-loop final actions and pass the frozen gates.
No robot, GPU, Colab, deployment, or hardware action occurred.
