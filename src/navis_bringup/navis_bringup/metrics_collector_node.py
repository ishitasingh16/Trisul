import time
import math
import csv
from pathlib import Path
from typing import Optional
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue

try:
    from navis_msgs.msg import DetectionArray, MissionStatus
    HAS_NAVIS_MSGS = True
except ImportError:
    HAS_NAVIS_MSGS = False


class MetricsCollectorNode(Node):

    def __init__(self):
        super().__init__('metrics_collector_node')

        self.declare_parameter('csv_log_path', 'metrics_log.csv')
        self.declare_parameter('publish_rate_hz', 1.0)

        csv_path = self.get_parameter('csv_log_path').get_parameter_value().string_value
        rate_hz = self.get_parameter('publish_rate_hz').get_parameter_value().double_value

        self.start_time = time.monotonic()
        self.total_distance = 0.0
        self.last_position: Optional[tuple] = None
        self.latest_inference_time_ms = 0.0
        self.detection_count = 0
        self.replan_events = 0
        self.collision_count = 0
        self.mission_state = 'IDLE'

        self.csv_file = open(csv_path, mode='w', newline='', buffering=1)
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            'timestamp', 'elapsed_time', 'distance_traveled',
            'inference_time_ms', 'detection_count', 'mission_state'
        ])

        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.sub_cmd_vel = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        if HAS_NAVIS_MSGS:
            self.sub_det = self.create_subscription(DetectionArray, '/detections', self.det_callback, 10)
            self.sub_status = self.create_subscription(MissionStatus, '/world_model/status', self.status_callback, 10)

        self.pub_diagnostics = self.create_publisher(DiagnosticArray, '/diagnostics', 10)
        self.timer = self.create_timer(1.0 / rate_hz, self.timer_callback)

    def odom_callback(self, msg: Odometry):
        px = msg.pose.pose.position.x
        py = msg.pose.pose.position.y
        if self.last_position is not None:
            dist = math.hypot(px - self.last_position[0], py - self.last_position[1])
            self.total_distance += dist
        self.last_position = (px, py)

    def cmd_vel_callback(self, msg: Twist):
        pass

    def det_callback(self, msg):
        self.latest_inference_time_ms = msg.inference_time_ms
        self.detection_count += len(msg.detections)

    def status_callback(self, msg):
        if msg.state == 'REPLANNING' and self.mission_state != 'REPLANNING':
            self.replan_events += 1
        self.mission_state = msg.state
        self.collision_count = msg.collision_count

    def timer_callback(self):
        now_sec = time.monotonic()
        elapsed = now_sec - self.start_time

        self.csv_writer.writerow([
            f"{now_sec:.2f}", f"{elapsed:.2f}", f"{self.total_distance:.3f}",
            f"{self.latest_inference_time_ms:.2f}", self.detection_count, self.mission_state
        ])

        diag_msg = DiagnosticArray()
        diag_msg.header.stamp = self.get_clock().now().to_msg()

        status = DiagnosticStatus()
        status.name = 'NAVIS Mission Metrics'
        status.level = DiagnosticStatus.OK
        status.message = f"State: {self.mission_state}"

        status.values = [
            KeyValue(key='Elapsed Time (s)', value=f"{elapsed:.2f}"),
            KeyValue(key='Total Distance (m)', value=f"{self.total_distance:.2f}"),
            KeyValue(key='Inference Latency (ms)', value=f"{self.latest_inference_time_ms:.2f}"),
            KeyValue(key='Detections Logged', value=str(self.detection_count)),
            KeyValue(key='Replan Events', value=str(self.replan_events)),
            KeyValue(key='Collisions', value=str(self.collision_count)),
        ]

        diag_msg.status.append(status)
        self.pub_diagnostics.publish(diag_msg)

    def destroy_node(self):
        if hasattr(self, 'csv_file') and not self.csv_file.closed:
            self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MetricsCollectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
