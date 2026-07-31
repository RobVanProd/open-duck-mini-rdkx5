# Winner-v113 post-export transform contract

Status: `PASS_WINNER_V113_POSTEXPORT_TRANSFORM_CONTRACT`

Both post-update V112 ONNX graphs retain every learned node and initializer, then append the already-frozen G3 actual-centered guard and exact x=0 deadband. No behavior, Gate 5, robot, torque, or motion is authorized by this transform.
