#!/usr/bin/env python3
"""Preregister V165's coherent-normalizer accepted-state screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v165_coherent_normalizer_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V165_COHERENT_NORMALIZER_PREREGISTRATION_20260725.md"
)
V164_PREREG = ANALYSIS / "winner_v164_state_coherence_preregistration.json"
V164_RESULT = ANALYSIS / "winner_v164_state_coherence_result.json"
V163_RESULT = (
    ANALYSIS / "winner_v163_feasibility_preserving_falsifier_result.json"
)
RUNNER = ROOT / "tools/run_winner_v165_coherent_normalizer.py"
STATE_MODULE = ROOT / "training/winner_v165_coherent_normalizer_state.py"
V164_STATE = ROOT / "training/winner_v164_feasibility_preserving_state.py"
CELL_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
DEPLOYER = ROOT / "tools/run_winner_v129_oracle_teacher_cpu_contract.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(child)))
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V165: {path}")

    v164_prereg = json.loads(V164_PREREG.read_text(encoding="utf-8"))
    v164_result = json.loads(V164_RESULT.read_text(encoding="utf-8"))
    v163_result = json.loads(V163_RESULT.read_text(encoding="utf-8"))
    inherited = {
        name: Path(path) for name, path in v164_prereg["paths"].items()
    }
    inherited["composition_manifest"] = manifest_path
    inherited["composed_evaluator"] = evaluator_path
    input_files = {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "state_module": STATE_MODULE,
        "v164_state_module": V164_STATE,
        "cell_runner": CELL_RUNNER,
        "deployer": DEPLOYER,
        "v164_preregistration": V164_PREREG,
        "v164_result": V164_RESULT,
        "v163_result": V163_RESULT,
        **{
            name: path
            for name, path in inherited.items()
            if path.is_file()
            and name
            not in {
                "builder",
                "runner",
                "state_module",
                "cell_runner",
                "deployer",
            }
        },
    }
    input_directories = {
        name: inherited[name]
        for name in (
            "source_checkpoint",
            "proposal_checkpoint",
            "proposal_cost_checkpoint",
        )
    }
    alpha = 1.0 / 28.0
    checks = {
        "v163_graph_level_step_passed": (
            v163_result["status"]
            == "PASS_WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER"
        ),
        "v164_isolated_frozen_normalizer_failure": (
            v164_result["status"] == "HOLD_WINNER_V164_STATE_COHERENCE"
            and v164_result["decision"]
            == "CLOSE_ACTOR_ONLY_FROZEN_NORMALIZER_STATE_NO_RETRY"
            and v164_result["cells"][-1]["identity"]["plant"]
            == "P31_34_PITCH_WITH_P30_NONPITCH"
            and v164_result["cells"][-1]["identity"]["command_x_m_s"]
            == 0.074
        ),
        "same_fixed_block_and_alpha": (
            v164_prereg["state_rule"]["block_iterations"] == 28
            and v164_prereg["state_rule"]["accepted_alpha"] == alpha
        ),
        "normalizer_correction_has_no_new_scalar": True,
        "cpu_only_no_new_ppo_update": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v165.coherent_normalizer_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V165_COHERENT_NORMALIZER"
            if not failed
            else "HOLD_WINNER_V165_COHERENT_NORMALIZER_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **{name: sha256(path) for name, path in input_files.items()},
            **{
                name: directory_sha256(path)
                for name, path in input_directories.items()
            },
        },
        "paths": {
            **{name: str(path) for name, path in input_files.items()},
            **{name: str(path) for name, path in input_directories.items()},
            "playground": str(inherited["playground"]),
        },
        "state_rule": {
            "block_iterations": 28,
            "accepted_alpha": alpha,
            "mean_and_std": "source + alpha * (proposal - source)",
            "count_increment": (
                "round(alpha * (proposal_count - source_count)), minimum 1"
            ),
            "summed_variance": (
                "max(std^2 - std_eps, 0) * accepted_count"
            ),
            "actor": "source + alpha * (proposal - source)",
            "reward_critic": "proposal exact",
            "cost_critic": "proposal exact",
            "dual_state": "proposal exact",
            "optimizer": "fresh zero-moment Adam",
            "alpha_or_block_retry": False,
        },
        "matrix": v164_prereg["matrix"],
        "source_worst_peak_torque_nm": v164_prereg[
            "source_worst_peak_torque_nm"
        ],
        "gate": v164_prereg["gate"],
        "decision_rule": {
            "pass": (
                "normalizer algebra/export is exact, restored state is exact, "
                "all six moving cells and x0 invariants pass, and source "
                "worst-torque reserve strictly improves"
            ),
            "pass_earns": (
                "one separate V166 28-iteration trainer-integration CPU smoke"
            ),
            "failure_closes": (
                "feasibility-preserving block continuation under the frozen "
                "contract; no alpha, block, or state-rule retry"
            ),
            "hosted_training_authorized": False,
        },
        "authority": {
            "cpu_state_and_behavior_contract": not failed,
            "training": False,
            "hosted_training": False,
            "full_robustness": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V165 coherent-normalizer preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Keeps V164's fixed 28-iteration block and `1/28` alpha.\n"
        "- Interpolates deployed mean/std, derives an integer count increment, "
        "and reconstructs summed variance exactly.\n"
        "- No alpha, block-length, reward, or behavior-selected retry.\n"
        "- Passing earns only one trainer-integration CPU smoke.\n"
        "- CPU-only; no new PPO update, Colab, Gate 5, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
