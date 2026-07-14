# Ground-Up Stage-1 Mixture 4M Result

Status: `PASS_FINITE_SCAFFOLD_HOLD_GAIT_NOT_EMERGED`

STAGE1MIX4 retained the reference-velocity frame correction and implemented
the preregistered 50/50 exact-zero versus positive-forward command mixture.
It used the same canonical PPO recipe, seed, task, and 4,014,080-step horizon
as the two controls.

- Artifact SHA-256: `9c54c49e85dd8b5667a26e45da1e23c71322ffd450a398aa33d69fb99ff3a934`
- Minimal-tree command patch SHA-256: `17912ed37aceb430977daa2eead8ca24da7b20a03b220417d609bab368a0c6a3`
- T4 training time: `1133.1868700240002 s`
- Five checkpoints/ONNX exports; VM stopped after verified download

## Evidence

Unlike R00W4 and FRAMEFIX4, every x=0 and x=0.08 run completed at both the 3M
and 4M checkpoints. This is a real stability improvement and satisfies the
first elimination criterion.

It did not satisfy gait emergence:

| checkpoint | x=.08 seed | world dx m | mean local vx m/s | finite |
|---:|---:|---:|---:|---|
| 3,010,560 | 100 | -0.038710 | -0.050058 | yes |
| 3,010,560 | 101 | -0.133560 | -0.064107 | yes |
| 4,014,080 | 100 | -0.025762 | -0.040232 | yes |
| 4,014,080 | 101 | 0.091137 | -0.178887 | yes |

The x=0 runs are only classified as finite at this emergence stage. Their
nontrivial drift remains a later hard-gate failure and is not being ignored.

## Decision

The corrected stage-1 mixture is the best tested *training scaffold* on the
first hard gate, not a candidate policy and not proof of the best PPO recipe.
All tested 4M checkpoints are immature by the frozen forward-motion evidence.
Architecture-family ranking at this horizon would be arbitrary.

The next run must extend this exact scaffold far enough to measure gait
emergence, with intermediate checkpoints and the same CPU evaluator. No policy
may advance on reward alone. No robot, RDK, onboard GPU, or local accelerator
is authorized.
