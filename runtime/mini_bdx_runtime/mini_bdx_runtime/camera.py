"""
摄像头模块 - 支持 RDK X5 和 Raspberry Pi
用于捕获图像并编码为 base64 格式
"""
import cv2
import base64
import os

# 尝试导入平台检测模块
try:
    from .platform_compat import PLATFORM
except ImportError:
    PLATFORM = "RPI"


class Cam:
    """摄像头控制类
    
    支持 RDK X5 (OpenCV) 和 Raspberry Pi (picamzero)。
    """
    
    def __init__(self, camera_id=0):
        """初始化摄像头
        
        Args:
            camera_id: 摄像头设备 ID，默认 0
        """
        self._disabled = False
        
        if PLATFORM == "RDK_X5":
            self._init_rdk_x5(camera_id)
        else:
            self._init_raspberry_pi()
    
    def _init_rdk_x5(self, camera_id):
        """RDK X5 平台初始化 - 使用 OpenCV"""
        try:
            self.cam = cv2.VideoCapture(camera_id)
            if not self.cam.isOpened():
                # 尝试使用 /dev/video0
                self.cam = cv2.VideoCapture("/dev/video0")
            
            if self.cam.isOpened():
                print(f"[Camera] RDK X5: OpenCV VideoCapture 设备 {camera_id}")
                self._use_opencv = True
            else:
                print("[Camera] RDK X5: 无法打开摄像头")
                self._disabled = True
                self._use_opencv = False
        except Exception as e:
            print(f"[Camera] RDK X5 初始化失败: {e}")
            self._disabled = True
            self._use_opencv = False
    
    def _init_raspberry_pi(self):
        """Raspberry Pi 平台初始化 - 使用 picamzero"""
        try:
            from picamzero import Camera
            self.cam = Camera()
            self._use_opencv = False
            print("[Camera] Raspberry Pi: picamzero")
        except ImportError:
            print("[Camera] Raspberry Pi: picamzero 未安装，尝试使用 OpenCV")
            try:
                self.cam = cv2.VideoCapture(0)
                if self.cam.isOpened():
                    self._use_opencv = True
                    print("[Camera] Raspberry Pi: OpenCV VideoCapture")
                else:
                    print("[Camera] 无法打开摄像头")
                    self._disabled = True
                    self._use_opencv = False
            except Exception:
                self._disabled = True
                self._use_opencv = False

    def get_encoded_image(self, output_path=None):
        """获取编码后的图像
        
        Args:
            output_path: 可选，保存图像的路径
            
        Returns:
            str: base64 编码的图像
        """
        if self._disabled:
            return None
        
        if output_path is None:
            output_path = "/tmp/duck_camera_capture.jpg"
        
        try:
            if self._use_opencv:
                ret, frame = self.cam.read()
                if not ret:
                    print("[Camera] 无法读取图像")
                    return None
                im = frame
            else:
                # picamzero
                im = self.cam.capture_array()
            
            # 处理图像
            im = cv2.resize(im, (512, 512))
            if len(im.shape) == 3 and im.shape[2] == 3:
                im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            im = cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE)
            
            # 保存图像
            cv2.imwrite(output_path, im)
            
            return self.encode_image(output_path)
        except Exception as e:
            print(f"[Camera] 捕获图像失败: {e}")
            return None

    def encode_image(self, image_path: str):
        """将图像文件编码为 base64
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            str: base64 编码的字符串
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def release(self):
        """释放摄像头资源"""
        if self._disabled:
            return
        
        if self._use_opencv and hasattr(self, 'cam'):
            self.cam.release()


if __name__ == "__main__":
    print(f"平台: {PLATFORM}")
    cam = Cam()
    
    if not cam._disabled:
        print("正在捕获图像...")
        encoded = cam.get_encoded_image("/tmp/test_capture.jpg")
        if encoded:
            print(f"图像已捕获，base64 长度: {len(encoded)}")
        else:
            print("图像捕获失败")
        cam.release()
    else:
        print("摄像头不可用")
