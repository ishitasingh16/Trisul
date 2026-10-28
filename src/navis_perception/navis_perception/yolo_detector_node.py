import time
from typing import List
from dataclasses import dataclass, field
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import Header
from cv_bridge import CvBridge
from ultralytics import YOLO

from navis_perception.image_processor import ImageProcessor

try:
    from navis_msgs.msg import Detection as RosDetection
    from navis_msgs.msg import DetectionArray as RosDetectionArray
    HAS_NAVIS_MSGS = True
except ImportError:
    HAS_NAVIS_MSGS = False

    @dataclass
    class RosDetection:
        class_name: str = ""
        confidence: float = 0.0
        bbox: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
        center: List[float] = field(default_factory=lambda: [0.0, 0.0])

    @dataclass
    class RosDetectionArray:
        header: Header = field(default_factory=Header)
        detections: List[RosDetection] = field(default_factory=list)
        inference_time_ms: float = 0.0


class YoloDetectorNode(Node):

    def __init__(self):
        super().__init__('yolo_detector_node')

        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('device', 'cpu')
        self.declare_parameter('input_size', 640)
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('detections_topic', '/detections')
        self.declare_parameter('annotated_image_topic', '/detections/image')

        self.model_path = self.get_parameter('model_path').get_parameter_value().string_value
        self.conf_threshold = self.get_parameter('confidence_threshold').get_parameter_value().double_value
        self.device = self.get_parameter('device').get_parameter_value().string_value
        self.input_size = self.get_parameter('input_size').get_parameter_value().integer_value
        self.image_topic = self.get_parameter('image_topic').get_parameter_value().string_value
        self.detections_topic = self.get_parameter('detections_topic').get_parameter_value().string_value
        self.annotated_image_topic = self.get_parameter('annotated_image_topic').get_parameter_value().string_value

        self.bridge = CvBridge()
        self.processor = ImageProcessor()
        self.model = YOLO(self.model_path)

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.sub_image = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            sensor_qos
        )

        self.annotated_pub = self.create_publisher(Image, self.annotated_image_topic, 1)

        if HAS_NAVIS_MSGS:
            self.detections_pub = self.create_publisher(RosDetectionArray, self.detections_topic, 10)
        else:
            self.detections_pub = None
            self.get_logger().warn('navis_msgs not available; detections topic will not publish ROS messages until navis_msgs is built.')

    def image_callback(self, msg: Image):
        start_time = time.perf_counter()
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            device=self.device,
            imgsz=self.input_size,
            verbose=False
        )

        inference_time_ms = (time.perf_counter() - start_time) * 1000.0

        detections_list = []
        if results and len(results) > 0:
            boxes = results[0].boxes
            if boxes is not None:
                for box in boxes:
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[cls_id]

                    det = RosDetection()
                    det.class_name = class_name
                    det.confidence = conf
                    det.bbox = [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])]
                    center_x = float((xyxy[0] + xyxy[2]) / 2.0)
                    center_y = float((xyxy[1] + xyxy[3]) / 2.0)
                    det.center = [center_x, center_y]
                    detections_list.append(det)

        if self.detections_pub is not None:
            array_msg = RosDetectionArray()
            array_msg.header = msg.header
            array_msg.detections = detections_list
            array_msg.inference_time_ms = float(inference_time_ms)
            self.detections_pub.publish(array_msg)

        if self.annotated_pub.get_subscription_count() > 0:
            annotated_frame = self.processor.annotate(frame, detections_list)
            out_msg = self.bridge.cv2_to_imgmsg(annotated_frame, encoding='bgr8')
            out_msg.header = msg.header
            self.annotated_pub.publish(out_msg)


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
