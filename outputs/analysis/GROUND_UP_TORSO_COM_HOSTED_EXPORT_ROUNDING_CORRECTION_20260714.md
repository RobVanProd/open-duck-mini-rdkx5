# Ground-Up Torso-COM Hosted Export-Rounding Correction

status: `REPORTING_CONTRACT_CORRECTION_ONLY`

The first corrected remote invocation passed source composition, patch, syntax,
dependency, and CUDA-device checks, then completed the frozen 2,000,000-step
`U05_DIRECT` training command. It stopped after training when the package
expected checkpoint/ONNX names `0/1024000/2048000` but observed exactly:

- checkpoints: `0/1003520/2007040`;
- ONNX exports: `0/1003520/2007040`.

Those observed steps match the established rounding of prior hosted jobs with
the same 256-environment PPO batch shape. The incorrect values came from the
four-environment CPU smoke and did not alter training, parameters, commands,
randomization, seed, or selection criteria.

The correction changes only predicted hosted export names to
`0/1003520/2007040` for each direct 2M arm, `0/501760` for each 500k curriculum
stage, and `0/501760/1003520` for its final 1M stage. `U05_DIRECT` must be
resumed from its already completed exact exports and must not be retrained.
The full CPU package checker must pass again before resume.
Because `colab exec` does not forward ordinary script arguments, the job also
defaults to resume mode only when its output root already exists; every reused
stage still has to pass the corrected exact checkpoint and ONNX step assertion.
