import time
import math
from typing import Optional, List
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseWithCovarianceStamped, PointStamped, Point
import tf2_ros

try:
    from tf2_geometry_msgs import do_transform_point
except ImportError:
    do_transform_point = None

try:
    from navis_msgs.msg import WorldObject as RosWorldObject
    from navis_msgs.msg import WorldObjectArray as RosWorldObjectArray
    from navis_msgs.msg import MissionStatus as RosMissionStatus
    from navis_msgs.msg import DetectionArray
    HAS_NAVIS_MSGS = True
except ImportError:
    HAS_NAVIS_MSGS = False

from navis_world_model.object_tracker import ObjectTracker
from navis_world_model.semantic_layer import SemanticLayer
from navis_perception.depth_estimator import DepthEstimator


class WorldModelNode(Node):

    def __init__(self):
        super().__init__('world_model_node')

        self.declare_parameter('association_radius', 0.5)
        self.declare_parameter('stale_timeout_sec', 30.0)
        self.declare_parameter('camera_fov_rad', 1.04719755)
        self.declare_parameter('image_width', 640)
        self.declare_parameter('angle_margin_rad', 0.087266)
        self.declare_parameter('target_frame', 'map')
        self.declare_parameter('publish_rate_hz', 5.0)

        assoc_radius = self.get_parameter('association_radius').get_parameter_value().double_value
        stale_sec = self.get_parameter('stale_timeout_sec').get_parameter_value().double_value
        fov_rad = self.get_parameter('camera_fov_rad').get_parameter_value().double_value
        img_w = self.get_parameter('image_width').get_parameter_value().integer_value
        self.angle_margin = self.get_parameter('angle_margin_rad').get_parameter_value().double_value
        self.target_frame = self.get_parameter('target_frame').get_parameter_value().string_value
        rate_hz = self.get_parameter('publish_rate_hz').get_parameter_value().double_value

        self.tracker = ObjectTracker(association_radius=assoc_radius, stale_timeout_sec=stale_sec)
        self.depth_estimator = DepthEstimator(camera_fov_rad=fov_rad, image_width=img_w)
        self.semantic_layer = SemanticLayer()

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.latest_scan: Optional[LaserScan] = None
        self.last_pose: Optional[Point] = None
        self.distance_traveled = 0.0
        self.start_time = time.monotonic()
        self.collision_count = 0

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.sub_scan = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            sensor_qos
        )

        self.sub_pose = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.pose_callback,
            10
        )

        self.sub_map = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )

        if HAS_NAVIS_MSGS:
            self.sub_detections = self.create_subscription(
                DetectionArray,
                '/detections',
                self.detections_callback,
                10
            )
            self.pub_objects = self.create_publisher(RosWorldObjectArray, '/world_model/objects', 10)
            self.pub_status = self.create_publisher(RosMissionStatus, '/world_model/status', 10)
        else:
            self.pub_objects = None
            self.pub_status = None

        self.timer = self.create_timer(1.0 / rate_hz, self.timer_callback)

    def scan_callback(self, msg: LaserScan):
        self.latest_scan = msg

    def map_callback(self, msg: OccupancyGrid):
        pass

    def pose_callback(self, msg: PoseWithCovarianceStamped):
        curr_pt = msg.pose.pose.position
        if self.last_pose is not None:
            step = math.hypot(curr_pt.x - self.last_pose.x, curr_pt.y - self.last_pose.y)
            self.distance_traveled += step
        self.last_pose = curr_pt

    def detections_callback(self, msg):
        if self.latest_scan is None:
            return

        now_sec = time.monotonic()
        scan_ranges = np.array(self.latest_scan.ranges, dtype=np.float32)

        for det in msg.detections:
            center_x = det.center[0]
            target_angle = self.depth_estimator.bbox_to_angle(center_x)

            dist = self.depth_estimator.estimate_distance(
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

            x_sensor, y_sensor = self.depth_estimator.polar_to_cartesian(dist, target_angle)
            map_pt = self.transform_point(x_sensor, y_sensor, self.latest_scan.header.frame_id, self.target_frame)

            if map_pt is not None:
                self.tracker.update_or_add(
                    class_name=det.class_name,
                    x=map_pt.x,
                    y=map_pt.y,
                    z=map_pt.z,
                    confidence=det.confidence,
                    current_time=now_sec
                )

    def transform_point(self, x: float, y: float, source_frame: str, target_frame: str) -> Optional[Point]:
        pt = PointStamped()
        pt.header.frame_id = source_frame
        pt.header.stamp = self.get_clock().now().to_msg()
        pt.point.x = x
        pt.point.y = y
        pt.point.z = 0.0

        try:
            if not self.tf_buffer.can_transform(target_frame, source_frame, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=0.02)):
                return None
            trans = self.tf_buffer.lookup_transform(target_frame, source_frame, rclpy.time.Time())
            if do_transform_point is not None:
                return do_transform_point(pt, trans).point
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
            return None
        return None

    def timer_callback(self):
        now_sec = time.monotonic()
        self.tracker.prune_stale(now_sec)
        active_objects = self.tracker.get_objects()

        if self.pub_objects is not None:
            obj_array_msg = RosWorldObjectArray()
            obj_array_msg.header.stamp = self.get_clock().now().to_msg()
            obj_array_msg.header.frame_id = self.target_frame

            for obj in active_objects:
                msg_obj = RosWorldObject()
                msg_obj.id = int(obj.id)
                msg_obj.class_name = obj.class_name
                msg_obj.position.x = float(obj.x)
                msg_obj.position.y = float(obj.y)
                msg_obj.position.z = float(obj.z)
                msg_obj.confidence = float(obj.confidence)
                msg_obj.is_dynamic = bool(obj.is_dynamic)
                obj_array_msg.objects.append(msg_obj)

            self.pub_objects.publish(obj_array_msg)

        if self.pub_status is not None:
            status_msg = RosMissionStatus()
            status_msg.state = "ACTIVE"
            status_msg.elapsed_time = float(now_sec - self.start_time)
            status_msg.distance_traveled = float(self.distance_traveled)
            status_msg.objects_detected = len(active_objects)
            status_msg.collision_count = int(self.collision_count)
            self.pub_status.publish(status_msg)


def main(args=None):
    rclpy.init(args=args)
    node = WorldModelNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
