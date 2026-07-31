#!/usr/bin/env python3
"""Run the one preregistered applied-target-state continuation on Colab T4."""

from __future__ import annotations

from pathlib import Path

import colab_ground_up_measured_bridge_continuation as job


ASSETS = Path("/content")
job.ROOT = ASSETS / "ground_up_applied_target_playground"
job.SOURCE_ROOT = ASSETS / "ground_up_applied_target_source"
job.OUTPUT = ASSETS / "ground_up_applied_target_outputs" / "A2_APPLIED_TARGET_STATE"
job.ARTIFACT = ASSETS / "A2_APPLIED_TARGET_STATE_artifacts.tar.gz"
job.MANIFEST = ASSETS / "A2_APPLIED_TARGET_STATE_manifest.json"
job.SOURCE_CHECKPOINT = (
    job.SOURCE_ROOT
    / "A1_MEASURED_BRIDGE_ONLY"
    / "2026_07_14_164618_1003520"
)
job.SOURCE_ARCHIVE = "A1_MEASURED_BRIDGE_ONLY_artifacts.tar.gz"
job.PATCHES = (
    "ground_up_search_runner.patch",
    "ground_up_reference_conditioned.patch",
    "ground_up_recipe_search.patch",
    "ground_up_stage1_mechanism_stack.patch",
    "ground_up_nominal_reference_bootstrap.patch",
    "ground_up_signed_progress_objective.patch",
    "ground_up_reference_residual_actor.patch",
    "ground_up_hard_vector_command_support.patch",
    "ground_up_measured_actuator_bridge.patch",
    "ground_up_applied_target_observation.patch",
)
job.EXPECTED_HASHES = {
    **job.EXPECTED_HASHES,
    "ground_up_applied_target_observation.patch": "bdcac27115fcbe855079f5365ac046e863a9b302ff16f560d12a26cd492f2821",
    "A1_MEASURED_BRIDGE_ONLY_artifacts.tar.gz": "bf9116063bbd42212c7a14f0c4fb052a8f5b72dc381a35ad833f998debbcc2e8",
}
job.EXPECTED_HASHES.pop("A1_HARD_VECTOR_COMMAND_SUPPORT_artifacts.tar.gz")
job.EXTRA_TRAINING_ARGS = ("--ground_up_applied_target_observation",)
job.SCHEMA_VERSION = "ground_up_applied_target_state_colab.v1"
job.RESULT_PREFIX = "GROUND_UP_APPLIED_TARGET_RESULT="


if __name__ == "__main__":
    raise SystemExit(job.main())
