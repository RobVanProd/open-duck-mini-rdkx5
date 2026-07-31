# Phase 2 Corrected Live-Oracle Iter1 Rate165 Candidate

status: `OFFLINE_SIM_CANDIDATE`

This candidate is a deployable-shape ONNX policy:

```text
obs[1,101] -> continuous_actions[1,14]
```

It was trained offline by phase/contact-modulated behavior cloning from the
corrected `z=0.0026` live-oracle iteration-1 aggregate manifest. It is not a
robot-validated policy.

## Files

- `candidate.onnx`
- `candidate_mlp.npz`
- `SHA256SUMS`

## Hashes

- ONNX:
  `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`
- NPZ:
  `2a896d32b9e40565008073970cacc9d31c8543e5ee8f3ee44162c5ddcd73ed36`

## Offline Gates

Corrected bridge:

```text
outputs/analysis/actuator_response_fit_corrected_knee.json
```

Conditions:

- task: `rough_terrain_backlash`
- terrain hfield z-scale: `0.0026`
- reset mode: `home-support`
- bridge mode: `fitted`
- seeds: `0..7`
- duration: `15 s`

Gate results:

- `x=0.08`: `8/8` pass, track ratio `0.3400`, mean vx `0.0272 m/s`,
  max pitch-chain p95 velocity `1.6410 rad/s`, corrected p95 and max velocity
  excess `0.0000`, max tracking p95 `0.1827 rad`.
- `x=0.0`: `8/8` pass, mean vx approximately `0.0000 m/s`, max pitch-chain
  p95 velocity `0.0642 rad/s`, corrected p95 and max velocity excess `0.0000`.

## Scope

No robot test, SSH, deploy, grounded replay, or runtime behavior change was
performed for this candidate. Hardware validation remains a separate reviewed
step.
