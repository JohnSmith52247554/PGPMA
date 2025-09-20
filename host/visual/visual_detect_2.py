import cv2
import numpy as np
import os
import time
from pyzbar import pyzbar
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from threading import Lock
import warnings
import logging
from pyzbar.pyzbar import decode as pyzbar_decode

from widgets.console import VisualConsole
from s_serial import Message, MsgType

# 忽略警告
warnings.filterwarnings("ignore", category=RuntimeWarning)

LOOP_FLAG = True
def set_loop_flag(flag):
    global LOOP_FLAG
    LOOP_FLAG = flag

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
#logger = logging.getLogger(__name__)

# 检查CUDA是否可用
CUDA_AVAILABLE = cv2.cuda.getCudaEnabledDeviceCount() > 0
#print(f"CUDA Available: {CUDA_AVAILABLE}")

# 全局参数
THRESH = 100  # Canny边缘检测阈值
N = 11  # 阈值级别数量
MIN_AREA = 1000  # 最小面积阈值
MAX_COSINE = 0.3  # 最大角度余弦值(用于检测直角)

# 坐标网格参数
GRID_SPACING = 50  # 网格间距(像素)
GRID_COLOR = (50, 50, 50)  # 网格线颜色
AXIS_COLOR_X = (0, 0, 255)  # X轴颜色(红色)
AXIS_COLOR_Y = (0, 255, 0)  # Y轴颜色(绿色)
AXIS_COLOR_Z = (255, 0, 0)  # Z轴颜色(蓝色)
GRID_ALPHA = 0.3  # 网格透明度
AXIS_LABEL_FONT = cv2.FONT_HERSHEY_SIMPLEX
AXIS_LABEL_SCALE = 0.5
AXIS_LABEL_THICKNESS = 1

# 方形合并参数
MERGE_DISTANCE_THRESHOLD = 30
MERGE_AREA_RATIO_THRESHOLD = 0.5
MERGE_ANGLE_THRESHOLD = 30

# 像素到毫米的转换
PX_TO_MM = 1.25# 0.5mm/像素
CAMERA_HEIGHT = 800  # 相机高度(mm)

# 数字显示参数
DIGIT_DISPLAY_SIZE = 100
DIGIT_DISPLAY_POSITION = (10, 10)
DIGIT_COLOR = (0, 255, 255)
DIGIT_FONT = cv2.FONT_HERSHEY_SIMPLEX
DIGIT_FONT_SCALE = 2
DIGIT_FONT_THICKNESS = 3

# 二维码显示参数
QR_DISPLAY_SIZE = 100
QR_DISPLAY_POSITION = (210, 10)
QR_COLOR = (0, 255, 0)

# 并行处理设置
MAX_WORKERS = 4  # 最大线程数

# 优化参数
GAUSSIAN_BLUR_SIZE = (3, 3)  # 高斯模糊核大小
USE_BLUR = True  # 是否使用轻度模糊

# 亮度调整参数
BRIGHTNESS_ADJUSTMENT_RATE = 0.1  # 亮度调整速率
TARGET_QR_BRIGHTNESS = 120  # 目标二维码亮度值
MIN_BRIGHTNESS = -50  # 最小亮度调整值
MAX_BRIGHTNESS = 50  # 最大亮度调整值

# 圆形检测参数
CIRCLE_MIN_DIST = 30  # 圆心之间的最小距离
CIRCLE_PARAM1 = 50  # 边缘检测阈值
CIRCLE_PARAM2 = 64  # 累加器阈值
CIRCLE_MIN_RADIUS = 10  # 最小半径
CIRCLE_MAX_RADIUS = 100  # 最大半径

# 输出全局变量
DETECTED = False
AXIS_X = 0
AXIS_Y = 0
ROT = 0
CURRENT_BRIGHTNESS = 0

# 安全状态记录
secure_status = {}  # 使用QR码ID作为键，True/False作为值
SECURE_COLOR = (0, 255, 0)  # 绿色表示安全
NOT_SECURE_COLOR = (0, 0, 255)  # 红色表示不安全
SECURE_LOCK = Lock()  # 安全状态数据锁

# 平滑处理参数
HISTORY_LENGTH = 5  # 使用最近5帧进行平滑
position_history = []

# 坐标历史记录
COORDINATE_HISTORY = deque(maxlen=100)  # 存储最近100个坐标点（约1秒数据）
COORD_LOCK = Lock()  # 坐标历史数据锁
LAST_AVG_TIME = time.time()  # 上次计算平均值的时间

# 优先级锁定机制参数
PRIORITY_LOCK_DURATION = 2.0  # 优先级锁定持续时间(秒)
priority_lock = None  # 当前锁定的二维码ID
priority_lock_time = 0  # 锁定开始时间
PRIORITY_LOCK = Lock()  # 优先级锁数据锁

# 放大搜索参数
ZOOM_FACTOR = 1.5  # 放大系数
MIN_RECT_AREA = 2000  # 最小矩形面积阈值
ZOOM_SEARCH_COLOR = (0, 165, 255)  # 橙色标记放大区域
DEBUG_MODE = True  # 调试模式开关
ZOOM_WINDOW_NAME = "Zoomed Area"
ZOOM_WINDOW_SIZE = (400, 400)  # 放大窗口尺寸
ZOOM_BORDER_COLOR = (0, 255, 255)  # 黄色边框
ZOOM_BORDER_THICKNESS = 2
ZOOM_ENABLED = True  # 是否启用放大功能
ZOOM_WINDOW_VISIBLE = False  # 放大窗口是否可见
LOCAL_SEARCH_RADIUS = 200  # 在最近二维码附近搜索的范围(像素)

# 调试颜色定义
DEBUG_COLORS = {
    'standard_qr': (0, 255, 0),  # 绿色 - 标准QR码
    'tilted_qr': (0, 255, 255),  # 黄色 - 倾斜QR码
    'zoomed_qr': (255, 165, 0),  # 橙色 - 放大区域检测到的QR码
    'square': (255, 0, 255),  # 紫色 - 检测到的方形
    'zoom_area': (0, 165, 255),  # 橙色 - 放大区域
}

# 存储最后一帧的zoom area图像
last_zoomed_frame = None
LAST_ZOOMED_FRAME_LOCK = Lock()

# 运动模糊处理参数
MOTION_WINDOW_SIZE = 5  # 时域分析帧数
MOTION_DEBLUR_ITER = 3  # 反卷积迭代次数
MIN_MOTION_THRESH = 2.0  # 最小有效运动像素/帧



