"""
天线控制器测试脚本 - 支持 xbox 和 f710 手柄
"""
import argparse
from mini_bdx_runtime.antennas import Antennas
import time

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("--controller", type=str, default="f710", choices=["xbox", "f710"],
                    help="选择手柄类型: xbox 或 f710 (默认 f710)")
args = parser.parse_args()

# 根据参数选择控制器
if args.controller == "f710":
    from mini_bdx_runtime.f710_controller import F710Controller
    controller = F710Controller(60)
    print("[Controller] 使用 F710 控制器")
else:
    from mini_bdx_runtime.xbox_controller import XBoxController
    controller = XBoxController(60)
    print("[Controller] 使用 Xbox 控制器")

antennas = Antennas()


while True:

    _, _, left_trigger, right_trigger = controller.get_last_command()

    antennas.set_position_left(right_trigger)
    antennas.set_position_right(left_trigger)

    # print(left_trigger, right_trigger)
    time.sleep(1 / 50)
