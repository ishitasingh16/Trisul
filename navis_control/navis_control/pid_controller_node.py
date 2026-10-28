import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Path
from rclpy.node import Node


class PidControllerNode(Node):
    """Follow the nearest path point with bounded linear/angular PID output."""

    def __init__(self):
        super().__init__('pid_controller')
        self.declare_parameter('linear_kp', 0.8)
        self.declare_parameter('linear_ki', 0.0)
        self.declare_parameter('linear_kd', 0.08)
        self.declare_parameter('angular_kp', 2.2)
        self.declare_parameter('angular_ki', 0.0)
        self.declare_parameter('angular_kd', 0.15)
        self.declare_parameter('max_linear_velocity', 0.35)
        self.declare_parameter('max_angular_velocity', 1.2)
        self.declare_parameter('goal_tolerance', 0.15)
        self.declare_parameter('control_rate', 20.0)

        self.path = None
        self.linear_integral = 0.0
        self.angular_integral = 0.0
        self.previous_linear_error = 0.0
        self.previous_angular_error = 0.0
        self.last_time = self.get_clock().now()

        self.create_subscription(Path, '/plan', self.path_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        rate = float(self.get_parameter('control_rate').value)
        self.create_timer(1.0 / rate, self.control_callback)

    def path_callback(self, message):
        self.path = message
        self.linear_integral = 0.0
        self.angular_integral = 0.0

    def control_callback(self):
        if self.path is None or not self.path.poses:
            self.publish_stop()
            return

        target = self.path.poses[0].pose.position
        distance = math.hypot(target.x, target.y)
        heading = math.atan2(target.y, target.x)
        now = self.get_clock().now()
        dt = max((now - self.last_time).nanoseconds / 1e9, 1e-3)
        self.last_time = now

        if distance <= float(self.get_parameter('goal_tolerance').value):
            self.publish_stop()
            self.path = None
            return

        linear_error = distance
        angular_error = math.atan2(math.sin(heading), math.cos(heading))
        self.linear_integral += linear_error * dt
        self.angular_integral += angular_error * dt
        linear_derivative = (linear_error - self.previous_linear_error) / dt
        angular_derivative = (angular_error - self.previous_angular_error) / dt
        self.previous_linear_error = linear_error
        self.previous_angular_error = angular_error

        linear = self.pid('linear', linear_error, self.linear_integral, linear_derivative)
        angular = self.pid('angular', angular_error, self.angular_integral, angular_derivative)
        if abs(angular_error) > math.pi / 4:
            linear *= 0.25

        command = Twist()
        command.linear.x = self.clamp(linear, 0.0, float(self.get_parameter('max_linear_velocity').value))
        command.angular.z = self.clamp(angular, -float(self.get_parameter('max_angular_velocity').value), float(self.get_parameter('max_angular_velocity').value))
        self.cmd_pub.publish(command)

    def pid(self, axis, error, integral, derivative):
        prefix = axis + '_'
        return (
            float(self.get_parameter(prefix + 'kp').value) * error
            + float(self.get_parameter(prefix + 'ki').value) * integral
            + float(self.get_parameter(prefix + 'kd').value) * derivative
        )

    @staticmethod
    def clamp(value, minimum, maximum):
        return max(minimum, min(value, maximum))

    def publish_stop(self):
        self.cmd_pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = PidControllerNode()
    try:
        rclpy.spin(node)
    finally:
        node.publish_stop()
        node.destroy_node()
        rclpy.shutdown()
