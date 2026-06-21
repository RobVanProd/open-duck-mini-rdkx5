#!/usr/bin/env python3
"""
RDK X5 移植测试脚本
测试 I2C (IMU)、GPIO (脚部触点) 和串口 (舵机) 功能
"""
import sys
import time

def test_platform_detection():
    """测试平台检测"""
    print("\n" + "="*50)
    print("1. 测试平台检测")
    print("="*50)
    
    try:
        from mini_bdx_runtime.platform_compat import PLATFORM, get_i2c_bus_number, is_rdk_x5
        print(f"✓ 检测到平台: {PLATFORM}")
        print(f"✓ I2C 总线号: {get_i2c_bus_number()}")
        print(f"✓ 是否 RDK X5: {is_rdk_x5()}")
        return True
    except Exception as e:
        print(f"✗ 平台检测失败: {e}")
        return False

def test_i2c_compat():
    """测试 I2C 兼容层"""
    print("\n" + "="*50)
    print("2. 测试 I2C 兼容层")
    print("="*50)
    
    try:
        from mini_bdx_runtime.i2c_compat import I2CCompat
        i2c = I2CCompat()
        devices = i2c.scan()
        print(f"✓ I2C 总线扫描成功")
        print(f"✓ 检测到设备: {[hex(d) for d in devices]}")
        
        # 检查 BNO055 (0x28 或 0x29)
        if 0x28 in devices or 0x29 in devices:
            print(f"✓ 检测到 BNO055 IMU")
        else:
            print(f"⚠ 未检测到 BNO055 IMU (预期地址 0x28 或 0x29)")
        
        i2c.deinit()
        return True
    except Exception as e:
        print(f"✗ I2C 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imu():
    """测试 IMU 读取"""
    print("\n" + "="*50)
    print("3. 测试 IMU")
    print("="*50)
    
    try:
        from mini_bdx_runtime.raw_imu import Imu
        print("正在初始化 IMU (可能需要几秒钟)...")
        imu = Imu(50, upside_down=False)
        
        print("等待 IMU 数据...")
        time.sleep(0.5)
        
        for i in range(5):
            data = imu.get_data()
            print(f"  [{i+1}] 陀螺仪: {data['gyro']}, 加速度计: {data['accelero']}")
            time.sleep(0.1)
        
        print("✓ IMU 测试成功")
        return True
    except Exception as e:
        print(f"✗ IMU 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gpio():
    """测试 GPIO (脚部触点)"""
    print("\n" + "="*50)
    print("4. 测试 GPIO (脚部触点)")
    print("="*50)
    
    try:
        from mini_bdx_runtime.feet_contacts import FeetContacts
        fc = FeetContacts()
        
        print("读取脚部触点状态 (5次)...")
        for i in range(5):
            status = fc.get()
            left = "触地" if status[0] else "悬空"
            right = "触地" if status[1] else "悬空"
            print(f"  [{i+1}] 左脚: {left}, 右脚: {right}")
            time.sleep(0.2)
        
        fc.stop()
        print("✓ GPIO 测试成功")
        return True
    except Exception as e:
        print(f"✗ GPIO 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_serial():
    """测试串口 (舵机连接)"""
    print("\n" + "="*50)
    print("5. 测试串口 (舵机连接)")
    print("="*50)
    
    import os
    
    # 检查可能的串口设备
    serial_devices = []
    for dev in ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1"]:
        if os.path.exists(dev):
            serial_devices.append(dev)
    
    if serial_devices:
        print(f"✓ 检测到串口设备: {serial_devices}")
    else:
        print("⚠ 未检测到串口设备")
        return False
    
    # 尝试连接舵机
    try:
        import rustypot
        usb_port = serial_devices[0]
        print(f"尝试连接舵机 ({usb_port})...")
        io = rustypot.feetech(usb_port, 1000000)
        
        # 扫描舵机 ID
        print("扫描舵机 ID (这可能需要几秒钟)...")
        motor_ids = []
        for mid in range(1, 40):
            try:
                pos = io.read_present_position([mid])
                if pos:
                    motor_ids.append(mid)
            except:
                pass
        
        if motor_ids:
            print(f"✓ 检测到舵机 ID: {motor_ids}")
        else:
            print("⚠ 未检测到任何舵机")
        
        return True
    except Exception as e:
        print(f"⚠ 舵机连接测试失败: {e}")
        return False

def main():
    print("="*50)
    print("Open Duck Mini Runtime - RDK X5 移植测试")
    print("="*50)
    
    results = {}
    
    results["平台检测"] = test_platform_detection()
    results["I2C 兼容层"] = test_i2c_compat()
    results["IMU"] = test_imu()
    results["GPIO"] = test_gpio()
    results["串口"] = test_serial()
    
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("所有测试通过! 移植成功!")
    else:
        print("部分测试失败，请检查上面的错误信息")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
