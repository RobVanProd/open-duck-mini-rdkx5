"""
I2C 兼容层 - 用于 adafruit_bno055 库
支持 RDK X5 (smbus2) 和 Raspberry Pi (busio)

此模块提供 I2CCompat 类，在 RDK X5 上使用 smbus2 模拟 
Adafruit busio.I2C 接口，使得 adafruit_bno055 库可以正常工作。
"""
from .platform_compat import PLATFORM, get_i2c_bus_number

if PLATFORM == "RDK_X5":
    import smbus2
    
    class I2CCompat:
        """
        模拟 Adafruit busio.I2C 接口
        底层使用 smbus2，适配 RDK X5 平台
        """
        def __init__(self, scl=None, sda=None, frequency=400000):
            """初始化 I2C 总线
            
            Args:
                scl: 忽略 (RDK X5 使用固定引脚)
                sda: 忽略 (RDK X5 使用固定引脚)
                frequency: 忽略 (由系统设置)
            """
            bus_num = get_i2c_bus_number()
            self._bus = smbus2.SMBus(bus_num)
            self._locked = False
            print(f"[I2CCompat] 使用 smbus2, 总线: /dev/i2c-{bus_num}")
        
        def try_lock(self):
            """尝试锁定 I2C 总线"""
            if not self._locked:
                self._locked = True
                return True
            return False
        
        def unlock(self):
            """解锁 I2C 总线"""
            self._locked = False
        
        def scan(self):
            """扫描 I2C 总线上的设备
            
            Returns:
                list: 检测到的设备地址列表
            """
            devices = []
            for addr in range(0x08, 0x78):
                try:
                    self._bus.read_byte(addr)
                    devices.append(addr)
                except:
                    pass
            return devices
        
        def writeto(self, address, buffer, *, start=0, end=None, stop=True):
            """写入数据到 I2C 设备
            
            Args:
                address: I2C 设备地址
                buffer: 要写入的数据 (bytes 或 bytearray)
                start: 起始索引
                end: 结束索引
                stop: 是否发送停止位 (忽略)
            """
            if end is None:
                end = len(buffer)
            data = list(buffer[start:end])
            if len(data) == 0:
                return
            if len(data) == 1:
                self._bus.write_byte(address, data[0])
            else:
                # 第一个字节作为寄存器地址
                self._bus.write_i2c_block_data(address, data[0], data[1:])
        
        def readfrom_into(self, address, buffer, *, start=0, end=None):
            """从设备读取数据到 buffer
            
            Args:
                address: I2C 设备地址
                buffer: 接收数据的缓冲区
                start: 起始索引
                end: 结束索引
            """
            if end is None:
                end = len(buffer)
            length = end - start
            try:
                # 读取数据 (从寄存器 0 开始)
                data = self._bus.read_i2c_block_data(address, 0, length)
                for i, byte in enumerate(data):
                    if start + i < len(buffer):
                        buffer[start + i] = byte
            except Exception as e:
                raise IOError(f"I2C read error: {e}")
        
        def writeto_then_readfrom(self, address, buffer_out, buffer_in, 
                                   *, out_start=0, out_end=None, 
                                   in_start=0, in_end=None, stop=False):
            """写入后读取 (常用于读取寄存器)
            
            Args:
                address: I2C 设备地址
                buffer_out: 要写入的数据 (通常是寄存器地址)
                buffer_in: 接收数据的缓冲区
                out_start, out_end: 输出缓冲区范围
                in_start, in_end: 输入缓冲区范围
                stop: 是否在写入后发送停止位 (忽略)
            """
            if out_end is None:
                out_end = len(buffer_out)
            if in_end is None:
                in_end = len(buffer_in)
            
            out_data = list(buffer_out[out_start:out_end])
            in_length = in_end - in_start
            
            if len(out_data) == 0:
                # 无输出数据,直接读取
                data = self._bus.read_i2c_block_data(address, 0, in_length)
            elif len(out_data) == 1:
                # 单字节写入,作为寄存器地址读取
                data = self._bus.read_i2c_block_data(address, out_data[0], in_length)
            else:
                # 多字节写入后读取
                self._bus.write_i2c_block_data(address, out_data[0], out_data[1:])
                data = self._bus.read_i2c_block_data(address, 0, in_length)
            
            for i, byte in enumerate(data):
                if in_start + i < len(buffer_in):
                    buffer_in[in_start + i] = byte
        
        def deinit(self):
            """关闭 I2C 总线"""
            if hasattr(self, '_bus') and self._bus:
                self._bus.close()
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.deinit()
            return False
        
        def __del__(self):
            self.deinit()

else:
    # 树莓派使用原生 busio
    import board
    import busio
    
    class I2CCompat(busio.I2C):
        """树莓派平台使用原生 busio.I2C"""
        def __init__(self, scl=None, sda=None, frequency=400000):
            if scl is None:
                scl = board.SCL
            if sda is None:
                sda = board.SDA
            super().__init__(scl, sda, frequency=frequency)
            print("[I2CCompat] 使用 busio.I2C")


# 测试代码
if __name__ == "__main__":
    print(f"平台: {PLATFORM}")
    i2c = I2CCompat()
    print("I2C 总线扫描结果:")
    devices = i2c.scan()
    for addr in devices:
        print(f"  - 0x{addr:02X}")
    i2c.deinit()