class MotionBlurProcessor:
    """运动模糊二维码处理核心类"""

    def __init__(self):
        self.frame_buffer = deque(maxlen=MOTION_WINDOW_SIZE)
        self.motion_vectors = deque(maxlen=MOTION_WINDOW_SIZE - 1)
        self.lock = Lock()

    def estimate_motion(self, frame1, frame2):
        """改进的运动估计（结合光流和特征匹配）"""
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # 双策略运动估计
        flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        median_flow = np.median(flow.reshape(-1, 2), axis=0)

        if np.linalg.norm(median_flow) < MIN_MOTION_THRESH:
            # 小运动时使用特征点匹配验证
            orb = cv2.ORB_create(100)
            kp1, des1 = orb.detectAndCompute(gray1, None)
            kp2, des2 = orb.detectAndCompute(gray2, None)

            if des1 is not None and des2 is not None:
                bf = cv2.BFMatcher(cv2.NORM_HAMMING)
                matches = bf.knnMatch(des1, des2, k=2)
                good = [m for m, n in matches if m.distance < 0.75 * n.distance]

                if len(good) > 10:
                    src_pts = np.float32([kp1[m.queryIdx].pt for m in good])
                    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good])
                    feature_flow = np.median(dst_pts - src_pts, axis=0)
                    return feature_flow

        return median_flow

    def temporal_integration(self, frames, motions):
        """时域多帧融合（确保输出为三通道图像）"""
        if not frames or not motions:
            return None

        # 确保所有帧为三通道
        frames = [frame if len(frame.shape) == 3 else cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                  for frame in frames]

        h, w = frames[0].shape[:2]
        aligned = [frames[0]]

        # 对齐帧序列
        for i in range(1, len(frames)):
            dx, dy = motions[i - 1]
            M = np.float32([[1, 0, -dx], [0, 1, -dy]])
            aligned.append(cv2.warpAffine(frames[i], M, (w, h)))

        # 自适应加权融合（保持三通道）
        integrated = np.zeros_like(frames[0], dtype=np.float32)
        for i, frame in enumerate(aligned):
            weight = 0.5 + 0.5 * i / len(frames)
            integrated += frame.astype(np.float32) * weight

        # 归一化并转换为8位图像
        integrated = cv2.normalize(integrated / integrated.max(), None, 0, 255, cv2.NORM_MINMAX)
        return integrated.astype(np.uint8)

    def motion_deblur(self, image, motion_vector):
        """基于运动估计的反卷积"""
        angle = np.degrees(np.arctan2(motion_vector[1], motion_vector[0]))
        length = np.linalg.norm(motion_vector)

        if length < 1:  # 忽略微小运动
            return image

        # 生成运动模糊核
        kernel_size = int(length * 2) + 1
        kernel = np.zeros((kernel_size, kernel_size))
        center = (kernel_size // 2, kernel_size // 2)
        cv2.line(kernel, center,
                 (int(center[0] + length * np.cos(np.radians(angle))),
                  int(center[1] + length * np.sin(np.radians(angle)))),
                 1, thickness=1)
        kernel /= kernel.sum()

        # Richardson-Lucy反卷积
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        result = gray.copy()
        for _ in range(MOTION_DEBLUR_ITER):
            conv = cv2.filter2D(result, -1, kernel)
            ratio = cv2.divide(gray, conv + 1e-6, dtype=cv2.CV_32F)
            result *= cv2.filter2D(ratio, -1, kernel[::-1, ::-1])

        return cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX)

    def process_frame(self, frame):
        """处理单帧并更新缓冲区"""
        with self.lock:
            if len(self.frame_buffer) >= 1:
                prev_frame = self.frame_buffer[-1]
                motion = self.estimate_motion(prev_frame, frame)
                self.motion_vectors.append(motion)

            self.frame_buffer.append(frame)

            # 当缓冲足够时进行处理
            if len(self.frame_buffer) >= MOTION_WINDOW_SIZE:
                avg_motion = np.mean(self.motion_vectors, axis=0)
                integrated = self.temporal_integration(
                    list(self.frame_buffer),
                    list(self.motion_vectors))
                deblurred = self.motion_deblur(integrated, avg_motion)
                return deblurred
        return None


