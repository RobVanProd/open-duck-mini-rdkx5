# Ground-Up Measured-Bridge-Only Continuation Result

status: `REJECT_CLOSE_FEEDFORWARD_BRIDGE_ONLY_ARM`

The single preregistered T4 continuation completed at steps
`0/1,003,520/2,007,040`. The 8,167,988-byte archive was downloaded and verified
at SHA-256
`bf9116063bbd42212c7a14f0c4fb052a8f5b72dc381a35ad833f998debbcc2e8`
before the session was stopped. Colab then reported zero active sessions.

Both post-update stateful ONNX policies were evaluated on local CPU with the
unchanged fitted bridge, deterministic home reset, x=`.074/.077/.080`, seeds
`100/101`, and the frozen 1.08-second window. Every run completed, moved
forward, retained bilateral contact transitions, stayed finite and
nonconstant, had zero saturation, and had zero target-rate excess.

| checkpoint | x | mean vx m/s | command ratio | tracking p95 rad | single support | gate |
|---:|---:|---:|---:|---:|---:|---|
| 1,003,520 | .074 | .07463 | 1.0085 | .21099 | 50.00% | hold tracking |
| 1,003,520 | .077 | .08014 | 1.0407 | .20137 | 50.00% | hold tracking |
| 1,003,520 | .080 | .08758 | 1.0947 | .18858 | 42.59% | pass |
| 2,007,040 | .074 | .07663 | 1.0355 | .20487 | 35.19% | hold tracking |
| 2,007,040 | .077 | .08793 | 1.1420 | .20332 | 46.30% | hold tracking |
| 2,007,040 | .080 | .08784 | 1.0980 | .20832 | 44.44% | hold tracking |

The unchanged tracking threshold is `<=.20 rad`. The 1M x=.08 result proves
that training inside the measured transition can clear the gate without
collapsing gait, adding penalties, violating target rates, or saturating.
However, five of six command/checkpoint cells still fail and the improvement
does not persist at 2M. The preregistration requires both checkpoints to pass
all commands, so the exact feedforward bridge-only arm is rejected. No
checkpoint selection, extra horizon, learning-rate change, reward change, or
bridge-vector tuning is permitted from this result.

The next authorized work is read-only: audit whether the actor observation
contains the causal actuator state needed to disambiguate the fitted 2-3 tick
delay and first-order lag. That audit must distinguish existing sent-action
history and actual joint state from missing applied-target/bridge history before
selecting an explicit-state or recurrent mechanism. It does not authorize
training or accelerator use.

No robot, RDK-X5, local iGPU, onboard GPU, deployment, torque, or motor access
was used or authorized.

