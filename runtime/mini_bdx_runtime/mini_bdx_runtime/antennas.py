"""
天线舵机控制模块 - 支持 RDK X5 和 Raspberry Pi
注意: RDK X5 暂不支持 PWM，该功能在 RDK X5 上会被禁用
"""
import math
import time

# 尝试导入平台检测模块
try:
    from .platform_compat import PLATFORM
except ImportError:
    PLATFORM = "RPI"

LEFT_SIGN = 1
RIGHT_SIGN = -1
MIN_UPDATE_INTERVAL = 1 / 50  # 20ms


def value_to_duty_cycle(v):
    """将 -1~1 的值转换为 PWM 占空比"""
    pulse_width_ms = 1.5 + (v * 0.5)  # 1ms to 2ms
    duty_cycle = int((pulse_width_ms / 20) * 65535)
    return min(max(duty_cycle, 3277), 6553)


class Antennas:
    """天线舵机控制类
    
    在 RDK X5 上此功能被禁用 (不支持 PWM)
    """
    
    def __init__(self):
        self._disabled = False
        
        if PLATFORM == "RDK_X5":
            # RDK X5 暂不支持 PWM，禁用天线功能
            print("[Antennas] RDK X5 不支持 PWM，天线功能已禁用")
            self._disabled = True
            return
        
        # Raspberry Pi 使用 pwmio
        import board
        import pwmio
        
        LEFT_ANTENNA_PIN = board.D13
        RIGHT_ANTENNA_PIN = board.D12
        
        neutral_duty = value_to_duty_cycle(0)
        self.pwm_left = pwmio.PWMOut(LEFT_ANTENNA_PIN, frequency=50, duty_cycle=neutral_duty)
        self.pwm_right = pwmio.PWMOut(RIGHT_ANTENNA_PIN, frequency=50, duty_cycle=neutral_duty)
        print("[Antennas] Raspberry Pi: 天线功能已启用")

    def set_position_left(self, position):
        """设置左天线位置"""
        if self._disabled:
            return
        self.set_position(self.pwm_left, position, LEFT_SIGN)

    def set_position_right(self, position):
        """设置右天线位置"""
        if self._disabled:
            return
        self.set_position(self.pwm_right, position, RIGHT_SIGN)

    def set_position(self, pwm, value, sign=1):
        """设置天线位置
        
        Args:
            pwm: PWM 对象
            value: -1 到 1 的位置值
            sign: 方向符号
        """
        if self._disabled:
            return
        if -1 <= value <= 1:
            duty_cycle = value_to_duty_cycle(value * sign)
            pwm.duty_cycle = duty_cycle
        else:
            print("Invalid input! Enter a value between -1 and 1.")

    def stop(self):
        """停止天线并释放资源"""
        if self._disabled:
            return
        time.sleep(MIN_UPDATE_INTERVAL)
        self.set_position_left(0)
        self.set_position_right(0)
        time.sleep(MIN_UPDATE_INTERVAL)
        self.pwm_left.deinit()
        self.pwm_right.deinit()


if __name__ == "__main__":
    print(f"平台: {PLATFORM}")
    antennas = Antennas()

    if antennas._disabled:
        print("天线功能已禁用，无法测试")
    else:
        try:
            start_time = time.monotonic()
            current_time = start_time

            while current_time - start_time < 5:
                value = math.sin(2 * math.pi * 1 * current_time)
                antennas.set_position_left(value)
                antennas.set_position_right(value)
                time.sleep(MIN_UPDATE_INTERVAL)
                current_time = time.monotonic()
        finally:
            antennas.stop()