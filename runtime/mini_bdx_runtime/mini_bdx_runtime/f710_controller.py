"""
Logitech F710 手柄控制器 (X-mode)
与 XBoxController 保持相同接口，方便切换使用
"""
import pygame
from threading import Thread
from queue import Queue
import time
import numpy as np
from mini_bdx_runtime.buttons import Buttons


# 速度范围
X_RANGE = [-0.15, 0.15]
Y_RANGE = [-0.2, 0.2]
YAW_RANGE = [-1.0, 1.0]

# 头部角度范围 (弧度)
NECK_PITCH_RANGE = [-0.34, 1.1]
HEAD_PITCH_RANGE = [-0.78, 0.3]
HEAD_YAW_RANGE = [-0.5, 0.5]
HEAD_ROLL_RANGE = [-0.5, 0.5]

# F710 X-mode 轴映射
AXIS_LEFT_X = 0      # 左摇杆 X
AXIS_LEFT_Y = 1      # 左摇杆 Y
AXIS_LT = 2          # 左扳机 (范围 -1 到 1)
AXIS_RIGHT_X = 3     # 右摇杆 X
AXIS_RIGHT_Y = 4     # 右摇杆 Y
AXIS_RT = 5          # 右扳机 (范围 -1 到 1)

# F710 X-mode 按钮映射
BTN_A = 0
BTN_B = 1
BTN_X = 2
BTN_Y = 3
BTN_LB = 4
BTN_RB = 5
BTN_BACK = 6
BTN_START = 7
BTN_LOGITECH = 8
BTN_LEFT_STICK = 9
BTN_RIGHT_STICK = 10


