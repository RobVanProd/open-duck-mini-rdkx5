#!/usr/bin/env python3
"""Rank an equal-window ground-up recipe rung using frozen offline gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_candidate(value: str) -> tuple[str, list[Path]]:
    candidate_id, separator, paths = value.partition("=")
    if not separator or not candidate_id or not paths:
        raise argparse.ArgumentTypeError("candidate must be ID=EVAL.json,EVAL.json")
    return candidate_id, [Path(path) for path in paths.split(",")]


def summarize(candidate_id: str, paths: list[Path]) -> dict[str, object]:
    checkpoints: list[dict[str, object]] = []
    moving_pass_seeds_by_checkpoint: list[set[int]] = []
    for path in paths:
        payload = json.loads(path.read_text())
        runs = payload["runs"]
        zero_runs = [run for run in runs if float(run["command_x"]) == 0.0]
        moving_runs = [run for run in runs if float(run["command_x"]) > 0.0]
        zero_finite = sum(
            run.get("error") is None
            and run["emergence"]["termination_reason"] == "duration_complete"
            for run in zero_runs
        )
        moving_pass_seeds = {
            int(run["seed"]) for run in moving_runs if run["emergence"]["pass"]
        }
        moving_pass_seeds_by_checkpoint.append(moving_pass_seeds)
        hard_failures = sum(
            run.get("error") is not None
            or run["emergence"]["termination_reason"] != "duration_complete"
            or run["emergence"].get("constant_saturated_action_vector", False)
            for run in runs
        )
        checkpoints.append({
            "path": str(path),
            "policy_sha256": payload["inputs"]["policy_sha256"],
            "checkpoint_emergence_pass": bool(payload["aggregate"]["checkpoint_emergence_pass"]),
            "zero_finite_runs": zero_finite,
            "zero_runs": len(zero_runs),
            "moving_pass_runs": len(moving_pass_seeds),
            "moving_runs": len(moving_runs),
            "moving_pass_seeds": sorted(moving_pass_seeds),
            "hard_failures": hard_failures,
        })

    persistent_moving_seeds = (
        set.intersection(*moving_pass_seeds_by_checkpoint)
        if moving_pass_seeds_by_checkpoint else set()
    )
    score = {
        "full_checkpoint_passes": sum(item["checkpoint_emergence_pass"] for item in checkpoints),
        "zero_finite_runs": sum(item["zero_finite_runs"] for item in checkpoints),
        "moving_pass_runs": sum(item["moving_pass_runs"] for item in checkpoints),
        "persistent_moving_seeds": len(persistent_moving_seeds),
        "hard_failures": sum(item["hard_failures"] for item in checkpoints),
    }
    score_key = [
        -score["hard_failures"],
        score["full_checkpoint_passes"],
        score["zero_finite_runs"],
        score["moving_pass_runs"],
        score["persistent_moving_seeds"],
    ]
    return {
        "candidate_id": candidate_id,
        "checkpoints": checkpoints,
        "score": score,
        "score_key": score_key,
        "persistent_moving_seeds": sorted(persistent_moving_seeds),
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Ground-Up Recipe Rung Ranking",
        "",
        f"status: `{payload['status']}`",
        "",
        "Training reward is excluded. Equal score keys remain tied.",
        "",
        "| rank | candidate | full checkpoints | zero finite runs | moving passes | persistent moving seeds | hard failures |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for item in payload["ranking"]:
        score = item["score"]
        lines.append(
            f"| {item['rank']} | `{item['candidate_id']}` | "
            f"{score['full_checkpoint_passes']} | {score['zero_finite_runs']} | "
            f"{score['moving_pass_runs']} | {score['persistent_moving_seeds']} | "
            f"{score['hard_failures']} |"
        )
    lines.extend(["", "This ranking is a recipe-search result, not policy or robot clearance.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", required=True, type=parse_candidate)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    if len({candidate_id for candidate_id, _ in args.candidate}) != len(args.candidate):
        raise SystemExit("candidate IDs must be unique")
    counts = {len(paths) for _, paths in args.candidate}
    if len(counts) != 1:
        raise SystemExit("all candidates must have the same number of evaluated checkpoints")

    summaries = [summarize(candidate_id, paths) for candidate_id, paths in args.candidate]
    summaries.sort(key=lambda item: item["score_key"], reverse=True)
    previous_key: list[int] | None = None
    rank = 0
    for index, item in enumerate(summaries, start=1):
        if item["score_key"] != previous_key:
            rank = index
            previous_key = item["score_key"]
        item["rank"] = rank
    payload = {
        "schema_version": "ground_up_recipe_rung_ranking.v1",
        "status": "RANKED_EQUAL_WINDOW_OFFLINE_EVIDENCE",
        "selection_uses_training_reward": False,
        "ranking": summaries,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text(render_markdown(payload))
    print(json.dumps({"status": payload["status"], "ranking": [
        {"candidate_id": item["candidate_id"], "rank": item["rank"], "score": item["score"]}
        for item in summaries
    ]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
