"""
平台兼容层 - 自动检测 RDK X5 或 Raspberry Pi
用于 Open Duck Mini Runtime 移植
"""
import os

def detect_platform():
    """检测当前运行平台"""
    # 方法1: 检测 Hobot.GPIO
    try:
        import Hobot.GPIO as GPIO
        if hasattr(GPIO, 'model'):
            model = GPIO.model
            if 'RDK' in model or 'X5' in model:
                return "RDK_X5"
        # 如果能导入 Hobot.GPIO 就认为是 RDK
        return "RDK_X5"
    except ImportError:
        pass
    
    # 方法2: 检测 I2C 总线 (RDK X5 特有 I2C-5)
    if os.path.exists("/dev/i2c-5") and not os.path.exists("/dev/i2c-1"):
        return "RDK_X5"
    
    # 默认树莓派
    return "RPI"

# 全局平台标识
PLATFORM = detect_platform()

def get_i2c_bus_number():
    """获取 I2C 总线号
    
    Returns:
        int: I2C 总线号
        - RDK X5: 5 (40-pin 物理引脚 3/5)
        - Raspberry Pi: 1
    """
    if PLATFORM == "RDK_X5":
        return 5
    return 1

def is_rdk_x5():
    """检查是否为 RDK X5 平台"""
    return PLATFORM == "RDK_X5"

def is_raspberry_pi():
    """检查是否为 Raspberry Pi 平台"""
    return PLATFORM == "RPI"

# 启动时打印平台信息
print(f"[platform_compat] 检测到平台: {PLATFORM}, I2C 总线: {get_i2c_bus_number()}")