class F710Controller:
    """Logitech F710 手柄控制器 (X-mode)"""
    
    def __init__(self, command_freq, only_head_control=False):
        self.command_freq = command_freq
        self.head_control_mode = only_head_control
        self.only_head_control = only_head_control

        self.last_commands = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.last_left_trigger = 0.0
        self.last_right_trigger = 0.0
        
        pygame.init()
        self.p1 = pygame.joystick.Joystick(0)
        self.p1.init()
        print(f"[F710Controller] 手柄: {self.p1.get_name()}")
        print(f"[F710Controller] 轴数: {self.p1.get_numaxes()}, 按钮数: {self.p1.get_numbuttons()}")
        
        self.cmd_queue = Queue(maxsize=1)

        self.A_pressed = False
        self.B_pressed = False
        self.X_pressed = False
        self.Y_pressed = False
        self.LB_pressed = False
        self.RB_pressed = False

        self.buttons = Buttons()

        Thread(target=self.commands_worker, daemon=True).start()

    def commands_worker(self):
        while True:
            self.cmd_queue.put(self.get_commands())
            time.sleep(1 / self.command_freq)

    def get_commands(self):
        last_commands = self.last_commands
        left_trigger = self.last_left_trigger
        right_trigger = self.last_right_trigger

        # F710 X-mode 轴读取
        l_x = -1 * self.p1.get_axis(AXIS_LEFT_X)
        l_y = -1 * self.p1.get_axis(AXIS_LEFT_Y)
        r_x = -1 * self.p1.get_axis(AXIS_RIGHT_X)
        r_y = -1 * self.p1.get_axis(AXIS_RIGHT_Y)

        # 扳机: -1 (未按) 到 1 (全按), 归一化到 0-1
        right_trigger = np.around((self.p1.get_axis(AXIS_RT) + 1) / 2, 3)
        left_trigger = np.around((self.p1.get_axis(AXIS_LT) + 1) / 2, 3)

        if left_trigger < 0.1:
            left_trigger = 0
        if right_trigger < 0.1:
            right_trigger = 0

        if not self.head_control_mode:
            lin_vel_y = l_x
            lin_vel_x = l_y
            ang_vel = r_x
            
            if lin_vel_x >= 0:
                lin_vel_x *= np.abs(X_RANGE[1])
            else:
                lin_vel_x *= np.abs(X_RANGE[0])

            if lin_vel_y >= 0:
                lin_vel_y *= np.abs(Y_RANGE[1])
            else:
                lin_vel_y *= np.abs(Y_RANGE[0])

            if ang_vel >= 0:
                ang_vel *= np.abs(YAW_RANGE[1])
            else:
                ang_vel *= np.abs(YAW_RANGE[0])

            last_commands[0] = lin_vel_x
            last_commands[1] = lin_vel_y
            last_commands[2] = ang_vel
        else:
            last_commands[0] = 0.0
            last_commands[1] = 0.0
            last_commands[2] = 0.0
            last_commands[3] = 0.0  # neck pitch

            head_yaw = l_x
            head_pitch = l_y
            head_roll = r_x

            if head_yaw >= 0:
                head_yaw *= np.abs(HEAD_YAW_RANGE[0])
            else:
                head_yaw *= np.abs(HEAD_YAW_RANGE[1])

            if head_pitch >= 0:
                head_pitch *= np.abs(HEAD_PITCH_RANGE[0])
            else:
                head_pitch *= np.abs(HEAD_PITCH_RANGE[1])

            if head_roll >= 0:
                head_roll *= np.abs(HEAD_ROLL_RANGE[0])
            else:
                head_roll *= np.abs(HEAD_ROLL_RANGE[1])

            last_commands[4] = head_pitch
            last_commands[5] = head_yaw
            last_commands[6] = head_roll

        # F710 X-mode 按钮处理
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if self.p1.get_button(BTN_A):
                    self.A_pressed = True
                if self.p1.get_button(BTN_B):
                    self.B_pressed = True
                if self.p1.get_button(BTN_X):
                    self.X_pressed = True
                if self.p1.get_button(BTN_Y):
                    self.Y_pressed = True
                    if not self.only_head_control:
                        self.head_control_mode = not self.head_control_mode
                if self.p1.get_button(BTN_LB):
                    self.LB_pressed = True
                if self.p1.get_button(BTN_RB):
                    self.RB_pressed = True

            if event.type == pygame.JOYBUTTONUP:
                self.A_pressed = False
                self.B_pressed = False
                self.X_pressed = False
                self.Y_pressed = False
                self.LB_pressed = False
                self.RB_pressed = False

        up_down = self.p1.get_hat(0)[1] if self.p1.get_numhats() > 0 else 0
        pygame.event.pump()

        return (
            np.around(last_commands, 3),
            self.A_pressed,
            self.B_pressed,
            self.X_pressed,
            self.Y_pressed,
            self.LB_pressed,
            self.RB_pressed,
            left_trigger,
            right_trigger,
            up_down,
        )

    def get_last_command(self):
        A_pressed = False
        B_pressed = False
        X_pressed = False
        Y_pressed = False
        LB_pressed = False
        RB_pressed = False
        up_down = 0
        try:
            (
                self.last_commands,
                A_pressed,
                B_pressed,
                X_pressed,
                Y_pressed,
                LB_pressed,
                RB_pressed,
                self.last_left_trigger,
                self.last_right_trigger,
                up_down,
            ) = self.cmd_queue.get(False)
        except Exception:
            pass

        self.buttons.update(
            A_pressed,
            B_pressed,
            X_pressed,
            Y_pressed,
            LB_pressed,
            RB_pressed,
            up_down == 1,
            up_down == -1,
        )

        return (
            self.last_commands,
            self.buttons,
            self.last_left_trigger,
            self.last_right_trigger,
        )


if __name__ == "__main__":
    print("测试 F710 控制器...")
    controller = F710Controller(20)

    while True:
        cmd, buttons, lt, rt = controller.get_last_command()
        print(f"命令: {cmd[:3]}, LT: {lt:.2f}, RT: {rt:.2f}", end="\r")
        time.sleep(0.05)
