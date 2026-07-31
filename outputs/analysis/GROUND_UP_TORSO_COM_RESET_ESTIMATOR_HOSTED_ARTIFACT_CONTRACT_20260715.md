# Ground-Up Torso-COM Reset-Estimator Hosted Artifact Contract — 2026-07-15

## Result

`PASS_RESET_ESTIMATOR_HOSTED_ARTIFACT_CONTRACT`

The recovered `RESET_EST_LATCH_U05` archive is 10,067,634 bytes with SHA-256
`88bf9c799e3a44e7f7817823166ee4365cc574a1a68d662930ae448884563673`.
The external and archived manifests are exact. All three Orbax directory hashes
and all three ONNX hashes/sizes match; CPU ONNX validation and finite inference
pass with the exact 116-D stateful interface.

The corrected expansion report preserves the original sole `1e-7` failure
byte-for-structure and separately passes the float32-epsilon gate. Actor error
is exactly one epsilon, critic error zero, all other raw checks pass, and the
manifest contains the exact frozen 2M command. Training log and event file are
present. Hosted execution took 958.802 seconds; total session wall was
1,068.778 seconds. Recovery, the 2,400-second ceiling, and named cleanup pass;
zero sessions remain and compute use is `UNMEASURED`.

Training and hosted reward remain behavior-unevaluated and carry no selection
weight.

## Authority

This authorizes only a local CPU transform contract for the two post-update
exports, applying the already-frozen actual-position guard, x=0 deadband, and
conservative left-ankle envelope before the complete behavior matrix. No
behavior result exists yet. No new training, Colab, local GPU/iGPU, RDK-X5,
runtime, or robot action is authorized.

