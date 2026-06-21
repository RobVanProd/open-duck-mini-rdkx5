"""
投影仪控制模块 - 支持 RDK X5 和 Raspberry Pi
通过 GPIO 控制投影仪开关
"""
import time

# 尝试导入平台检测模块
try:
    from .platform_compat import PLATFORM
except ImportError:
    PLATFORM = "RPI"

# BCM 编号
PROJECTOR_GPIO_BCM = 25

class Projector:
    """投影仪控制类
    
    通过 GPIO 控制投影仪开关，支持 RDK X5 和 Raspberry Pi。
    """
    
    def __init__(self):
        self.on = False
        self._disabled = False
        
        if PLATFORM == "RDK_X5":
            self._init_rdk_x5()
        else:
            self._init_raspberry_pi()
    
    def _init_rdk_x5(self):
        """RDK X5 平台初始化"""
        try:
            import Hobot.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(PROJECTOR_GPIO_BCM, GPIO.OUT, initial=GPIO.LOW)
            self._use_hobot = True
            print(f"[Projector] RDK X5: GPIO BCM {PROJECTOR_GPIO_BCM}")
        except Exception as e:
            print(f"[Projector] RDK X5 GPIO 初始化失败: {e}")
            self._disabled = True
            self._use_hobot = False
    
    def _init_raspberry_pi(self):
        """Raspberry Pi 平台初始化"""
        import board
        import digitalio
        
        self.project = digitalio.DigitalInOut(board.D25)
        self.project.direction = digitalio.Direction.OUTPUT
        self._use_hobot = False
        print("[Projector] Raspberry Pi: board.D25")

    def switch(self):
        """切换投影仪状态"""
        if self._disabled:
            return
        
        self.on = not self.on
        
        if self._use_hobot:
            self.GPIO.output(PROJECTOR_GPIO_BCM, self.GPIO.HIGH if self.on else self.GPIO.LOW)
        else:
            self.project.value = self.on

    def stop(self):
        """关闭投影仪并释放资源"""
        if self._disabled:
            return
        
        if self._use_hobot:
            self.GPIO.output(PROJECTOR_GPIO_BCM, self.GPIO.LOW)
            self.GPIO.cleanup([PROJECTOR_GPIO_BCM])
        else:
            self.project.value = False
            self.project.deinit()


if __name__ == "__main__":
    print(f"平台: {PLATFORM}")
    p = Projector()
    try:
        while True:
            p.switch()
            print(f"投影仪: {'开' if p.on else '关'}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止")
    finally:
        p.stop()
