# Ground-Up Tracking-Tail Colab Package Check

status: `PASS_COLAB_PACKAGE_CONTRACT`

failed checks: `none`
arms: `[('T1_QUARTER', -1643.0637410077638), ('T2_EQUAL', -6572.254964031055), ('T3_FOUR', -26289.01985612422)]`
expected exports per arm: `[0, 512000, 1024000]`
maximum hosted wall time: `14400` seconds
maximum compute at reported 1.07 CU/hour: `4.28` CU

Every arm independently restores the same protected 1M checkpoint. This check authorizes the fixed hosted package only; behavior remains unevaluated and no robot, RDK-X5, deployment, or local GPU access follows.
