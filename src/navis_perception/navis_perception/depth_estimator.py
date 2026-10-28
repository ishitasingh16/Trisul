import math
from typing import Optional, Tuple, List
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PointStamped, Point
import tf2_ros

try:
    from tf2_geometry_msgs import do_transform_point
except ImportError:
    do_transform_point = None

try:
    from navis_msgs.msg import DetectionArray
    HAS_NAVIS_MSGS = True
except ImportError:
    HAS_NAVIS_MSGS = False


class DepthEstimator:

    def __init__(self, camera_fov_rad: float = 1.04719755, image_width: int = 640):
        self.camera_fov_rad = camera_fov_rad
        self.image_width = image_width

    def bbox_to_angle(self, bbox_center_x: float) -> float:
        norm_x = (bbox_center_x - (self.image_width / 2.0)) / self.image_width
        return -norm_x * self.camera_fov_rad

    def estimate_distance(
        self,
        target_angle: float,
        angle_margin: float,
        scan_ranges: np.ndarray,
        angle_min: float,
        angle_increment: float,
        range_min: float,
        range_max: float,
    ) -> Optional[float]:
        total_angles = scan_ranges.shape[0]
        if total_angles == 0 or angle_increment <= 0.0:
            return None

        angles = angle_min + np.arange(total_angles, dtype=np.float32) * angle_increment
        angular_diff = np.abs(np.arctan2(np.sin(angles - target_angle), np.cos(angles - target_angle)))
        valid_mask = (angular_diff <= angle_margin) & np.isfinite(scan_ranges) & (scan_ranges >= range_min) & (scan_ranges <= range_max)

        valid_ranges = scan_ranges[valid_mask]
        if valid_ranges.size == 0:
            return None

        return float(np.percentile(valid_ranges, 25))

    def polar_to_cartesian(self, distance: float, angle: float) -> Tuple[float, float]:
        return distance * math.cos(angle), distance * math.sin(angle)


class DepthEstimationNode(Node):

    def __init__(self):
        super().__init__('depth_estimation_node')

        self.declare_parameter('camera_fov_rad', 1.04719755)
        self.declare_parameter('image_width', 640)
        self.declare_parameter('angle_margin_rad', 0.087266)
        self.declare_parameter('target_frame', 'map')
        self.declare_parameter('robot_frame', 'base_link')

        camera_fov = self.get_parameter('camera_fov_rad').get_parameter_value().double_value
        image_width = self.get_parameter('image_width').get_parameter_value().integer_value
        self.angle_margin = self.get_parameter('angle_margin_rad').get_parameter_value().double_value
        self.target_frame = self.get_parameter('target_frame').get_parameter_value().string_value
        self.robot_frame = self.get_parameter('robot_frame').get_parameter_value().string_value

        self.estimator = DepthEstimator(camera_fov_rad=camera_fov, image_width=image_width)
        self.latest_scan: Optional[LaserScan] = None

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            sensor_qos
        )

        if HAS_NAVIS_MSGS:
            self.det_sub = self.create_subscription(
                DetectionArray,
                '/detections',
                self.detections_callback,
                10
            )

    def scan_callback(self, msg: LaserScan):
        self.latest_scan = msg

    def detections_callback(self, msg):
        if self.latest_scan is None:
            return

        scan_ranges = np.array(self.latest_scan.ranges, dtype=np.float32)

        for det in msg.detections:
            center_x = det.center[0]
            target_angle = self.estimator.bbox_to_angle(center_x)

            dist = self.estimator.estimate_distance(
                target_angle=target_angle,
                angle_margin=self.angle_margin,
                scan_ranges=scan_ranges,
                angle_min=self.latest_scan.angle_min,
                angle_increment=self.latest_scan.angle_increment,
                range_min=self.latest_scan.range_min,
                range_max=self.latest_scan.range_max,
            )

            if dist is None:
                continue

            x_sensor, y_sensor = self.estimator.polar_to_cartesian(dist, target_angle)
            map_pt = self.transform_point(x_sensor, y_sensor, self.latest_scan.header.frame_id, self.target_frame)

    def transform_point(self, x: float, y: float, source_frame: str, target_frame: str) -> Optional[Point]:
        pt = PointStamped()
        pt.header.frame_id = source_frame
        pt.header.stamp = self.get_clock().now().to_msg()
        pt.point.x = x
        pt.point.y = y
        pt.point.z = 0.0

        try:
            if not self.tf_buffer.can_transform(target_frame, source_frame, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=0.05)):
                return None
            trans = self.tf_buffer.lookup_transform(target_frame, source_frame, rclpy.time.Time())
            if do_transform_point is not None:
                transformed = do_transform_point(pt, trans)
                return transformed.point
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
            return None
        return None


def main(args=None):
    rclpy.init(args=args)
    node = DepthEstimationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
