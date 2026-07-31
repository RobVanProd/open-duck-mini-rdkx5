# Soft-Prior Playground Patch Verification

status: `PASS_SOFT_PRIOR_PLAYGROUND_PATCH_APPLIED`

## Scope

The default-off soft-prior training hook was applied to the sibling
`Open_Duck_Playground` checkout on branch:

```text
codex/forward-progress-reward
```

Playground PR:

```text
https://github.com/RobVanProd/Open_Duck_Playground/pull/4
```

Playground commit:

```text
11ebae1 training: add default-off soft prior reward
```

## Files Changed In Playground

```text
playground/open_duck_mini_v2/joystick.py
playground/open_duck_mini_v2/runner.py
```

The patch adds:

```text
--enable_soft_prior
--soft_prior_config_json
--soft_prior_scale
--soft_prior_huber_delta
--soft_prior_phase_source
```

and a default-off `soft_prior` reward/diagnostic term.

## Verification

Source validation:

```text
../envs/open-duck-playground/bin/python -m py_compile \
  playground/open_duck_mini_v2/joystick.py \
  playground/open_duck_mini_v2/runner.py

git diff --check
git diff --cached --check
```

Patch helper idempotence:

```text
python3 tools/prepare_training_soft_prior_patch.py \
  --playground-path ../Open_Duck_Playground
```

Result:

```text
PASS_ALREADY_PATCHED
```

Runner flag exposure was verified through `runner.py --help`.

Runner config-load smoke was run without training, with CPU-forced JAX, and
loaded:

```text
soft_prior_enable: True
soft_prior_period: 50
soft_prior_joint_indices: [2, 3, 4, 11, 12, 13]
soft_prior_rows: 50
soft_prior_scale: -0.05
obs_size: 101
action_size: 14
```

## Safety

No robot tests, SSH, deployment, robot runtime behavior changes, policy file
changes, or training runs were performed for this patch verification.

The hook remains default-off unless `--enable_soft_prior` and a compact config
JSON are passed explicitly.
