# Phase-Conditioned Action Outcome Cohorts

status: `PASS_PHASE_ACTION_OUTCOME_COHORT_ANALYSIS_READY`

Offline analysis only. No training, simulation, deployment, robot access,
local GPU, or Colab allocation was performed.

## Cohorts

Cohorts are rank-defined from measured manifest mean velocity; no behavior
threshold was chosen after inspecting joint actions.

| cohort | seed | mean vx (m/s) |
|---|---:|---:|
| low | 3 | -0.045488 |
| low | 6 | 0.011378 |
| low | 1 | 0.025715 |
| high | 2 | 0.051730 |
| high | 4 | 0.054360 |
| high | 5 | 0.058277 |

## Contact Occupancy

| cohort | neither | right only (01) | left only (10) | double (11) |
|---|---:|---:|---:|---:|
| low | 2.00% | 17.33% | 12.67% | 68.00% |
| high | 1.33% | 8.67% | 10.00% | 80.00% |

## Phase-Conditioned Action Differences

A linear harmonic model uses the policy's two phase observations. The
between/within ratio ranks cohort separation relative to seed variation.

| joint | waveform between RMS | within RMS | ratio | intercept delta | harmonic RMS delta |
|---|---:|---:|---:|---:|---:|
| `left_knee` | 0.03923 | 0.01265 | 3.100 | +0.01774 | 0.03498 |
| `right_hip_yaw` | 0.02019 | 0.01193 | 1.692 | +0.01754 | 0.00999 |
| `left_ankle` | 0.03835 | 0.02273 | 1.687 | +0.01716 | 0.03429 |
| `head_roll` | 0.01582 | 0.01024 | 1.545 | -0.00906 | 0.01296 |
| `left_hip_yaw` | 0.01759 | 0.01216 | 1.446 | +0.01011 | 0.01439 |
| `right_hip_roll` | 0.01176 | 0.00851 | 1.382 | -0.00723 | 0.00927 |
| `right_hip_pitch` | 0.02758 | 0.02089 | 1.320 | -0.01071 | 0.02542 |
| `head_pitch` | 0.01640 | 0.01361 | 1.206 | +0.00823 | 0.01419 |
| `left_hip_pitch` | 0.03914 | 0.03250 | 1.204 | -0.03674 | 0.01350 |
| `neck_pitch` | 0.01427 | 0.01223 | 1.167 | +0.01361 | 0.00429 |
| `left_hip_roll` | 0.01651 | 0.01439 | 1.147 | +0.01177 | 0.01157 |
| `head_yaw` | 0.02279 | 0.02614 | 0.872 | -0.01128 | 0.01980 |
| `right_ankle` | 0.00999 | 0.01152 | 0.867 | +0.00360 | 0.00932 |
| `right_knee` | 0.01432 | 0.01824 | 0.785 | -0.01295 | 0.00612 |

## Existing Teacher Alignment on Low-Progress States

Cosine alignment compares the teacher correction with the empirical
low-to-high phase-action direction. +1 is aligned, 0 orthogonal, and -1
opposed.

| scope | mean cosine | median | positive samples | mean projection |
|---|---:|---:|---:|---:|
| all joints | -0.00304 | +0.02215 | 52.00% | +0.0000275 |
| pitch chain | +0.00670 | -0.02733 | 48.00% | +0.0000384 |

## Interpretation

The observed outcome separation is concentrated in phase-conditioned
pitch-chain behavior, especially the left knee and ankle. Contact
occupancy alone does not separate success: the high cohort has more, not
less, double support. The existing teacher correction is approximately
orthogonal to the empirical low-to-high action direction and therefore
does not encode a coherent outcome-aligned correction on these states.

## Empirical Full-Delta Offline Screen

Adding the measured cohort phase delta to the low-cohort actions, with
the registered pitch-chain temporal projection, gives:

- correction mean/p95/max: `0.01889` / `0.05114` / `0.06721`
- pitch target-rate p95/max: `1.52611` / `1.97267` rad/s

This is a screen, not a new teacher target. The high-cohort waveform must
not be applied counterfactually without state-matched safety evidence.

## Limitations

- Eight traces and rank-defined cohorts provide hypothesis evidence, not causality.
- Phase regression summarizes observed actions; it does not prove that applying the high-cohort waveform to low states is safe or effective.
- Teacher alignment is a directional screen and does not replace closed-loop evaluation.
