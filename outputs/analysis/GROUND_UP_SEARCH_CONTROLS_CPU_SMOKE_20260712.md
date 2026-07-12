# Ground-Up Search Controls CPU Smoke

status: `PASS_SEARCH_CONTROLS_CPU_SMOKE`

The combined search-runner patch applies cleanly to the pinned upstream commit
and exposes only PPO scale, imitation scale, and critic observation selection.
It does not change the environment or reward implementation itself.

A CPU smoke with `critic_observation=state` and `imitation_scale=0.5` completed
at step `1,280`, produced step-0 and final checkpoints, exported both ONNX
files, and reported evaluation reward `13.39878 +/- 5.75314`.

This proves wiring only. The immature action is near saturation and is not a
candidate. No robot, GPU, Colab, deployment, or hardware action occurred.
