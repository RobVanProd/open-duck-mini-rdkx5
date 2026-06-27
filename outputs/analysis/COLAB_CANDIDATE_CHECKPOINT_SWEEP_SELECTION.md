# Colab Candidate Checkpoint Sweep Selection

status: `PASS_GATE_ALIGNED_SELECTION_PLUMBING_READY`

## Summary

The A100 PPO warm-start and behavior-prior runs both increased training reward
while regressing the candidate gates. The failure mode was not GPU execution or
checkpoint export; it was reward-only checkpoint selection.

`tools/run_colab_cli_cuda_workflow.py` now runs a compact fitted-bridge
checkpoint sweep after candidate training exports ONNX files. If any exported
checkpoint passes the compact sweep, that checkpoint is selected for the normal
final x=0.0 and x=0.08 candidate gates instead of blindly using the latest
reward checkpoint.

This is offline-only infrastructure. It does not train by itself, SSH, deploy,
touch the robot, or change runtime behavior.

## Default Compact Sweep

```text
commands: 0.0, 0.08
duration: 1.0 s
bridge: fitted
platform: gpu in Colab
sim preflight timeout: 600 s
closed-loop timeout: 1800 s
```

The final candidate gates still use the normal longer gate path after selection.

## New Flags

```bash
--candidate-checkpoint-sweep
--no-candidate-checkpoint-sweep
--candidate-checkpoint-sweep-commands 0.0,0.08
--candidate-checkpoint-sweep-duration 1.0
--candidate-checkpoint-sweep-timeout-s 7200
```

## Selection Rule

```text
1. Train candidate and collect exported ONNX checkpoints.
2. Run tools/sweep_candidate_checkpoints.py over all exported ONNX files.
3. If any checkpoint has PASS_PROMOTE_CANDIDATE_CHECKPOINT, select the top
   promoted checkpoint.
4. If none promote, record the best available decision but do not treat it as
   a robot candidate.
5. Run the normal final x=0.0 and x=0.08 gates on the selected checkpoint.
```

The selected checkpoint metadata is written to:

```text
<colab-output>/<candidate_name>_selected_checkpoint.json
```

## Validation

```text
python3 -m py_compile tools/run_colab_cli_cuda_workflow.py tools/sweep_candidate_checkpoints.py
python3 tools/run_colab_cli_cuda_workflow.py --help
generated remote driver AST parse smoke
```

No robot tests were run.
