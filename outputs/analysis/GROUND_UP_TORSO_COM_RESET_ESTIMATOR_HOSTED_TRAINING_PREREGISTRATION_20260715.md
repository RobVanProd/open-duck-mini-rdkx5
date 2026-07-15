# Ground-Up Torso-COM Reset-Estimator Hosted Training Preregistration

status: `PREREGISTERED_HOSTED_PACKAGE_CONTRACT_REQUIRED`

## Evidence-selected question

The corrected torso-COM exposure search falsified missing axis exposure as a
sufficient explanation. The deterministic reset signal is decodable, the
frozen three-anchor estimator passes eight held-out offsets with 1.214 mm
worst error, and the `RESET_EST_LATCH_U05` CPU package contract passes exact
checkpoint, observation-layout, latch, and default-off checks.

The next falsifiable question is therefore singular: can the protected T2
feedforward policy learn the same frozen full-range task when the reset COM
estimate is explicitly observable and held for the episode? This does not
select recurrence, a new objective, a new optimizer, a second arm, or a new
recipe search.

## Frozen upstream evidence

- estimator-input CPU package contract JSON SHA-256:
  `00e152e469e8fdeba49d7031c259b688f722ea75764297cb7ea51431d9fc2914`;
- local checkpoint-expansion JSON SHA-256:
  `e5e7a3e8e34e7cc2ed511828d0e5323aed44d5e2d384082d31718ebb0a42b09c`;
- estimator-input patch SHA-256:
  `2758898a09ef487d5a6949b9aaafda3db9f00c10976136bd6f5c3e9e7a75a4e8`;
- protected source archive `GROUND_UP_TRACKING_TAIL_artifacts.tar.gz`
  SHA-256:
  `ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f`;
- protected raw checkpoint member:
  `ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190425_1024000`;
- frozen reference feature table SHA-256:
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`;
- frozen reference-residual actor source SHA-256:
  `546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630`.

## Frozen hosted topology expansion

The local expanded checkpoint is CPU-topology evidence and must not be assumed
portable to a hosted GPU. In the hosted process, after CUDA JAX is verified,
restore the protected raw checkpoint on that GPU and apply exactly the
contracted index-101 expansion:

- normalizer state and privileged state: insert mean 0, std 1, summed variance
  8,048,640;
- preserve count `{hi:0,lo:8048640}` and `std_eps=0`;
- actor first kernel `(115,512)`: insert one all-zero row at 101;
- critic first kernel `(226,512)`: insert one all-zero row at 101;
- preserve every other value exactly.

Save and restore the expanded checkpoint on the same hosted topology. Before
training, require 116/227-D shapes, exact inserted values, zero new rows,
bit-exact collapse to the protected source, bit-exact hosted save/restore, and
actor/critic step-zero error `<=1e-7` for `z={-1,0,+1}` with the final 14 raw
reference-action inputs unchanged. Any failure stops before PPO.

## Frozen single arm

Arm: `RESET_EST_LATCH_U05`.

- restore only the hosted-expanded protected T2 checkpoint;
- seed 100;
- uniform targeted name-resolved `trunk_assembly` X-COM offset
  `[-.05,+.05]` throughout;
- 2,000,000 requested continuation steps in one uninterrupted optimizer run;
- expected exports at actual steps 0, 1,003,520, and 2,007,040;
- reference-residual actor, privileged critic, phase 0, deterministic home
  reset, x-command support `[.074,.080)`, measured actuator bridge,
  applied-target observation, signed progress, and tracking-tail scale
  `-6572.254964031055`;
- LR `.0003`, discount `.97`, entropy `.005`, 256 environments, episode 600,
  unroll 20, batch 256, four minibatches, four updates;
- action velocity limits
  `5.24,5.24,1.50,1.50,1.50,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25`;
- fitted bridge delays
  `3,3,3,3,3,3,2,3,3,3,2,3,2,3` and taus
  `.015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005`;
- noise, unrelated dynamics axes, pushes, and terrain disabled.

The exact `U05_DIRECT` recipe is otherwise unchanged. No reward, seed, LR,
checkpoint, schedule, command, reset, bridge, horizon, architecture,
estimator, insertion index, normalization, or randomizer change is permitted
after outcomes. There is no second arm and no retry.

## Hosted limits and artifact contract

Only one hosted session and one training process may be used. Setup time and
failures count. Freeze a 2,400-second job wall ceiling and a 2.0 Colab compute-
unit ceiling. The prior three-arm run took 3,272.11 seconds total and its two
direct 2M arms took 848.30 and 787.03 training seconds, so this is a bounded
ceiling, not a performance estimate.

On success, atomically produce and recover:

- the hosted expansion report and hosted-expanded step-zero checkpoint;
- all three Orbax checkpoints and all three ONNX exports;
- complete stdout/training log and manifest with exact command, versions,
  CUDA devices, wall time, source/asset hashes, export steps, file hashes, and
  behavior status `UNEVALUATED`;
- one compressed archive of the complete output tree with SHA-256 and byte
  count.

The session must be stopped after artifacts are recovered and locally hash-
validated. A partial, timed-out, missing-export, topology-expansion failure, or
over-budget run is a failed arm; it is not resumed or retried.

## Frozen later evaluation and decision

Training reward and hosted eval reward have no selection weight. After a
separate local artifact contract, apply the already contracted graph-baked
actual-position guard, x=0 deadband, and conservative left-ankle envelope to
the two post-update full-range exports. A separate behavior authority must then
run the unchanged complete R1 plus COM-NEG and COM-POS matrix under both fits,
600 ticks per cell, deterministic home reset, exact per-run model readback,
bilateral gait, zero saturation/rate excess, tracking p95 `<=.20 rad`, and all
prior nominal/x=0 thresholds.

The arm advances only if both 1,003,520 and 2,007,040 checkpoints pass every
cell. Otherwise close it without retry, midpoint, closest-checkpoint promotion,
or reward selection. Even a pass is not robot clearance and authorizes only a
separate next preregistration.

## Required pre-session contract and authority boundary

Before any hosted session, a committed CPU-only package contract must verify:

1. exact preregistration, upstream result, archive, patch, helper, feature
   table, and composed-source hashes;
2. the single arm, exact recipe, export steps, wall/compute ceilings, no-resume
   rule, and atomic artifact manifest logic;
3. hosted expansion source equivalence to the passing local expansion, using
   the CPU-remapped protected checkpoint without training;
4. successful asset-only validation and source-checkpoint member extraction;
5. zero training steps, zero Colab sessions, CPU-only execution, and no local
   GPU/iGPU, RDK-X5, or robot access during the contract.

This preregistration authorizes only construction and CPU validation of that
hosted package. It does not authorize launching Colab, allocating compute,
running PPO, behavior evaluation, R2/R3, runtime design, GPU/iGPU access,
RDK-X5, robot access, deployment, torque, or motors. A passing committed
package contract may support a separate explicit hosted-run authorization; it
does not itself start or authorize the run.