class QRDetector:
    """增强版二维码检测器（集成运动模糊处理）"""

    def __init__(self):
        self.motion_processor = MotionBlurProcessor()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.last_valid = None

    def detect_standard_qr(self, frame):
        """标准二维码检测"""
        return pyzbar_decode(frame)

    def detect_tilted_qr(self, frame):
        """倾斜二维码检测"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        results = []

        for cnt in contours:
            if cv2.contourArea(cnt) < 1000:
                continue

            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int32(box)

            # 透视变换校正
            width, height = int(rect[1][0]), int(rect[1][1])
            dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")
            M = cv2.getPerspectiveTransform(box.astype(np.float32), dst)
            warped = cv2.warpPerspective(frame, M, (width, height))

            decoded = pyzbar_decode(warped)
            for d in decoded:
                d.rect = box  # 保存原始位置
                results.append(d)
        return results

    def detect_motion_blur_qr(self, frame):
        """运动模糊二维码检测"""
        processed = self.motion_processor.process_frame(frame)
        if processed is not None:
            # 并行尝试多种解码方式
            futures = [
                self.executor.submit(self.detect_standard_qr, processed),
                self.executor.submit(self.detect_tilted_qr, processed)
            ]

            results = []
            for future in futures:
                try:
                    results.extend(future.result(timeout=0.5))
                except Exception as e:
                    #logger.warning(f"Decoding error: {str(e)}")
                    pass
            return results
        return []

    def multi_strategy_detect(self, frame):
        """多策略联合检测"""
        # 第一级：快速标准检测
        standard_results = self.detect_standard_qr(frame)
        if standard_results:
            return standard_results

        # 第二级：运动模糊处理
        motion_results = self.detect_motion_blur_qr(frame)
        if motion_results:
            return motion_results

        # 第三级：倾斜检测
        return self.detect_tilted_qr(frame)


class GPUAccelerator:
    def __init__(self):
        self.canny_detector = cv2.cuda.createCannyEdgeDetector(50, 150) if CUDA_AVAILABLE else None
        self.clahe = cv2.cuda.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)) if CUDA_AVAILABLE else None
        self.gaussian_blur = (3, 3)
        self.stream = cv2.cuda_Stream() if CUDA_AVAILABLE else None

    def upload_to_gpu(self, frame):
        if not CUDA_AVAILABLE:
            return None
        gpu_frame = cv2.cuda_GpuMat()
        gpu_frame.upload(frame, stream=self.stream)
        return gpu_frame

    def preprocess_gpu(self, gpu_frame):
        if not CUDA_AVAILABLE or gpu_frame is None:
            return None

        # GPU处理流水线
        gpu_gray = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY, stream=self.stream)
        gpu_blur = cv2.cuda.GaussianBlur(gpu_gray, self.gaussian_blur, 0, stream=self.stream)

        if self.clahe:
            gpu_clahe = self.clahe.apply(gpu_gray, stream=self.stream)
        else:
            gpu_clahe = None

        if self.canny_detector:
            gpu_edges = self.canny_detector.detect(gpu_blur, stream=self.stream)
        else:
            gpu_edges = None

        return {
            'gray': gpu_gray,
            'blurred': gpu_blur,
            'clahe': gpu_clahe,
            'edges': gpu_edges
        }

    def download_from_gpu(self, gpu_mat):
        if not CUDA_AVAILABLE or gpu_mat is None:
            return None
        return gpu_mat.download(stream=self.stream)


# 初始化GPU加速器
gpu_accel = GPUAccelerator()


def cv_show(name, img):
    """显示图像并等待按键"""
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



def smooth_position(current_center, history):
    """使用移动平均平滑中心点位置"""
    if current_center is None:
        return None

    history.append(current_center)
    if len(history) > HISTORY_LENGTH:
        history.pop(0)

    if not history:
        return current_center

    return (sum(p[0] for p in history) / len(history),
            sum(p[1] for p in history) / len(history))


def order_points(pts):
    """将点排序为左上、右上、右下、左下的顺序"""
    if pts is None or len(pts) < 4:
        return None

    x_sorted = pts[np.argsort(pts[:, 0])]
    left_most = x_sorted[:2]
    right_most = x_sorted[2:]
    left_sorted = left_most[np.argsort(left_most[:, 1])]
    top_left = left_sorted[0]
    bottom_left = left_sorted[1]
    right_sorted = right_most[np.argsort(right_most[:, 1])]
    top_right = right_sorted[0]
    bottom_right = right_sorted[1]
    return np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")


def four_point_transform(image, pts):
    """执行四点透视变换"""
    if image is None or pts is None or len(pts) < 4:
        return None

    rect = order_points(pts)
    if rect is None:
        return None

    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped


def angle(pt1, pt2, pt0):
    """计算三个点之间的角度余弦值"""
    if pt1 is None or pt2 is None or pt0 is None:
        return 0.0

    vec1 = np.array([pt1[0] - pt0[0], pt1[1] - pt0[1]], dtype=np.float64)
    vec2 = np.array([pt2[0] - pt0[0], pt2[1] - pt0[1]], dtype=np.float64)

    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 * norm2 < 1e-10:
        return 0.0

    cosine = dot / (norm1 * norm2)
    return np.clip(cosine, -1.0, 1.0)


def is_border_contour(contour, image_shape, margin=20):
    """检查轮廓是否在图像边缘"""
    if contour is None or image_shape is None:
        return True

    height, width = image_shape[:2]
    for point in contour:
        if point is None or len(point) < 1:
            continue
        x, y = point[0]
        if (x < margin or x > width - margin or
                y < margin or y > height - margin):
            return True
    return False


def is_not_barcode(contour, barcode_rects, intersection_threshold=0.01, area_ratio_threshold=0.7):
    """
    增强版二维码判断（新增面积比例检测）
    完全重写以解决NoneType错误
    """
    # 快速检查：如果没有二维码或轮廓无效
    if not barcode_rects or contour is None or len(contour) < 3:
        return True

    try:
        # 优化轮廓处理（确保二维数组）
        contour = contour.reshape(-1, 2) if contour.ndim == 3 else contour
        if len(contour) < 3:  # 至少需要3个点构成多边形
            return True

        # 计算轮廓面积
        contour_area = cv2.contourArea(contour)
        if contour_area < 1:
            return True

        # 使用更高效的多边形近似
        epsilon = 0.01 * cv2.arcLength(contour, True)
        contour_poly = cv2.approxPolyDP(contour, epsilon, True)

        # 检查近似后的轮廓有效性
        if contour_poly is None or len(contour_poly) < 3:
            return True

        # 确保contour_poly是二维数组 (N,2)
        contour_poly = contour_poly.reshape(-1, 2)
        if len(contour_poly) < 3:
            return True

        # 预计算轮廓边界
        min_x, min_y = np.min(contour_poly, axis=0)
        max_x, max_y = np.max(contour_poly, axis=0)

        for b_rect in barcode_rects:
            # 快速检查：矩形是否有效
            if b_rect is None or len(b_rect) != 4:
                continue

            # 解析二维码矩形
            bx, by, bw, bh = map(int, b_rect)
            qr_area = bw * bh

            # ========== 新增：面积比例快速判断 ==========
            area_ratio = min(contour_area, qr_area) / max(contour_area, qr_area)
            if area_ratio > area_ratio_threshold:
                return False  # 面积相似度超过阈值，直接判定为二维码

            # 快速边界检查
            if (min_x > bx + bw or max_x < bx or
                    min_y > by + bh or max_y < by):
                continue

            # 计算相交面积
            intersection_area = 0
            try:
                # 创建二维码轮廓
                qr_contour = np.array([
                    [bx, by],
                    [bx + bw, by],
                    [bx + bw, by + bh],
                    [bx, by + bh]
                ], dtype=np.int32)

                # 方法1：使用凸包相交计算
                if len(contour_poly) >= 3 and len(qr_contour) >= 3:
                    _, intersect = cv2.intersectConvexConvex(
                        np.ascontiguousarray(contour_poly, dtype=np.float32),
                        np.ascontiguousarray(qr_contour, dtype=np.float32)
                    )
                    if intersect is not None and len(intersect) >= 3:
                        intersection_area = cv2.contourArea(intersect)
                    else:
                        # 方法2：矩形重叠计算
                        x_overlap = max(0, min(max_x, bx + bw) - max(min_x, bx))
                        y_overlap = max(0, min(max_y, by + bh) - max(min_y, by))
                        intersection_area = x_overlap * y_overlap

                # 双条件判断（相交比例或面积比例）
                intersection_ratio = intersection_area / min(contour_area, qr_area)
                if (intersection_ratio > intersection_threshold or
                        area_ratio > area_ratio_threshold):
                    return False

            except Exception as e:
                print(f"Intersection calc skipped: {str(e)}")
                continue

    except Exception as e:
        print(f"Error in is_not_barcode: {str(e)}")
        return True  # 出错时保守返回True

    return True


def find_largest_rectangle(contours, min_area=1000):
    """从轮廓中找出面积最大的矩形"""
    max_area = 0
    best_rect = None

    if contours is None:
        return None

    for cnt in contours:
        if cnt is None or len(cnt) < 3:
            continue

        # 多边形近似
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if approx is None or len(approx) != 4:
            continue

        area = cv2.contourArea(approx)
        if area > max_area and area > min_area:
            max_area = area
            best_rect = approx.reshape(4, 2)

    return best_rect


def find_zoom_area(contours, min_area=2000, qr_detected=False):
    """寻找适合放大的区域（仅在未检测到二维码时）"""
    if qr_detected or contours is None:
        return None

    # 找出面积最大的轮廓
    max_area = 0
    best_contour = None

    for cnt in contours:
        if cnt is None or len(cnt) < 3:
            continue

        area = cv2.contourArea(cnt)
        if area > max_area and area > min_area:
            max_area = area
            best_contour = cnt

    if best_contour is None:
        return None

    # 获取最小外接矩形
    rect = cv2.minAreaRect(best_contour)
    box = cv2.boxPoints(rect)
    box = np.int32(box)

    return box


def show_zoomed_window(image, zoom_area):
    """显示放大窗口并保存最后一帧"""
    global last_zoomed_frame

    if image is None or zoom_area is None:
        # 显示空白窗口
        blank = np.zeros((ZOOM_WINDOW_SIZE[1], ZOOM_WINDOW_SIZE[0], 3), dtype=np.uint8)
        cv2.putText(blank, "No Zoom Area", (50, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow(ZOOM_WINDOW_NAME, blank)
        return

    try:
        # 执行透视变换
        rect = cv2.minAreaRect(zoom_area)
        box = cv2.boxPoints(rect)
        box = np.int64(box)

        width = int(rect[1][0])
        height = int(rect[1][1])

        dst = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(box.astype(np.float32), dst)
        warped = cv2.warpPerspective(image, M, (width, height))

        if warped is None or warped.size == 0:
            raise ValueError("Invalid warped image")

        # 调整大小以适应窗口
        zoomed = cv2.resize(warped, ZOOM_WINDOW_SIZE)

        # 保存最后一帧zoom area图像
        with LAST_ZOOMED_FRAME_LOCK:
            last_zoomed_frame = zoomed.copy()

        # 添加边框和标题
        cv2.rectangle(zoomed, (0, 0),
                      (zoomed.shape[1] - 1, zoomed.shape[0] - 1),
                      ZOOM_BORDER_COLOR, ZOOM_BORDER_THICKNESS)

        cv2.putText(zoomed, "ZOOMED VIEW", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, ZOOM_BORDER_COLOR, 2)

        cv2.putText(zoomed, f"Zoom: {ZOOM_FACTOR}x", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, ZOOM_BORDER_COLOR, 1)

        cv2.imshow(ZOOM_WINDOW_NAME, zoomed)
    except Exception as e:
        print(f"Error showing zoomed window: {str(e)}")
        blank = np.zeros((ZOOM_WINDOW_SIZE[1], ZOOM_WINDOW_SIZE[0], 3), dtype=np.uint8)
        cv2.putText(blank, "Error in Zoom", (50, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow(ZOOM_WINDOW_NAME, blank)


def analyze_last_zoomed_frame():
    """分析最后一帧zoom area图像中的二维码"""
    global last_zoomed_frame

    with LAST_ZOOMED_FRAME_LOCK:
        if last_zoomed_frame is None:
            print("No zoomed frame available for analysis")
            return None

        # 在zoom area中检测二维码
        decoded = pyzbar.decode(last_zoomed_frame)
        results = []

        for barcode in decoded:
            if barcode is None:
                # 在图像上显示"未找到二维码"的文字
                continue

            (x, y, w, h) = barcode.rect
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            lines = barcode_data.split('\n')
            qr_id = int(lines[0]) if lines and lines[0].isdigit() else 0
            direction = lines[1] if len(lines) > 1 else "unknown"
            secure = lines[2] if len(lines) > 2 else "unknown"

            results.append({
                "data": barcode_data,
                "type": barcode_type,
                "position": (x, y, w, h),
                "id": qr_id,
                "direction": direction,
                "secure": secure,
                "source": "zoomed_frame_analysis"
            })

        return results


def zoom_and_search(image, rect, zoom_factor=1.5):
    """在指定矩形区域内放大并搜索二维码"""
    if image is None or rect is None:
        return None

    try:
        # 获取矩形边界
        x_coords = rect[:, 0]
        y_coords = rect[:, 1]
        x1, x2 = int(np.min(x_coords)), int(np.max(x_coords))
        y1, y2 = int(np.min(y_coords)), int(np.max(y_coords))

        # 计算放大区域
        width = x2 - x1
        height = y2 - y1
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        # 应用放大因子
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)

        # 计算新的边界（确保不超出图像范围）
        x1 = max(0, cx - new_width // 2)
        x2 = min(image.shape[1], cx + new_width // 2)
        y1 = max(0, cy - new_height // 2)
        y2 = min(image.shape[0], cy + new_height // 2)

        # 裁剪和放大区域
        zoomed_region = image[y1:y2, x1:x2]
        if zoomed_region is None or zoomed_region.size == 0:
            return None

        # 在放大区域中搜索二维码
        zoomed_qr = pyzbar.decode(zoomed_region)
        results = []

        for barcode in zoomed_qr:
            if barcode is None:
                continue

            (x, y, w, h) = barcode.rect
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            lines = barcode_data.split('\n')
            qr_id = int(lines[0]) if lines and lines[0].isdigit() else 0
            direction = lines[1] if len(lines) > 1 else "unknown"
            secure = lines[2] if len(lines) > 2 else "unknown"

            # 调整坐标到原始图像坐标系
            adjusted_rect = (x + x1, y + y1, w, h)

            results.append({
                "data": barcode_data,
                "type": barcode_type,
                "position": adjusted_rect,
                "id": qr_id,
                "direction": direction,
                "secure": secure,
                "source": "zoomed"  # 标记为放大区域检测到的
            })

        return results
    except Exception as e:
        print(f"Error in zoom_and_search: {str(e)}")
        return None


def find_squares_optimized(image):
    """优化后的方形检测函数（支持GPU加速）"""
    if image is None:
        return []

    if CUDA_AVAILABLE:
        # GPU加速路径
        gpu_frame = gpu_accel.upload_to_gpu(image)
        processed = gpu_accel.preprocess_gpu(gpu_frame)

        if processed and processed['edges']:
            edges = gpu_accel.download_from_gpu(processed['edges'])
        else:
            edges = None
    else:
        # CPU路径
        edges = None

    if edges is None:
        # 回退到CPU处理
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, GAUSSIAN_BLUR_SIZE, 0)
        edges = cv2.Canny(blurred, 0, THRESH)
        edges = cv2.dilate(edges, None)

    barcodes = pyzbar.decode(image)
    barcode_rects = [barcode.rect for barcode in barcodes if hasattr(barcode, 'rect')]

    squares = []
    for l in range(N):
        if l == 0:
            current_edges = edges
        else:
            if CUDA_AVAILABLE and processed and processed['blurred']:
                blurred_gpu = processed['blurred']
                _, current_edges = cv2.cuda.threshold(blurred_gpu, (l + 1) * 255 // N, 255, cv2.THRESH_BINARY)
                current_edges = gpu_accel.download_from_gpu(current_edges)
            else:
                _, current_edges = cv2.threshold(blurred, (l + 1) * 255 // N, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(current_edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if contour is None or len(contour) < 3:
                continue

            if is_border_contour(contour, image.shape):
                continue

            if not is_not_barcode(contour, barcode_rects):
                continue

            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if approx is None or len(approx) != 4:
                continue

            area = cv2.contourArea(approx)
            if area > MIN_AREA and cv2.isContourConvex(approx):
                max_cosine = 0
                for j in range(4):
                    cosine = abs(angle(
                        approx[j][0],
                        approx[(j + 2) % 4][0],
                        approx[(j + 1) % 4][0]
                    ))
                    max_cosine = max(max_cosine, cosine)

                if max_cosine < MAX_COSINE:
                    approx = approx.reshape(4, 2).astype(np.float32)
                    squares.append(approx)

    return squares


def merge_close_squares(squares):
    """合并接近的方形"""
    if squares is None or len(squares) < 2:
        return squares

    centers = []
    areas = []
    rotations = []

    for square in squares:
        if square is None or len(square) < 4:
            continue

        center = np.mean(square, axis=0)
        centers.append(center)
        areas.append(cv2.contourArea(square))

        pt0 = square[0]
        pt1 = square[1]
        dx = pt1[0] - pt0[0]
        dy = pt1[1] - pt0[1]
        rotations.append(np.degrees(np.arctan2(dy, dx)))

    groups = []
    visited = [False] * len(squares)

    for i in range(len(squares)):
        if visited[i] or squares[i] is None:
            continue

        group = [i]
        visited[i] = True

        for j in range(i + 1, len(squares)):
            if visited[j] or squares[j] is None:
                continue

            dist = np.linalg.norm(centers[i] - centers[j])
            area_ratio = min(areas[i], areas[j]) / max(areas[i], areas[j])
            angle_diff = min(abs(rotations[i] - rotations[j]), 360 - abs(rotations[i] - rotations[j]))

            if (dist < MERGE_DISTANCE_THRESHOLD and
                    area_ratio > MERGE_AREA_RATIO_THRESHOLD and
                    angle_diff < MERGE_ANGLE_THRESHOLD):
                group.append(j)
                visited[j] = True

        groups.append(group)

    merged_squares = []
    for group in groups:
        if len(group) == 1:
            merged_squares.append(squares[group[0]])
        else:
            merged_points = np.zeros((4, 2), dtype=np.float32)
            max_area_idx = group[0]
            for idx in group:
                if areas[idx] > areas[max_area_idx]:
                    max_area_idx = idx

            ref_square = squares[max_area_idx]
            for k in range(4):
                point_sum = np.zeros(2, dtype=np.float32)
                count = 0

                for idx in group:
                    min_dist = float('inf')
                    closest_point = None

                    for m in range(4):
                        dist = np.linalg.norm(ref_square[k] - squares[idx][m])
                        if dist < min_dist:
                            min_dist = dist
                            closest_point = squares[idx][m]

                    if closest_point is not None:
                        point_sum += closest_point
                        count += 1

                if count > 0:
                    merged_points[k] = point_sum / count
                else:
                    merged_points[k] = ref_square[k]

            merged_squares.append(merged_points)

    return merged_squares


def create_centered_coordinate_grid(width, height):
    """创建以帧中心为原点的坐标网格"""
    if width <= 0 or height <= 0:
        return None

    grid_image = np.zeros((height, width, 3), dtype=np.uint8)
    cx = width // 2
    cy = height // 2

    for y in range(0, height, GRID_SPACING):
        thickness = 3 if y == cy else 1
        color = AXIS_COLOR_Y if y == cy else GRID_COLOR
        cv2.line(grid_image, (0, y), (width, y), color, thickness)

        if abs(y - cy) % (GRID_SPACING * 5) == 0:
            coord = (y - cy) // 1
            mm_y = coord * PX_TO_MM
            label = f"{int(mm_y)}mm" if coord != 0 else "Y=0"
            label_x = 5
            label_y = y + 5 if y < cy else y - 5
            cv2.putText(grid_image, label, (label_x, label_y),
                        AXIS_LABEL_FONT, AXIS_LABEL_SCALE, color, AXIS_LABEL_THICKNESS)

    for x in range(0, width, GRID_SPACING):
        thickness = 3 if x == cx else 1
        color = AXIS_COLOR_X if x == cx else GRID_COLOR
        cv2.line(grid_image, (x, 0), (x, height), color, thickness)

        if abs(x - cx) % (GRID_SPACING * 5) == 0:
            coord = (x - cx) // 1
            mm_x = coord * PX_TO_MM
            label = f"{int(mm_x)}mm" if coord != 0 else "X=0"
            label_x = x - 20 if x < cx else x - 25
            label_y = 20
            cv2.putText(grid_image, label, (label_x, label_y),
                        AXIS_LABEL_FONT, AXIS_LABEL_SCALE, color, AXIS_LABEL_THICKNESS)

    z_length = GRID_SPACING * 2
    cv2.arrowedLine(grid_image, (cx, cy), (cx - z_length, cy - z_length), AXIS_COLOR_Z, 2, tipLength=0.2)
    cv2.putText(grid_image, "Z", (cx - z_length - 20, cy - z_length - 10),
                AXIS_LABEL_FONT, AXIS_LABEL_SCALE, AXIS_COLOR_Z, AXIS_LABEL_THICKNESS)

    cv2.drawMarker(grid_image, (cx, cy), (200, 200, 200), cv2.MARKER_CROSS, 20, 2)
    cv2.putText(grid_image, "O(0,0)", (cx + 5, cy - 10),
                AXIS_LABEL_FONT, AXIS_LABEL_SCALE, (200, 200, 200), AXIS_LABEL_THICKNESS)

    cv2.putText(grid_image, "X", (width - 30, cy - 10),
                AXIS_LABEL_FONT, AXIS_LABEL_SCALE, AXIS_COLOR_X, AXIS_LABEL_THICKNESS)
    cv2.putText(grid_image, "Y", (cx + 10, 30),
                AXIS_LABEL_FONT, AXIS_LABEL_SCALE, AXIS_COLOR_Y, AXIS_LABEL_THICKNESS)

    return grid_image


def calculate_object_position(square, frame_width, frame_height):
    """计算物体相对于中心的位置"""
    if square is None or len(square) < 4 or frame_width <= 0 or frame_height <= 0:
        return None, 0, 0, 0, 0

    center = np.mean(square, axis=0)
    cx, cy = center
    offset_x = cx - frame_width // 2
    offset_y = cy - frame_height // 2
    mm_x = offset_x * PX_TO_MM
    mm_y = offset_y * PX_TO_MM
    mm_z = CAMERA_HEIGHT

    pt0 = square[0]
    pt1 = square[1]
    dx = pt1[0] - pt0[0]
    dy = pt1[1] - pt0[1]
    rotation = np.degrees(np.arctan2(dy, dx))

    # 将角度限制在0~90度范围内
    rotation = rotation % 90

    return center, mm_x, mm_y, mm_z, rotation


def calculate_qr_position(qr_polygon, frame_width, frame_height):
    """计算QR码相对于中心的位置（使用多边形顶点）"""
    if qr_polygon is None or len(qr_polygon) < 4 or frame_width <= 0 or frame_height <= 0:
        return None, 0, 0, 0, 0

    # 计算中心点
    center = np.mean(qr_polygon, axis=0)
    cx, cy = center

    # 计算相对于图像中心的偏移
    offset_x = cx - frame_width // 2
    offset_y = cy - frame_height // 2

    # 转换为毫米
    mm_x = offset_x * PX_TO_MM
    mm_y = offset_y * PX_TO_MM
    mm_z = CAMERA_HEIGHT

    # 计算旋转角度（使用第一条边的角度）
    pt0 = qr_polygon[0]
    pt1 = qr_polygon[1]
    dx = pt1[0] - pt0[0]
    dy = pt1[1] - pt0[1]
    rotation = np.degrees(np.arctan2(dy, dx))

    return center, mm_x, mm_y, mm_z, rotation


def parse_qr_data(qr_data):
    #id接口
    #第一行：id
    #第二行：分拣方向
    #第三行：是否经过安检
    """解析二维码数据，提取ID和方向"""
    if not qr_data:
        return 0, "unknown", "unknown"

    lines = qr_data.split('\n')
    if len(lines) >= 3:
        try:
            qr_id = int(lines[0].strip())
            direction = lines[1].strip()
            secure = lines[2].strip()
            return qr_id, direction, secure
        except ValueError:
            return 0, "unknown", "unknown"
    if len(lines) == 2:
        try:
            qr_id = int(lines[0].strip())
            direction = lines[1].strip()
            return qr_id, direction, "unknown"
        except ValueError:
            return 0, "unknown", "unknown"
    if len(lines) == 1:
        try:
            qr_id = int(lines[0].strip())
            return qr_id, "unknown", "unknown"
        except ValueError:
            return 0, "unknown", "unknown"
    return 0, "unknown", "unknown"


def preprocess_for_qr_detection(image):
    """为QR码检测准备图像的多层次处理（支持GPU加速）"""
    if image is None:
        return None

    if CUDA_AVAILABLE:
        # GPU加速路径
        gpu_frame = gpu_accel.upload_to_gpu(image)
        processed = gpu_accel.preprocess_gpu(gpu_frame)

        # 下载处理后的图像
        gray = gpu_accel.download_from_gpu(processed['gray']) if processed and processed['gray'] else None
        blurred = gpu_accel.download_from_gpu(processed['blurred']) if processed and processed['blurred'] else None
        clahe_img = gpu_accel.download_from_gpu(processed['clahe']) if processed and processed['clahe'] else None
        edges = gpu_accel.download_from_gpu(processed['edges']) if processed and processed['edges'] else None
    else:
        # CPU路径
        gray = None
        blurred = None
        clahe_img = None
        edges = None

    # 回退到CPU处理
    if gray is None:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if blurred is None:
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    if clahe_img is None:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(gray)
    if edges is None:
        edges = cv2.Canny(gray, 50, 150)

    # 形态学操作（通常在CPU上执行）
    kernel = np.ones((3, 3), np.uint8)
    morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    # 自适应阈值（通常在CPU上执行）
    adaptive = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 11, 2)

    return {
        'original': image.copy(),
        'gray': gray,
        'blurred': blurred,
        'adaptive': adaptive,
        'clahe': clahe_img,
        'edges': edges,
        'morph': morph
    }


def show_processed_images(processed_images):
    """显示所有处理后的图像"""
    if processed_images is None:
        return

    # 创建空白画布
    canvas_width = 800
    canvas_height = 600
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

    # 定义每个小图像的位置和大小
    cell_width = canvas_width // 3
    cell_height = canvas_height // 3

    # 放置原始图像
    resized = cv2.resize(processed_images['original'], (cell_width, cell_height))
    canvas[0:cell_height, 0:cell_width] = resized
    cv2.putText(canvas, "Original", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # 放置灰度图像
    gray = cv2.cvtColor(processed_images['gray'], cv2.COLOR_GRAY2BGR)
    resized = cv2.resize(gray, (cell_width, cell_height))
    canvas[0:cell_height, cell_width:2 * cell_width] = resized
    cv2.putText(canvas, "Gray", (cell_width + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # 放置模糊图像
    blurred = cv2.cvtColor(processed_images['blurred'], cv2.COLOR_GRAY2BGR)
    resized = cv2.resize(blurred, (cell_width, cell_height))
    canvas[0:cell_height, 2 * cell_width:3 * cell_width] = resized
    cv2.putText(canvas, "Blurred", (2 * cell_width + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # 放置自适应阈值图像
    adaptive = cv2.cvtColor(processed_images['adaptive'], cv2.COLOR_GRAY2BGR)
    resized = cv2.resize(adaptive, (cell_width, cell_height))
    canvas[cell_height:2 * cell_height, 0:cell_width] = resized
    cv2.putText(canvas, "Adaptive", (10, cell_height + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # 放置CLAHE图像
    clahe = cv2.cvtColor(processed_images['clahe'], cv2.COLOR_GRAY2BGR)
    resized = cv2.resize(clahe, (cell_width, cell_height))
    canvas[cell_height:2 * cell_height, cell_width:2 * cell_width] = resized
    cv2.putText(canvas, "CLAHE", (cell_width + 10, cell_height + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # 放置边缘图像
    edges = cv2.cvtColor(processed_images['edges'], cv2.COLOR_GRAY2BGR)
    resized = cv2.resize(edges, (cell_width, cell_height))
    canvas[cell_height:2 * cell_height, 2 * cell_width:3 * cell_width] = resized
    cv2.putText(canvas, "Edges", (2 * cell_width + 10, cell_height + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # 显示画布
    cv2.imshow("Processed Images", canvas)


def detect_and_decode_qrcode(image):
    """改进的QR码检测和解码函数（使用新的时域分析版本）"""
    if image is None:
        return []

    detector = QRDetector()
    results = detector.multi_strategy_detect(image)

    formatted_results = []
    for barcode in results:
        if barcode is None:
            continue

        # 获取位置信息
        if hasattr(barcode, 'rect'):
            (x, y, w, h) = barcode.rect
        else:
            # 如果没有rect属性，则使用多边形的最小外接矩形
            if hasattr(barcode, 'polygon'):
                polygon = barcode.polygon
                points = np.array([[p.x, p.y] for p in polygon])
                x, y, w, h = cv2.boundingRect(points)
            else:
                continue  # 跳过没有位置信息的二维码

        # 获取多边形顶点
        if hasattr(barcode, 'polygon'):
            polygon = barcode.polygon
            qr_polygon = np.array([[p.x, p.y] for p in polygon], dtype=np.float32)
        else:
            qr_polygon = np.array([
                [x, y],
                [x + w, y],
                [x + w, y + h],
                [x, y + h]
            ], dtype=np.float32)

        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        qr_id, direction, secure = parse_qr_data(barcode_data)

        formatted_results.append({
            "data": barcode_data,
            "type": barcode_type,
            "position": (x, y, w, h),
            "polygon": qr_polygon,
            "id": qr_id,
            "direction": direction,
            "secure": secure,
            "source": "standard_qr" if hasattr(barcode, 'rect') else "tilted_qr"
        })

    return formatted_results

def detect_tilted_qrcode(image):
    """改进的倾斜QR码检测函数（使用新的时域分析版本）"""
    # 这个功能已经被整合到QRDetector类中
    return []


def create_qr_display(qr_data, size=100):
    """为QR码数据创建显示"""
    if not qr_data:
        qr_data = ""

    display = np.zeros((size, size, 3), dtype=np.uint8)
    cv2.rectangle(display, (0, 0), (size - 1, size - 1), (100, 100, 100), 2)

    max_line_length = 10
    lines = []
    current_line = ""

    for word in qr_data.split():
        if len(current_line) + len(word) + 1 <= max_line_length:
            current_line += (" " + word if current_line else word)
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    font_scale = min(0.5, 0.7 / max(1, len(lines)))
    line_height = int(size * 0.8 / max(3, len(lines)))

    for i, line in enumerate(lines):
        text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)[0]
        text_x = (size - text_size[0]) // 2
        text_y = size // 2 - (len(lines) // 2 - i) * line_height

        cv2.putText(display, line, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 2)
        cv2.putText(display, line, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, QR_COLOR, 1)

    return display


def save_squares(orig_image, squares, output_dir="detected_squares"):
    """保存所有检测到的方形"""
    if orig_image is None or squares is None:
        return

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    for i, square in enumerate(squares):
        if square is None or len(square) < 4:
            continue

        warped = four_point_transform(orig_image, square)
        if warped is None:
            continue

        output_path = os.path.join(output_dir, f"square_{timestamp}_{i + 1}.jpg")
        cv2.imwrite(output_path, warped)
        print(f"Square {i + 1} saved as: {output_path}")
        cv2.imshow(f"Square {i + 1}", warped)


def update_coordinate_history(console : VisualConsole) -> None | dict:
    """更新坐标历史记录并计算平均值"""
    global COORDINATE_HISTORY, LAST_AVG_TIME, DETECTED, AXIS_X, AXIS_Y, ROT

    current_time = time.time()

    with COORD_LOCK:
        detected = DETECTED
        x, y, rot = AXIS_X, AXIS_Y, ROT

    if detected:
        with COORD_LOCK:
            COORDINATE_HISTORY.append({
                'time': current_time,
                'x': x,
                'y': y,
                'rot': rot
            })

    if current_time - LAST_AVG_TIME >= 1.0:
        LAST_AVG_TIME = current_time

        with COORD_LOCK:
            COORDINATE_HISTORY = deque(
                [d for d in COORDINATE_HISTORY
                 if current_time - d['time'] <= 1.0],
                maxlen=100
            )

            if COORDINATE_HISTORY and DETECTED:
                #坐标参数：avg_x,avg_y,avg_rot是三个接口
                avg_x = sum(d['x'] for d in COORDINATE_HISTORY) / len(COORDINATE_HISTORY)
                avg_y = sum(d['y'] for d in COORDINATE_HISTORY) / len(COORDINATE_HISTORY)
                avg_rot = sum(d['rot'] for d in COORDINATE_HISTORY) / len(COORDINATE_HISTORY)

                '''
                print(f"[{time.strftime('%H:%M:%S')}] 平均坐标 - "
                      f"X: {avg_x:.1f}mm, Y: {avg_y:.1f}mm, 旋转: {avg_rot:.1f}° "
                      f"(基于{len(COORDINATE_HISTORY)}帧)")
                '''
                console.add_message(f"[{time.strftime('%H:%M:%S')}] 平均坐标 - "
                      f"X: {avg_x:.1f}mm, Y: {avg_y:.1f}mm, 旋转: {avg_rot:.1f}° "
                      f"(基于{len(COORDINATE_HISTORY)}帧)")
                return {
                    'x': AXIS_X,
                    'y': AXIS_Y,
                    'rot': ROT
                }

            else:
                #print(f"[{time.strftime('%H:%M:%S')}] 未检测到目标")
                console.add_message(f"[{time.strftime('%H:%M:%S')}] 未检测到目标")
                return None


def adjust_brightness(image, brightness=0):
    """调整图像的亮度"""
    if image is None:
        return None

    if brightness != 0:
        image = cv2.convertScaleAbs(image, alpha=1.0, beta=brightness)
    return image


def calculate_qr_brightness(image, qr_rect):
    """计算二维码区域的平均亮度"""
    if image is None or qr_rect is None or len(qr_rect) != 4:
        return None

    x, y, w, h = qr_rect

    if w <= 0 or h <= 0:
        return None

    height, width = image.shape[:2]
    x1 = max(0, min(x, width - 1))
    y1 = max(0, min(y, height - 1))
    x2 = max(0, min(x + w, width - 1))
    y2 = max(0, min(y + h, height - 1))

    if x2 <= x1 or y2 <= y1:
        return None

    qr_roi = image[y1:y2, x1:x2]
    if qr_roi.size == 0:
        return None

    gray = cv2.cvtColor(qr_roi, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)


def update_brightness(image, qr_rects):
    """根据二维码区域更新亮度设置"""
    global CURRENT_BRIGHTNESS

    if image is None or not qr_rects:
        return adjust_brightness(image, CURRENT_BRIGHTNESS)

    qr_rect = qr_rects[0]["position"]
    current_brightness = calculate_qr_brightness(image, qr_rect)

    if current_brightness is None:
        return adjust_brightness(image, CURRENT_BRIGHTNESS)

    brightness_diff = TARGET_QR_BRIGHTNESS - current_brightness
    brightness_adjustment = brightness_diff * BRIGHTNESS_ADJUSTMENT_RATE
    CURRENT_BRIGHTNESS += brightness_adjustment
    CURRENT_BRIGHTNESS = np.clip(CURRENT_BRIGHTNESS, MIN_BRIGHTNESS, MAX_BRIGHTNESS)

    adjusted_image = adjust_brightness(image, CURRENT_BRIGHTNESS)
    return adjusted_image


def update_secure_status(qr_id, has_red_circle):
    """更新安全状态记录"""
    global secure_status
    with SECURE_LOCK:
        if qr_id not in secure_status:
            secure_status[qr_id] = has_red_circle
        elif has_red_circle:
            secure_status[qr_id] = True  # 一旦检测到红色圆形就永久标记


def get_secure_status(qr_id):
    """获取安全状态"""
    with SECURE_LOCK:
        return secure_status.get(qr_id, False)


def update_priority_lock(current_qr_id, current_time):
    """更新优先级锁定状态"""
    global priority_lock, priority_lock_time

    with PRIORITY_LOCK:
        if priority_lock is None:
            # 没有锁定，直接锁定当前最高ID的二维码
            priority_lock = current_qr_id
            priority_lock_time = current_time
        elif current_qr_id > priority_lock:
            # 检测到更高ID的二维码，更新锁定
            priority_lock = current_qr_id
            priority_lock_time = current_time
        elif current_time - priority_lock_time > PRIORITY_LOCK_DURATION:
            # 锁定超时，释放锁定
            priority_lock = None
            priority_lock_time = 0


def should_keep_priority_lock(current_time):
    """检查是否应该保持当前优先级锁定"""
    with PRIORITY_LOCK:
        if priority_lock is None:
            return False
        return current_time - priority_lock_time <= PRIORITY_LOCK_DURATION


def draw_debug_info(image, detections):
    """绘制调试信息（检测来源标记）"""
    if not DEBUG_MODE or image is None or not detections:
        return

    for det in detections:
        if "position" not in det:
            continue

        x, y, w, h = det["position"]
        det_type = det.get("detection_type", "unknown")

        # 根据检测类型选择颜色
        color = DEBUG_COLORS.get(det_type, (255, 255, 255))

        # 绘制检测类型标签
        label = f"{det_type.upper()}"
        cv2.putText(image, label, (x, y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # 绘制来源信息
        if "source" in det:
            source_label = f"Source: {det['source']}"
            cv2.putText(image, source_label, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)


def visual_detect_2(camera_id : int, console : VisualConsole):
    global COORDINATE_HISTORY, LAST_AVG_TIME, DETECTED, AXIS_X, AXIS_Y, ROT, CURRENT_BRIGHTNESS
    global priority_lock, priority_lock_time, DEBUG_MODE, ZOOM_WINDOW_VISIBLE, last_zoomed_frame

    try:
        # 初始化日志
        #logger.info("程序启动")
        #logger.info(f"NumPy版本: {np.__version__}")
        #logger.info(f"OpenCV版本: {cv2.__version__}")
        #logger.info(f"使用GPU加速: {CUDA_AVAILABLE}")

        #print("NumPy版本:", np.__version__)
        #print("OpenCV版本:", cv2.__version__)
        console.add_message("program start")

        # 初始化摄像头
        try:
            cap = cv2.VideoCapture(camera_id)
            if not cap.isOpened():
                raise RuntimeError("无法打开摄像头")
        except Exception as e:
            #logger.error(f"摄像头初始化失败: {str(e)}")
            console.add_message(f"camera init failed: {str(e)}")
            return

        # 初始化界面
        #print("多物体检测程序启动（中心坐标系）...")
        #print(f"使用GPU加速: {CUDA_AVAILABLE}")
        #print("按键说明:")
        #print("  s - 保存检测到的方形")
        #print("  c - 切换轮廓显示")
        #print("  a - 切换自动保存模式")
        #print("  g - 切换坐标网格")
        #print("  t - 切换处理图像显示")
        #print("  d - 切换调试模式")
        #print("  z - 切换放大窗口")
        #print("  l - 分析最后一帧放大区域")
        #print("  q - 退出程序")

        # 初始化状态
        show_contours = True
        auto_save = False
        grid_enabled = True
        brightness_adjustment = True
        show_processed = False
        last_save_time = time.time()

        # 创建输出目录
        try:
            output_dir = "detected_squares"
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            #logger.error(f"创建输出目录失败: {str(e)}")
            console.add_message(f"create output dir failed: {str(e)}")
            output_dir = "."

        # 创建窗口
        '''
        try:
            cv2.namedWindow("Multi-Square Detector", cv2.WINDOW_NORMAL)
            if ZOOM_WINDOW_VISIBLE:
                cv2.namedWindow(ZOOM_WINDOW_NAME, cv2.WINDOW_NORMAL)
        except Exception as e:
            #logger.error(f"创建窗口失败: {str(e)}")
            return
        '''

        # 初始化网格层
        try:
            ret, first_frame = cap.read()
            if not ret:
                raise RuntimeError("无法获取第一帧")
            grid_layer = create_centered_coordinate_grid(first_frame.shape[1], first_frame.shape[0])
        except Exception as e:
            #logger.error(f"初始化网格层失败: {str(e)}")
            console.add_message(f"init grid layer failed: {str(e)}")
            grid_layer = None

        # 初始化线程池
        executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

        # 性能统计
        fps = 0
        frame_count = 0
        start_time = time.time()

        # 历史数据
        last_valid_qr = None
        last_valid_square = None
        current_zoom_rect = None

        while True:
            global LOOP_FLAG
            if not LOOP_FLAG:
                break

            try:
                # 读取帧
                ret, frame = cap.read()
                if not ret:
                    #logger.warning("无法获取帧")
                    console.add_message("无法获取帧")
                    break

                current_time = time.time()

                # 转换为3通道图像（如果是灰度图）
                try:
                    if len(frame.shape) == 2:
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                except Exception as e:
                    #logger.error(f"图像转换失败: {str(e)}")
                    continue

                orig = frame.copy()

                # 并行处理任务
                try:
                    with ThreadPoolExecutor(max_workers=3) as executor:
                        squares_future = executor.submit(find_squares_optimized, frame.copy())
                        qr_future = executor.submit(detect_and_decode_qrcode, frame.copy())
                        tilted_qr_future = executor.submit(detect_tilted_qrcode, frame.copy())

                        try:
                            squares = squares_future.result(timeout=1.0)
                            qr_results = qr_future.result(timeout=1.0)
                            tilted_qr_results = tilted_qr_future.result(timeout=1.0)
                        except Exception as e:
                            #logger.error(f"并行处理超时: {str(e)}")
                            console.add_message(f"parallel processing timeout: {str(e)}")
                            continue
                except Exception as e:
                    #logger.error(f"并行处理失败: {str(e)}")
                    console.add_message(f"parallel processing failed: {str(e)}")
                    continue

                # 边缘检测用于寻找放大区域
                try:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                    edges = cv2.Canny(blurred, 50, 150)
                    all_contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                except Exception as e:
                    #logger.error(f"边缘检测失败: {str(e)}")
                    console.add_message(f"edge detection failed: {str(e)}")
                    all_contours = []

                # 合并并排序QR码结果
                all_qr_results = []
                try:
                    if qr_results is not None:
                        all_qr_results.extend(qr_results)
                    if tilted_qr_results is not None:
                        all_qr_results.extend(tilted_qr_results)

                    all_qr_results.sort(key=lambda x: x.get("id", 0), reverse=True)
                except Exception as e:
                    #logger.error(f"QR码结果合并失败: {str(e)}")
                    console.add_message(f"merge qr results failed: {str(e)}")
                    all_qr_results = []

                # 寻找放大区域
                current_zoom_rect = None
                if ZOOM_ENABLED and not all_qr_results:
                    try:
                        current_zoom_rect = find_zoom_area(all_contours, qr_detected=bool(all_qr_results))

                        if current_zoom_rect is not None:
                            try:
                                zoom_qr_results = zoom_and_search(frame, current_zoom_rect)
                                if zoom_qr_results:
                                    all_qr_results.extend(zoom_qr_results)
                                    all_qr_results.sort(key=lambda x: x.get("id", 0), reverse=True)
                                    current_zoom_rect = None
                            except Exception as e:
                                #logger.error(f"放大区域搜索失败: {str(e)}")
                                console.add_message(f"zoom area search failed: {str(e)}")
                    except Exception as e:
                        #logger.error(f"寻找放大区域失败: {str(e)}")
                        console.add_message(f"find zoom area failed: {str(e)}")

                # 合并接近的方形
                try:
                    merged_squares = merge_close_squares(squares) if squares else []
                except Exception as e:
                    #logger.error(f"合并方形失败: {str(e)}")
                    console.add_message(f"merge squares failed: {str(e)}")
                    merged_squares = []

                # 确定显示内容
                display_squares = []
                display_qr = None
                DETECTED = False

                try:
                    if all_qr_results:
                        current_max_id_qr = all_qr_results[0]
                        # 读取最大的qr码值
                        current_qr_id = current_max_id_qr.get("id", 0)

                        # 确保包含多边形数据
                        if "polygon" not in current_max_id_qr:
                            try:
                                x, y, w, h = current_max_id_qr.get("position", (0, 0, 10, 10))
                                current_max_id_qr["polygon"] = np.array([
                                    [x, y],
                                    [x + w, y],
                                    [x + w, y + h],
                                    [x, y + h]
                                ], dtype=np.float32)
                            except Exception as e:
                                #logger.error(f"创建多边形失败: {str(e)}")
                                continue

                        # 更新优先级锁定
                        update_priority_lock(current_qr_id, current_time)

                        # 检查是否保持锁定
                        if should_keep_priority_lock(current_time) and priority_lock != current_qr_id:
                            if last_valid_qr is not None:
                                display_qr = last_valid_qr.get("polygon")
                                if display_qr is not None:
                                    center, AXIS_X, AXIS_Y, _, ROT = calculate_qr_position(
                                        display_qr, frame.shape[1], frame.shape[0])
                                    DETECTED = True
                        else:
                            qr_polygon = current_max_id_qr["polygon"]
                            qr_center = np.mean(qr_polygon, axis=0)

                            # 查找包含QR码中心的矩形
                            qr_containing = [
                                s for s in merged_squares
                                if cv2.pointPolygonTest(s.astype(np.float32), tuple(qr_center), False) >= 0
                            ]

                            if qr_containing:
                                display_squares = [max(qr_containing, key=cv2.contourArea)]
                                center, AXIS_X, AXIS_Y, _, ROT = calculate_object_position(
                                    display_squares[0], frame.shape[1], frame.shape[0])
                                DETECTED = True
                                last_valid_square = display_squares[0]
                                last_valid_qr = current_max_id_qr
                            else:
                                display_qr = qr_polygon
                                center, AXIS_X, AXIS_Y, _, ROT = calculate_qr_position(
                                    display_qr, frame.shape[1], frame.shape[0])
                                DETECTED = True
                                last_valid_qr = current_max_id_qr
                                last_valid_square = None
                    elif last_valid_qr is not None and should_keep_priority_lock(current_time):
                        display_qr = last_valid_qr.get("polygon")
                        if display_qr is not None:
                            center, AXIS_X, AXIS_Y, _, ROT = calculate_qr_position(
                                display_qr, frame.shape[1], frame.shape[0])
                            DETECTED = True
                except Exception as e:
                    #logger.error(f"确定显示内容失败: {str(e)}")
                    console.add_message(f"determine display content failed: {str(e)}")

                # 亮度调整
                if brightness_adjustment and all_qr_results:
                    try:
                        frame = update_brightness(frame, all_qr_results)
                    except Exception as e:
                        #logger.error(f"亮度调整失败: {str(e)}")
                        console.add_message(f"brightness adjustment failed: {str(e)}")

                # 创建显示图像
                display = frame.copy()

                # 添加网格层
                if grid_enabled and grid_layer is not None:
                    try:
                        display = cv2.addWeighted(display, 1 - GRID_ALPHA, grid_layer, GRID_ALPHA, 0)
                    except Exception as e:
                        #logger.error(f"添加网格层失败: {str(e)}")
                        console.add_message(f"add grid layer failed: {str(e)}")

                # 绘制检测结果
                try:
                    # 绘制QR码
                    for qr in all_qr_results:
                        try:
                            if "rect" in qr:  # 倾斜QR码
                                cv2.polylines(display, [qr["rect"].astype(int)], True, DEBUG_COLORS['tilted_qr'], 2)
                            else:  # 标准QR码
                                x, y, w, h = qr.get("position", (0, 0, 10, 10))
                                cv2.rectangle(display, (x, y), (x + w, y + h), DEBUG_COLORS['standard_qr'], 2)

                            # 绘制多边形顶点
                            if "polygon" in qr:
                                for point in qr["polygon"]:
                                    cv2.circle(display, tuple(point.astype(int)), 5, (0, 0, 255), -1)
                        except Exception as e:
                            #logger.error(f"绘制QR码失败: {str(e)}")
                            console.add_message(f"draw qr failed: {str(e)}")

                    # 绘制方形
                    if show_contours and display_squares:
                        for square in display_squares:
                            try:
                                if square is not None and len(square) >= 4:
                                    cv2.drawContours(display, [square.astype(int)], -1, DEBUG_COLORS['square'], 2)
                                    for point in square:
                                        cv2.circle(display, tuple(point.astype(int)), 6, DEBUG_COLORS['square'], -1)

                                    center, mm_x, mm_y, mm_z, rotation = calculate_object_position(
                                        square, frame.shape[1], frame.shape[2])

                                    # 显示坐标信息
                                    info_x = int(center[0] - 100)
                                    info_y = int(center[1] + 80)
                                    cv2.rectangle(display, (info_x - 5, info_y - 50),
                                                  (info_x + 220, info_y + 30), (40, 40, 40), -1)

                                    cv2.putText(display, f"X: {mm_x:.1f}mm", (info_x, info_y - 20),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                                    cv2.putText(display, f"Y: {mm_y:.1f}mm", (info_x, info_y),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 100, 255), 1)
                                    cv2.putText(display, f"Rot: {rotation:.1f}°", (info_x, info_y + 20),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)
                            except Exception as e:
                                #logger.error(f"绘制方形失败: {str(e)}")
                                console.add_message(f"draw square failed: {str(e)}")

                    # 绘制放大区域
                    if current_zoom_rect is not None:
                        try:
                            cv2.drawContours(display, [current_zoom_rect], 0, ZOOM_SEARCH_COLOR, 2)
                            cv2.putText(display, "ZOOM AREA", tuple(current_zoom_rect[0]),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, ZOOM_SEARCH_COLOR, 2)
                        except Exception as e:
                            #logger.error(f"绘制放大区域失败: {str(e)}")
                            pass
                except Exception as e:
                    #logger.error(f"绘制结果失败: {str(e)}")
                    pass

                # 显示放大窗口
                if ZOOM_WINDOW_VISIBLE:
                    try:
                        show_zoomed_window(frame, current_zoom_rect)
                    except Exception as e:
                        #logger.error(f"显示放大窗口失败: {str(e)}")
                        pass

                # 更新坐标历史
                info = update_coordinate_history(console)
                if info is not None:
                    info['qr_id'] = current_qr_id
                    console.add_message(f'QR id: {current_qr_id}')
                    console.master.add_task(Message(MsgType.VISUAL_MODE, info))

                # 显示主窗口
                try:
                    #cv2.imshow("Multi-Square Detector", display)
                    console.set_image(display)
                except Exception as e:
                    #logger.error(f"显示窗口失败: {str(e)}")
                    break

                # 计算FPS
                frame_count += 1
                if frame_count >= 10:
                    fps = frame_count / (time.time() - start_time)
                    frame_count = 0
                    start_time = time.time()
                    #logger.info(f"FPS: {fps:.1f}")

                # 按键处理
                '''
                try:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s') and display_squares:
                        try:
                            save_squares(orig, display_squares, output_dir)
                            logger.info(f"保存 {len(display_squares)} 个方形")
                        except Exception as e:
                            logger.error(f"保存失败: {str(e)}")
                    elif key == ord('c'):
                        show_contours = not show_contours
                    elif key == ord('a'):
                        auto_save = not auto_save
                    elif key == ord('g'):
                        grid_enabled = not grid_enabled
                    elif key == ord('t'):
                        show_processed = not show_processed
                    elif key == ord('d'):
                        DEBUG_MODE = not DEBUG_MODE
                    elif key == ord('z'):
                        ZOOM_WINDOW_VISIBLE = not ZOOM_WINDOW_VISIBLE
                        if ZOOM_WINDOW_VISIBLE:
                            cv2.namedWindow(ZOOM_WINDOW_NAME, cv2.WINDOW_NORMAL)
                        else:
                            cv2.destroyWindow(ZOOM_WINDOW_NAME)
                    elif key == ord('l'):
                        try:
                            zoom_results = analyze_last_zoomed_frame()
                            if zoom_results:
                                logger.info(f"在放大区域发现 {len(zoom_results)} 个QR码")
                        except Exception as e:
                            logger.error(f"分析放大区域失败: {str(e)}")
                except Exception as e:
                    logger.error(f"按键处理失败: {str(e)}")
            '''

            except Exception as e:
                #logger.error(f"主循环错误: {str(e)}")
                continue

    except Exception as e:
        #logger.critical(f"程序发生严重错误: {str(e)}", exc_info=True)
        console.add_message(f"程序发生严重错误: {str(e)}")
    finally:
        # 清理资源
        try:
            executor.shutdown()
            cap.release()
            cv2.destroyAllWindows()
            #logger.info("程序正常退出")
            console.add_message("program exited")
        except Exception as e:
            #logger.error(f"资源清理失败: {str(e)}")
            console.add_message(f"资源清理失败: {str(e)}")


if __name__ == "__main__":
    #main()
    pass