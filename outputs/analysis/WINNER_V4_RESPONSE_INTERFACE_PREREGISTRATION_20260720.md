# Winner-v4 Automatic-Response Interface Preregistration — 2026-07-20

status: `PREREGISTERED_PENDING_RUNTIME_REVIEW`

decision: `REQUEST_RUNTIME_SCHEMA_REVIEW_NO_IMPLEMENTATION`

JSON SHA-256: `562ea92c4ba9eb026263740a07fe349ed79e051f0a162e8dd476812f089b6adc`

## Hypothesis

The broad recurrent adapter failed because the deployed policy had to infer episode dynamics only implicitly after control began. Supplying a deterministic, machine-collected pre-policy response context may make the supported configuration regime observable without a manual mass, COM, dimension, or component inventory.

This is not a training preregistration. It freezes a proposed deployment ABI for
runtime review and a zero-PPO CPU contract. The completed winner-v3 result is not
reclassified.

## Proposed ONNX ABI

```text
obs[1,115], previous_action[1,14], h_in[1,64], response_context[1,73]
  -> action[1,14], previous_action_out[1,14], h_out[1,64]
```

The existing 115-D observation, final-action semantics, phase timing, and recurrent
state meanings remain unchanged. `response_context` is a separate immutable per-episode
input. Runtime sends physical SI values; normalization is embedded in the ONNX graph.

## Exact 73-field order

0. `joint_response.left_hip_yaw.delay_ticks`
1. `joint_response.left_hip_yaw.gain_ratio`
2. `joint_response.left_hip_yaw.time_constant_s`
3. `joint_response.left_hip_yaw.tracking_p95_rad`
4. `joint_response.left_hip_yaw.current_p95_a`
5. `joint_response.left_hip_roll.delay_ticks`
6. `joint_response.left_hip_roll.gain_ratio`
7. `joint_response.left_hip_roll.time_constant_s`
8. `joint_response.left_hip_roll.tracking_p95_rad`
9. `joint_response.left_hip_roll.current_p95_a`
10. `joint_response.left_hip_pitch.delay_ticks`
11. `joint_response.left_hip_pitch.gain_ratio`
12. `joint_response.left_hip_pitch.time_constant_s`
13. `joint_response.left_hip_pitch.tracking_p95_rad`
14. `joint_response.left_hip_pitch.current_p95_a`
15. `joint_response.left_knee.delay_ticks`
16. `joint_response.left_knee.gain_ratio`
17. `joint_response.left_knee.time_constant_s`
18. `joint_response.left_knee.tracking_p95_rad`
19. `joint_response.left_knee.current_p95_a`
20. `joint_response.left_ankle.delay_ticks`
21. `joint_response.left_ankle.gain_ratio`
22. `joint_response.left_ankle.time_constant_s`
23. `joint_response.left_ankle.tracking_p95_rad`
24. `joint_response.left_ankle.current_p95_a`
25. `joint_response.neck_pitch.delay_ticks`
26. `joint_response.neck_pitch.gain_ratio`
27. `joint_response.neck_pitch.time_constant_s`
28. `joint_response.neck_pitch.tracking_p95_rad`
29. `joint_response.neck_pitch.current_p95_a`
30. `joint_response.head_pitch.delay_ticks`
31. `joint_response.head_pitch.gain_ratio`
32. `joint_response.head_pitch.time_constant_s`
33. `joint_response.head_pitch.tracking_p95_rad`
34. `joint_response.head_pitch.current_p95_a`
35. `joint_response.head_yaw.delay_ticks`
36. `joint_response.head_yaw.gain_ratio`
37. `joint_response.head_yaw.time_constant_s`
38. `joint_response.head_yaw.tracking_p95_rad`
39. `joint_response.head_yaw.current_p95_a`
40. `joint_response.head_roll.delay_ticks`
41. `joint_response.head_roll.gain_ratio`
42. `joint_response.head_roll.time_constant_s`
43. `joint_response.head_roll.tracking_p95_rad`
44. `joint_response.head_roll.current_p95_a`
45. `joint_response.right_hip_yaw.delay_ticks`
46. `joint_response.right_hip_yaw.gain_ratio`
47. `joint_response.right_hip_yaw.time_constant_s`
48. `joint_response.right_hip_yaw.tracking_p95_rad`
49. `joint_response.right_hip_yaw.current_p95_a`
50. `joint_response.right_hip_roll.delay_ticks`
51. `joint_response.right_hip_roll.gain_ratio`
52. `joint_response.right_hip_roll.time_constant_s`
53. `joint_response.right_hip_roll.tracking_p95_rad`
54. `joint_response.right_hip_roll.current_p95_a`
55. `joint_response.right_hip_pitch.delay_ticks`
56. `joint_response.right_hip_pitch.gain_ratio`
57. `joint_response.right_hip_pitch.time_constant_s`
58. `joint_response.right_hip_pitch.tracking_p95_rad`
59. `joint_response.right_hip_pitch.current_p95_a`
60. `joint_response.right_knee.delay_ticks`
61. `joint_response.right_knee.gain_ratio`
62. `joint_response.right_knee.time_constant_s`
63. `joint_response.right_knee.tracking_p95_rad`
64. `joint_response.right_knee.current_p95_a`
65. `joint_response.right_ankle.delay_ticks`
66. `joint_response.right_ankle.gain_ratio`
67. `joint_response.right_ankle.time_constant_s`
68. `joint_response.right_ankle.tracking_p95_rad`
69. `joint_response.right_ankle.current_p95_a`
70. `body_response.pitch_rate_p95_rad_s`
71. `body_response.roll_rate_p95_rad_s`
72. `body_response.acceleration_norm_p95_m_s2`

No mass, COM, inertia, component identity, scale reading, caliper reading, or manual
per-build value is present. The context is reproduced from the runtime's immutable
automatic-excitation trace, metadata, and `duck_config.json`.

## Pretraining falsification

Before any PPO step, policy and runtime flatteners must be bit-exact on committed
fixtures; the profile must reproduce within `1e-9`; the protected actor must remain
bit-exact with its new branch disabled; and repeated simulator response contexts must
be deterministic. The exact signed X endpoint pair must not collapse to an identical
73-vector. A collapse closes this formulation; true configuration parameters may not
be appended as a rescue.

## Runtime review required

- Does the 73-field flatten order exactly match profile v4 production and validation?
- Can runtime supply response_context as a separate immutable ONNX input without changing obs[115]?
- Can the context be hash-bound to the raw automatic calibration evidence and selected policy envelope before arming?
- Does any current runtime path silently reorder, scale, default, or substitute a context value?
- Does the supported/benched collection posture make the profile unsuitable as a policy-conditioning input?
- Are additional sign-preserving response fields required before a signed-X identifiability screen?

## Authority

This artifact requests schema review only. It authorizes no runtime implementation,
training, Colab, GPU/iGPU, X5 or robot access, serial/GPIO/I2C, torque, motion, Gate 5,
deployment, or robot clearance.
