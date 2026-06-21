"""
脚部触点检测模块 - 支持 RDK X5 和 Raspberry Pi
用于检测鸭子机器人双脚是否接触地面
"""
import time
from .platform_compat import PLATFORM

# 引脚映射
# 树莓派 BCM 22 = 物理引脚 15 (左脚)
# 树莓派 BCM 27 = 物理引脚 13 (右脚)
# RDK X5 使用相同的 BCM 编码
LEFT_FOOT_PIN_BCM = 22
RIGHT_FOOT_PIN_BCM = 27

class FeetContacts:
    """脚部触点检测类
    
    通过 GPIO 读取微动开关状态，检测双脚是否接触地面。
    支持 RDK X5 (Hobot.GPIO) 和 Raspberry Pi (digitalio) 两个平台。
    """
    
    def __init__(self):
        """初始化 GPIO 引脚"""
        if PLATFORM == "RDK_X5":
            self._init_rdk_x5()
        else:
            self._init_raspberry_pi()
    
    def _init_rdk_x5(self):
        """RDK X5 平台初始化"""
        import Hobot.GPIO as GPIO
        self.GPIO = GPIO
        self._use_hobot = True
        
        GPIO.setwarnings(False)
        # 使用 BCM 编码模式 (与树莓派兼容)
        GPIO.setmode(GPIO.BCM)
        # 设置为输入模式
        # 注意: Hobot.GPIO 可能不支持 pull_up_down 参数，使用 try-except 处理
        try:
            # 尝试使用 PUD_UP (RPi.GPIO 风格)
            GPIO.setup(LEFT_FOOT_PIN_BCM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(RIGHT_FOOT_PIN_BCM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        except AttributeError:
            # Hobot.GPIO 可能不支持上拉电阻设置，仅设置为输入
            GPIO.setup(LEFT_FOOT_PIN_BCM, GPIO.IN)
            GPIO.setup(RIGHT_FOOT_PIN_BCM, GPIO.IN)
            print("[FeetContacts] 警告: Hobot.GPIO 不支持内部上拉电阻，请确保外部已连接上拉电阻")
        print(f"[FeetContacts] RDK X5: GPIO BCM {LEFT_FOOT_PIN_BCM}, {RIGHT_FOOT_PIN_BCM}")

    
    def _init_raspberry_pi(self):
        """Raspberry Pi 平台初始化"""
        import board
        import digitalio
        self._use_hobot = False
        
        self.left_foot = digitalio.DigitalInOut(board.D22)
        self.left_foot.direction = digitalio.Direction.INPUT
        self.left_foot.pull = digitalio.Pull.UP
        
        self.right_foot = digitalio.DigitalInOut(board.D27)
        self.right_foot.direction = digitalio.Direction.INPUT
        self.right_foot.pull = digitalio.Pull.UP
        print(f"[FeetContacts] Raspberry Pi: board.D22, board.D27")

    def get(self):
        """获取脚部触点状态
        
        Returns:
            list: [左脚触地, 右脚触地]，True 表示触地
        """
        if self._use_hobot:
            # RDK X5: 低电平表示触地 (上拉 + 接地触发)
            left = not self.GPIO.input(LEFT_FOOT_PIN_BCM)
            right = not self.GPIO.input(RIGHT_FOOT_PIN_BCM)
        else:
            # Raspberry Pi: 同上
            left = not self.left_foot.value
            right = not self.right_foot.value
        return [left, right]

    def stop(self):
        """释放 GPIO 资源"""
        if self._use_hobot:
            self.GPIO.cleanup([LEFT_FOOT_PIN_BCM, RIGHT_FOOT_PIN_BCM])
        else:
            self.left_foot.deinit()
            self.right_foot.deinit()

if __name__ == "__main__":
    print(f"平台: {PLATFORM}")
    feet_contacts = FeetContacts()
    try:
        print("开始检测脚部触点 (Ctrl+C 退出)...")
        while True:
            status = feet_contacts.get()
            print(f"左脚: {'触地' if status[0] else '悬空'}, 右脚: {'触地' if status[1] else '悬空'}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n停止检测")
    finally:
        feet_contacts.stop()
