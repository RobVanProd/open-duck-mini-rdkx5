# Phase 2 Trainable Policy Branch Decision

status: `HOLD_TASK_MATCHED_TRAINABLE_POLICY_MISSING`

## Executive Summary

Phase 2 has in-envelope deployable walkers, but no trainable PPO/DR warm-start currently preserves the z=0.0075 rough+push behavior. BC-only live-oracle continuation is closed as-is, and long domain-randomization training should not launch until a task-matched step-0 trainable policy clears the gate.

Robot validation remains blocked. No robot tests, SSH, deployment, grounded replay, runtime behavior change, or training was performed by this reporter.

## Current Evidence

### Deployable Boundary

- status: `HOLD_PHASE2_Z0075_INTERMEDIATE_PUSH_STABILITY`
- policy: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- duration_complete_count: `6`
- fall_count: `2`
- mean track ratio: `0.5622310372021643`
- mean vx: `0.04497848297617314`
- max tracking p95: `0.20070266723632812`
- max p95 velocity excess: `0.0`
- max instantaneous velocity excess: `1.326827049255371`

Interpretation: this is useful deployable behavior, but the harder z=0.0075 intermediate-push boundary is still a hold, not a promotion gate.

### Live-Oracle BC Loop

- Iter24 status: `HOLD_ITER24_LIVE_ORACLE_SEED6_REGRESSION`
- Iter24 candidate: `policy/candidates/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_20260704/candidate.onnx`
- Iter24 compact pass/fall: `4` / `1`
- Iter27 status: `HOLD_ITER27_LIVE_ORACLE_MULTI_SEED_REGRESSION`
- Iter27 candidate: `policy/candidates/phase2_z0075_iter27_live_oracle_seed6_active_history_context_rate150_20260705/candidate.onnx`
- Iter27 compact pass/fall: `2` / `3`
- Iter27 max velocity-envelope excess: `0.0`

Interpretation: Iter27 regressed relative to Iter24. Continuing the same BC-only live-oracle rung as-is is closed for now.

### PPO-Compatible Warm-Starts

- trainable screen status: `HOLD_NO_TASK_MATCHED_TRAINABLE_WARMSTART`
- candidate count: `3`

| candidate | pass/total | falls | track ratio mean | mean vx | decision |
|---|---:|---:|---:|---:|---|
| `limit198_step0` | `0/5` | `2` | `0.1630371513828402` | `0.013042972110627212` | Not promotable. Safer but too slow under the current z0.0075 push gate and falls on seeds 6 and 7. |
| `rate165_step0` | `0/5` | `3` | `1.1016063929905697` | `0.08812851143924558` | Not promotable. Moves aggressively but falls early on seeds 0, 1, and 2. |
| `ppo_loc_iter24_step0` | `2/5` | `None` | `None` | `None` | Not promotable. Good action fidelity and close manifest coverage, but closed-loop seed stability regresses. |

- PPO trace status: `HOLD_PPO_LOC_STEP0_CLOSED_LOOP_INSTABILITY`
- PPO trace policy: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0.onnx`
- nearest distance p95 max: `0.3356696694682808`
- nearest action L1 p95 max: `0.027115175581752707`

Interpretation: the PPO-loc regression is not explained by missing local manifest coverage or a large local action-fit error. The failed step-0 checkpoint is not a valid DR parent.

## Decision

Do not launch long Phase 2 domain-randomization training from any current PPO-compatible checkpoint. First produce a task-matched trainable policy whose step-0 export clears the z=0.0075 rough+push corrected-bridge gate.

Required next conditions before DR escalation:

- Use Iter24 as the latest useful deployable analysis baseline, not Iter25/26/27.
- Do not continue scalar anchor weighting or BC-only live-oracle relabeling as the next default branch.
- Build a trainable policy class/objective that preserves the deployable baseline under the canonical z=0.0075 push gate before any DR escalation.
- Acceptable next branches: recurrent/hidden-state actor with explicit export, validation-aware mixture/ensemble diagnostic, or PPO fine-tuning only after a task-matched behavior-preserving step-0 gate passes.

## Gate To Reopen Training

A new trainable parent must pass, at minimum:

- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- reset: `home-support`, `reset_settle_ticks=10`
- bridge: corrected fitted actuator bridge
- command: `x=0.08`
- push: `0.075-0.125`, interval `1.0-1.5s`
- seeds: `0,1,2,6,7` compact screen before full 8-seed promotion
- corrected velocity-envelope excess: `0`

Only after this step-0 behavior-preservation gate passes should staged domain randomization resume.
