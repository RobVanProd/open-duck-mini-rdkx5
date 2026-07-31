# Winner-v97 mechanics numeric correction result

Status: `PASS_WINNER_V97_MECHANICS_NUMERIC_CORRECTION`

JSON SHA-256: `f163eb084f58b3e663d176d13d93b3481633bf09216d8b5dd10ddd0a27c13d58`

V97 changed no network, weight, seed, policy source, calibrator source, population,
or ONNX artifact. All four regenerated graphs are byte-identical to V96. The four
signed calibration traces remain exact to V92; same-plant signed context separation
is `0.15523325` for P30 and `0.15520260` for P31/34. The 1,200-tick same-input
maximum is `2.3841858e-7`, and the 256-case stress maximum rate excess is
`1.4901161e-7`, both below the independently frozen `1e-6` cross-CPU tolerance.
JAX/ONNX hidden error is below `9e-11`, adapter-delta error is below `1.5e-11`,
and independent final-action composition error is exactly zero.

This pass authorizes only a separately preregistered response-conditioned locomotion
training experiment. It does not authorize training by itself, deployment, Gate 5,
robot access, or robot clearance.
