# Rate165 Zero-Command Hold Preregistration

status: `PREREGISTERED_OFFLINE_ONLY`

The repeated suspended x=0 telemetry shows policy-commanded asymmetric dither,
while the hard-vector limiter is inactive. Test the already established
command gate without changing the moving policy:

- low branch: `outputs/analysis/zero_action_policy.onnx`
- high branch: unchanged rate165 candidate
- gate: `abs(obs[6]) <= 0.02`
- actuator bridge: fixed-target P30 fit
- hard vector: joints `2,3,4,11,12,13`, limits
  `1.50,1.50,1.75,1.25,1.00,1.25 rad/s`
- platform: CPU only; no local GPU, Colab, deployment, SSH, or robot motion

Acceptance is preregistered as:

1. ONNX branch verification max error <= `1e-6`.
2. x=0 full-eight home-support runs complete with zero falls, zero action
   motion, and zero pitch-chain velocity excess.
3. x=.08 full-eight results exactly reproduce the unchanged rate165
   hard-vector projection within report precision, because the high branch is
   unchanged.

Any failed clause holds the candidate. Passing only authorizes a staged review;
it does not authorize installation or physical motion.
