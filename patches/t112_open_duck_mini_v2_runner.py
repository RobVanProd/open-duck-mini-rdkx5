"""Runs training and evaluation loop for Open Duck Mini V2."""

import argparse
import jax.numpy as jp

from playground.common import randomize
from playground.common import winner_v3_variable_configuration as winner_v3
from playground.common.runner import BaseRunner
from playground.open_duck_mini_v2 import joystick, standing


class OpenDuckMiniV2Runner(BaseRunner):

    def __init__(self, args):
        super().__init__(args)
        available_envs = {
            "joystick": (joystick, joystick.Joystick),
            "standing": (standing, standing.Standing),
        }
        if args.env not in available_envs:
            raise ValueError(f"Unknown env {args.env}")

        self.env_file = available_envs[args.env]

        self.env_config = self.env_file[0].default_config()
        if args.imitation_scale is not None:
            self.env_config.reward_config.scales.imitation = args.imitation_scale
        self.env_config.reference_feature_table_path = args.reference_feature_table_path
        if args.policy_architecture in (
            "recurrent",
            "reference_residual_recurrent_adapter",
            "response_conditioned_reference_residual",
        ):
            self.env_config.recurrent_hidden_dim = args.recurrent_hidden_size
        self.env_config.ground_up_command_curriculum = args.ground_up_command_curriculum
        self.env_config.nominal_reference_bootstrap = args.nominal_reference_bootstrap
        self.env_config.nominal_reference_command_x = args.nominal_reference_command_x
        self.env_config.ground_up_hard_vector_command_support = (
            args.ground_up_hard_vector_command_support
        )
        self.env_config.ground_up_command_support_range = [
            args.ground_up_command_support_min_x,
            args.ground_up_command_support_max_x,
        ]
        if not (
            args.ground_up_command_support_min_x
            < args.ground_up_command_support_max_x
        ):
            raise ValueError("ground-up command support requires min_x < max_x")
        limits = [
            float(value)
            for value in args.ground_up_action_velocity_limits_rad_s.split(",")
        ]
        if len(limits) != 14 or any(value <= 0.0 for value in limits):
            raise ValueError("ground-up action velocity limits must be 14 positive values")
        self.env_config.ground_up_action_velocity_limits_rad_s = limits
        self.env_config.ground_up_measured_actuator_bridge = (
            args.ground_up_measured_actuator_bridge
        )
        self.env_config.ground_up_applied_target_observation = (
            args.ground_up_applied_target_observation
        )
        self.env_config.reward_config.scales.tracking_tail_exceedance = (
            args.ground_up_tracking_tail_exceedance_scale
        )
        self.env_config.ground_up_tracking_tail_threshold_rad = (
            args.ground_up_tracking_tail_threshold_rad
        )
        self.env_config.reward_config.scales.peak_torque_exceedance = (
            args.ground_up_peak_torque_exceedance_scale
        )
        self.env_config.reward_config.scales.linear_peak_torque_exceedance = (
            args.ground_up_linear_peak_torque_exceedance_scale
        )
        self.env_config.ground_up_peak_torque_threshold_nm = 1.91229675
        delay_ticks = [
            int(value)
            for value in args.ground_up_actuator_bridge_delay_ticks.split(",")
        ]
        if len(delay_ticks) != 14 or any(value < 0 for value in delay_ticks):
            raise ValueError("ground-up actuator bridge delays must be 14 nonnegative integers")
        tau_s = [
            float(value)
            for value in args.ground_up_actuator_bridge_tau_s.split(",")
        ]
        if len(tau_s) != 14 or any(value <= 0.0 for value in tau_s):
            raise ValueError("ground-up actuator bridge taus must be 14 positive values")
        self.env_config.ground_up_actuator_bridge_delay_ticks = delay_ticks
        self.env_config.ground_up_actuator_bridge_tau_s = tau_s
        self.env_config.reference_start_phase = args.reference_start_phase
        self.env_config.ground_up_signed_progress_objective = (
            args.ground_up_signed_progress_objective
        )
        self.env_config.winner_v3_variable_configuration = (
            args.winner_v3_variable_configuration
        )
        self.env_config.winner_v3_deviation_scale = args.winner_v3_deviation_scale
        self.env_config.winner_v119_train_transition_match = (
            args.winner_v119_train_transition_match
        )
        self.env_config.winner_t19_support_trainthrough = (
            args.winner_t19_support_trainthrough
        )
        self.env_config.winner_t31_action_margin_trainthrough = (
            args.winner_t31_action_margin_trainthrough
        )
        if (
            args.winner_t31_action_margin_trainthrough
            and not args.winner_t19_support_trainthrough
        ):
            raise ValueError(
                "T31 action-margin train-through requires T19 support "
                "train-through"
            )
        if (
            args.winner_t37_freeze_observation_normalizer
            and not args.winner_t31_action_margin_trainthrough
        ):
            raise ValueError(
                "T37 frozen observation normalizer requires T31 "
                "action-margin train-through"
            )
        if args.winner_t66_endpoint_core_continuation and not (
            args.winner_t37_freeze_observation_normalizer
            and args.winner_t31_action_margin_trainthrough
            and args.winner_t19_support_trainthrough
            and args.winner_v3_variable_configuration
            and args.policy_architecture
            == "reference_residual_recurrent_adapter"
        ):
            raise ValueError(
                "T66 requires the frozen-normalizer T31/T19 recurrent "
                "variable-configuration contract"
            )
        if args.winner_t77_endpoint_joint_adapter_continuation and not (
            args.winner_t37_freeze_observation_normalizer
            and args.winner_t31_action_margin_trainthrough
            and args.winner_t19_support_trainthrough
            and args.winner_v3_variable_configuration
            and args.policy_architecture
            == "reference_residual_recurrent_adapter"
            and not args.winner_t66_endpoint_core_continuation
        ):
            raise ValueError(
                "T77 requires the frozen-normalizer T31/T19 recurrent "
                "variable-configuration contract without the T66 update mask"
            )
        if args.winner_t98_hidden_expert_continuation and not (
            args.winner_t37_freeze_observation_normalizer
            and args.winner_t31_action_margin_trainthrough
            and args.winner_t19_support_trainthrough
            and args.winner_v3_variable_configuration
            and args.policy_architecture
            == "reference_residual_recurrent_adapter"
            and not args.winner_t66_endpoint_core_continuation
            and not args.winner_t77_endpoint_joint_adapter_continuation
            and args.winner_t98_hidden_gate_asset_path is not None
        ):
            raise ValueError(
                "T98 requires the frozen-normalizer T31/T19 recurrent "
                "variable-configuration contract, its gate asset, and no "
                "earlier actor-update mask"
            )
        self.env_config.winner_v127_constrained_cost = (
            args.winner_v127_constrained_cost
        )
        if args.winner_v127_constrained_cost and (
            args.ground_up_peak_torque_exceedance_scale != 0.0
            or args.ground_up_linear_peak_torque_exceedance_scale != 0.0
        ):
            raise ValueError(
                "winner-v127 cost must remain outside the clipped reward"
            )
        if args.nominal_reference_bootstrap:
            self.env_config.noise_config.level = 0.0
            self.env_config.noise_config.action_min_delay = 0
            self.env_config.noise_config.action_max_delay = 1
            self.env_config.noise_config.imu_min_delay = 0
            self.env_config.noise_config.imu_max_delay = 1
            self.env_config.push_config.enable = False
        if args.winner_v3_variable_configuration:
            if not args.nominal_reference_bootstrap:
                raise ValueError("winner-v3 requires deterministic nominal-reference reset")
            if args.policy_architecture not in (
                "reference_residual_recurrent_adapter",
                "response_conditioned_reference_residual",
            ):
                raise ValueError(
                    "winner-v3 requires a preregistered recurrent adapter"
                )
            if not (
                args.ground_up_hard_vector_command_support
                and args.ground_up_measured_actuator_bridge
                and args.ground_up_applied_target_observation
            ):
                raise ValueError("winner-v3 requires hard-vector, measured bridge and applied-target observation")
            if args.winner_t19_support_trainthrough:
                from playground.common.t19_support_trainthrough import (
                    SOURCE_RATE_LIMITS_RAD_S,
                )

                expected_limits = jp.asarray(
                    SOURCE_RATE_LIMITS_RAD_S, dtype=jp.float32
                )
            else:
                expected_limits = (
                    jp.asarray(
                        joystick.WINNER_V119_RATE_LIMITS_RAD_S,
                        dtype=jp.float32,
                    )
                    if args.winner_v119_train_transition_match
                    else winner_v3.CONSERVATIVE_VELOCITY_LIMITS_RAD_S
                )
            if not bool(
                jp.array_equal(
                    jp.asarray(limits, dtype=jp.float32),
                    expected_limits,
                )
            ):
                raise ValueError(
                    "winner-v3 selected all-joint velocity vector changed"
                )
            self.env_config.noise_config.level = args.winner_v3_deviation_scale
            self.env_config.noise_config.action_min_delay = 0
            self.env_config.noise_config.action_max_delay = 3
            self.env_config.noise_config.imu_min_delay = 0
            self.env_config.noise_config.imu_max_delay = 3
            self.env_config.push_config.enable = False
        self.env = self.env_file[1](task=args.task, config=self.env_config)
        self.eval_env = self.env_file[1](task=args.task, config=self.env_config)
        if args.winner_t19_support_trainthrough:
            from playground.common.t19_support_trainthrough import (
                RATE_LIMITS_RAD_S,
                SOURCE_RATE_LIMITS_RAD_S,
                SupportPrefixWrapper,
            )

            if (
                not args.winner_v3_variable_configuration
                or not args.winner_v119_train_transition_match
                or args.policy_architecture
                != "reference_residual_recurrent_adapter"
                or args.recurrent_hidden_size != 64
            ):
                raise ValueError(
                    "T19 requires V121 recurrent variable-configuration "
                    "training with the V119 source transition"
                )
            if not bool(
                jp.array_equal(
                    jp.asarray(limits, dtype=jp.float32),
                    jp.asarray(SOURCE_RATE_LIMITS_RAD_S, dtype=jp.float32),
                )
            ):
                raise ValueError("T19 trained source rate vector changed")
            if RATE_LIMITS_RAD_S.shape != SOURCE_RATE_LIMITS_RAD_S.shape:
                raise ValueError("T19 external physical rate vector changed")
            self.env = SupportPrefixWrapper(self.env)
            self.eval_env = SupportPrefixWrapper(self.eval_env)
        if args.policy_architecture == "response_conditioned_reference_residual":
            from playground.common.winner_v98_response_calibration_wrapper import (
                wrap_response_calibration,
            )
            from playground.common.winner_v98_response_conditioned_export import (
                validate_protected_policy_path,
            )

            if not args.winner_v3_variable_configuration:
                raise ValueError(
                    "response-conditioned policy requires winner-v3 variable configuration"
                )
            if args.recurrent_hidden_size != 64:
                raise ValueError("response-conditioned hidden size must remain 64")
            if args.winner_v98_protected_policy_path is None:
                raise ValueError("response-conditioned protected policy path is required")
            if args.winner_v98_calibrator_path is None:
                raise ValueError("response-conditioned calibrator path is required")
            validate_protected_policy_path(args.winner_v98_protected_policy_path)
            self.env = wrap_response_calibration(
                self.env,
                args.winner_v98_calibrator_path,
                calibration_ticks=args.winner_v98_calibration_ticks,
                home_return_ticks=args.winner_v98_home_return_ticks,
            )
            self.eval_env = wrap_response_calibration(
                self.eval_env,
                args.winner_v98_calibrator_path,
                calibration_ticks=args.winner_v98_calibration_ticks,
                home_return_ticks=args.winner_v98_home_return_ticks,
            )
        if args.winner_v3_variable_configuration:
            torso_body_id = int(self.env.mj_model.body(winner_v3.TORSO_BODY_NAME).id)
            torso_mass = float(self.env.mj_model.body_mass[torso_body_id])
            if torso_body_id != winner_v3.TORSO_BODY_ID or torso_mass <= 0.0:
                raise ValueError("winner-v3 named inertial torso contract failed")
            self.randomizer = winner_v3.make_winner_v3_configuration_randomizer(
                torso_body_id=torso_body_id,
                deviation_scale=args.winner_v3_deviation_scale,
            )
            if (
                args.winner_t66_endpoint_core_continuation
                or args.winner_t77_endpoint_joint_adapter_continuation
                or args.winner_t98_hidden_expert_continuation
            ):
                from playground.common.t66_endpoint_core_continuation import (
                    make_endpoint_bank_randomizer,
                )

                self.randomizer = make_endpoint_bank_randomizer(
                    self.randomizer,
                    torso_body_id=torso_body_id,
                )
                if args.winner_t98_hidden_expert_continuation:
                    print(
                        "T98_HIDDEN_EXPERT_CONTINUATION="
                        "strata=8,broad=1,isolated=7,"
                        "gate=always_on,"
                        "actor_updates=negative_adapter_location_only"
                    )
                elif args.winner_t77_endpoint_joint_adapter_continuation:
                    print(
                        "T77_ENDPOINT_JOINT_ADAPTER_CONTINUATION="
                        "strata=8,broad=1,isolated=7,"
                        "actor_updates=recurrent_core_plus_output_head"
                    )
                else:
                    print(
                        "T66_ENDPOINT_CORE_CONTINUATION="
                        "strata=8,broad=1,isolated=7,"
                        "actor_updates=recurrent_core_only"
                    )
            print(
                "WINNER_V3_VARIABLE_CONFIGURATION="
                f"name={winner_v3.TORSO_BODY_NAME},id={torso_body_id},mass={torso_mass},"
                f"deviation_scale={args.winner_v3_deviation_scale}"
            )
        elif args.ground_up_torso_com_randomization:
            torso_body_name = "trunk_assembly"
            torso_body_id = int(self.env.mj_model.body(torso_body_name).id)
            torso_body_mass = float(self.env.mj_model.body_mass[torso_body_id])
            if torso_body_id != randomize.TORSO_BODY_ID:
                raise ValueError(
                    f"torso schema mismatch: {torso_body_name} is {torso_body_id}, "
                    f"expected {randomize.TORSO_BODY_ID}"
                )
            if torso_body_mass <= 0.0:
                raise ValueError(f"named torso is massless: {torso_body_mass}")
            self.randomizer = randomize.make_ground_up_torso_com_x_randomizer(
                torso_body_id,
                args.ground_up_torso_com_x_min_m,
                args.ground_up_torso_com_x_max_m,
                args.ground_up_torso_com_distribution,
            )
            print(
                "GROUND_UP_TORSO_COM_RANDOMIZER="
                f"name={torso_body_name},id={torso_body_id},mass={torso_body_mass},"
                f"min={args.ground_up_torso_com_x_min_m},"
                f"max={args.ground_up_torso_com_x_max_m},"
                f"distribution={args.ground_up_torso_com_distribution}"
            )
        else:
            self.randomizer = (
                None if args.nominal_reference_bootstrap else randomize.domain_randomize
            )
        self.action_size = self.env.action_size
        self.obs_size = int(
            self.env.observation_size["state"][0]
        )  # 0: state 1: privileged_state
        self.restore_checkpoint_path = args.restore_checkpoint_path
        print(f"Observation size: {self.obs_size}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Open Duck Mini Runner Script")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="checkpoints",
        help="Where to save the checkpoints",
    )
    # parser.add_argument("--num_timesteps", type=int, default=300000000)
    parser.add_argument("--num_timesteps", type=int, default=150000000)
    parser.add_argument("--ppo_seed", type=int, default=0)
    parser.add_argument("--ppo_num_envs", type=int, default=8192)
    parser.add_argument("--ppo_num_evals", type=int, default=15)
    parser.add_argument("--ppo_episode_length", type=int, default=1000)
    parser.add_argument("--ppo_unroll_length", type=int, default=20)
    parser.add_argument("--ppo_batch_size", type=int, default=256)
    parser.add_argument("--ppo_num_minibatches", type=int, default=32)
    parser.add_argument("--ppo_num_updates_per_batch", type=int, default=4)
    parser.add_argument("--ppo_learning_rate", type=float, default=None)
    parser.add_argument("--ppo_discounting", type=float, default=None)
    parser.add_argument("--ppo_entropy_cost", type=float, default=None)
    parser.add_argument(
        "--policy_architecture",
        choices=[
            "mlp",
            "phase_moe",
            "recurrent",
            "reference_residual",
            "reference_residual_recurrent_adapter",
            "response_conditioned_reference_residual",
        ],
        default="mlp",
    )
    parser.add_argument("--recurrent_hidden_size", type=int, default=64)
    parser.add_argument("--winner_v98_protected_policy_path", default=None)
    parser.add_argument("--winner_v98_calibrator_path", default=None)
    parser.add_argument("--winner_v98_calibration_ticks", type=int, default=250)
    parser.add_argument("--winner_v98_home_return_ticks", type=int, default=250)
    parser.add_argument("--imitation_scale", type=float, default=None)
    parser.add_argument("--reference_feature_table_path", default=None)
    parser.add_argument("--ground_up_command_curriculum", action="store_true")
    parser.add_argument("--nominal_reference_bootstrap", action="store_true")
    parser.add_argument("--nominal_reference_command_x", type=float, default=0.074)
    parser.add_argument("--ground_up_torso_com_randomization", action="store_true")
    parser.add_argument("--ground_up_torso_com_x_min_m", type=float, default=-0.05)
    parser.add_argument("--ground_up_torso_com_x_max_m", type=float, default=0.05)
    parser.add_argument(
        "--ground_up_torso_com_distribution",
        choices=["uniform", "anchors"],
        default="uniform",
    )
    parser.add_argument("--ground_up_hard_vector_command_support", action="store_true")
    parser.add_argument("--ground_up_command_support_min_x", type=float, default=0.074)
    parser.add_argument("--ground_up_command_support_max_x", type=float, default=0.080)
    parser.add_argument(
        "--ground_up_action_velocity_limits_rad_s",
        default="5.24,5.24,1.50,1.50,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25",
    )
    parser.add_argument("--ground_up_measured_actuator_bridge", action="store_true")
    parser.add_argument("--ground_up_applied_target_observation", action="store_true")
    parser.add_argument(
        "--ground_up_tracking_tail_exceedance_scale", type=float, default=0.0
    )
    parser.add_argument(
        "--ground_up_tracking_tail_threshold_rad", type=float, default=0.20
    )
    parser.add_argument(
        "--ground_up_peak_torque_exceedance_scale", type=float, default=0.0
    )
    parser.add_argument(
        "--ground_up_linear_peak_torque_exceedance_scale",
        type=float,
        default=0.0,
    )
    parser.add_argument(
        "--ground_up_actuator_bridge_delay_ticks",
        default="3,3,3,3,3,3,2,3,3,3,2,3,2,3",
    )
    parser.add_argument(
        "--ground_up_actuator_bridge_tau_s",
        default=".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005",
    )
    parser.add_argument("--reference_start_phase", type=int, default=0)
    parser.add_argument("--ground_up_signed_progress_objective", action="store_true")
    parser.add_argument("--winner_v3_variable_configuration", action="store_true")
    parser.add_argument("--winner_v119_train_transition_match", action="store_true")
    parser.add_argument(
        "--winner_t19_support_trainthrough",
        action="store_true",
    )
    parser.add_argument(
        "--winner_t31_action_margin_trainthrough",
        action="store_true",
    )
    parser.add_argument(
        "--winner_t37_freeze_observation_normalizer",
        action="store_true",
    )
    parser.add_argument(
        "--winner_t66_endpoint_core_continuation",
        action="store_true",
    )
    parser.add_argument(
        "--winner_t77_endpoint_joint_adapter_continuation",
        action="store_true",
    )
    parser.add_argument(
        "--winner_t98_hidden_expert_continuation",
        action="store_true",
    )
    parser.add_argument("--winner_t98_hidden_gate_asset_path", default=None)
    parser.add_argument("--winner_v127_constrained_cost", action="store_true")
    parser.add_argument(
        "--winner_v3_deviation_scale",
        type=float,
        choices=[0.0, 0.25, 0.5, 1.0],
        default=0.0,
    )
    parser.add_argument(
        "--critic_observation", choices=["privileged_state", "state"], default="privileged_state"
    )
    parser.add_argument("--env", type=str, default="joystick", help="env")
    parser.add_argument("--task", type=str, default="flat_terrain", help="Task to run")
    parser.add_argument(
        "--restore_checkpoint_path",
        type=str,
        default=None,
        help="Resume training from this checkpoint",
    )
    # parser.add_argument(
    #     "--debug", action="store_true", help="Run in debug mode with minimal parameters"
    # )
    args = parser.parse_args()

    runner = OpenDuckMiniV2Runner(args)

    runner.train()


if __name__ == "__main__":
    main()
