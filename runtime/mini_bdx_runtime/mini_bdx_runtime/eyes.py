"""
眼睛 LED 控制模块 - 支持 RDK X5 和 Raspberry Pi
控制左右眼 LED 随机眨眼效果
"""
import random
import time
from threading import Thread, Event

# 尝试导入平台检测模块
try:
    from .platform_compat import PLATFORM
except ImportError:
    PLATFORM = "RPI"

# BCM 编号
LEFT_EYE_PIN_BCM = 24
RIGHT_EYE_PIN_BCM = 23


class Eyes:
    """眼睛 LED 控制类
    
    控制双眼 LED 实现随机眨眼效果，支持 RDK X5 和 Raspberry Pi。
    """
    
    def __init__(self, blink_duration=0.1, min_interval=1.0, max_interval=4.0):
        self.blink_duration = blink_duration
        self.min_interval = min_interval
        self.max_interval = max_interval
        self._disabled = False
        
        if PLATFORM == "RDK_X5":
            self._init_rdk_x5()
        else:
            self._init_raspberry_pi()
        
        if not self._disabled:
            self._stop_event = Event()
            self._thread = Thread(target=self.run, daemon=True)
            self._thread.start()
    
    def _init_rdk_x5(self):
        """RDK X5 平台初始化"""
        try:
            import Hobot.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(LEFT_EYE_PIN_BCM, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(RIGHT_EYE_PIN_BCM, GPIO.OUT, initial=GPIO.HIGH)
            self._use_hobot = True
            print(f"[Eyes] RDK X5: GPIO BCM {LEFT_EYE_PIN_BCM}, {RIGHT_EYE_PIN_BCM}")
        except Exception as e:
            print(f"[Eyes] RDK X5 GPIO 初始化失败: {e}")
            self._disabled = True
            self._use_hobot = False
    
    def _init_raspberry_pi(self):
        """Raspberry Pi 平台初始化"""
        import board
        import digitalio
        
        self.left_eye = digitalio.DigitalInOut(board.D24)
        self.left_eye.direction = digitalio.Direction.OUTPUT
        
        self.right_eye = digitalio.DigitalInOut(board.D23)
        self.right_eye.direction = digitalio.Direction.OUTPUT
        
        self._use_hobot = False
        print("[Eyes] Raspberry Pi: board.D24, board.D23")

    def _set_eyes(self, state):
        """设置双眼状态"""
        if self._disabled:
            return
        
        if self._use_hobot:
            value = self.GPIO.HIGH if state else self.GPIO.LOW
            self.GPIO.output(LEFT_EYE_PIN_BCM, value)
            self.GPIO.output(RIGHT_EYE_PIN_BCM, value)
        else:
            self.left_eye.value = state
            self.right_eye.value = state

    def run(self):
        """眨眼循环线程"""
        try:
            while not self._stop_event.is_set():
                self._set_eyes(False)
                time.sleep(self.blink_duration)
                self._set_eyes(True)
                next_blink = random.uniform(self.min_interval, self.max_interval)
                # 使用较短的等待间隔检查停止事件
                for _ in range(int(next_blink * 10)):
                    if self._stop_event.is_set():
                        break
                    time.sleep(0.1)
        except Exception as err:
            print(f"Error in eye thread: {err}")
            self._stop_event.set()

    def stop(self):
        """停止眨眼并释放资源"""
        if self._disabled:
            return
        
        self._stop_event.set()
        if hasattr(self, '_thread'):
            self._thread.join(timeout=1)
        
        self._set_eyes(False)
        
        if self._use_hobot:
            self.GPIO.cleanup([LEFT_EYE_PIN_BCM, RIGHT_EYE_PIN_BCM])
        else:
            self.left_eye.deinit()
            self.right_eye.deinit()


if __name__ == "__main__":
    print(f"平台: {PLATFORM}")
    e = Eyes()
    try:
        print("眼睛 LED 开始闪烁 (Ctrl+C 退出)...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止")
    finally:
        e.stop()
