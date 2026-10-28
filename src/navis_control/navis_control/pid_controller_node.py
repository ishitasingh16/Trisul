import time
import math
from typing import Optional, List
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import Twist


class PID:

    def __init__(self, kp: float, ki: float, kd: float, min_val: float, max_val: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_val = min_val
        self.max_val = max_val
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time: Optional[float] = None

    def update(self, error: float, now: float) -> float:
        if self.last_time is None:
            self.last_time = now
            self.last_error = error
            return max(self.min_val, min(self.max_val, self.kp * error))

        dt = now - self.last_time
        if dt <= 0.0:
            return max(self.min_val, min(self.max_val, self.kp * error))

        self.integral += error * dt
        derivative = (error - self.last_error) / dt

        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.last_error = error
        self.last_time = now

        return max(self.min_val, min(self.max_val, output))

    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = None


class PidControllerNode(Node):

    def __init__(self):
        super().__init__('pid_controller_node')

        self.declare_parameter('kp_linear', 0.8)
        self.declare_parameter('ki_linear', 0.0)
        self.declare_parameter('kd_linear', 0.05)
        self.declare_parameter('kp_angular', 2.0)
        self.declare_parameter('ki_angular', 0.0)
        self.declare_parameter('kd_angular', 0.1)
        self.declare_parameter('max_linear_vel', 0.5)
        self.declare_parameter('max_angular_vel', 1.0)
        self.declare_parameter('lookahead_dist', 0.4)

        kp_l = self.get_parameter('kp_linear').get_parameter_value().double_value
        ki_l = self.get_parameter('ki_linear').get_parameter_value().double_value
        kd_l = self.get_parameter('kd_linear').get_parameter_value().double_value
        max_l = self.get_parameter('max_linear_vel').get_parameter_value().double_value

        kp_a = self.get_parameter('kp_angular').get_parameter_value().double_value
        ki_a = self.get_parameter('ki_angular').get_parameter_value().double_value
        kd_a = self.get_parameter('kd_angular').get_parameter_value().double_value
        max_a = self.get_parameter('max_angular_vel').get_parameter_value().double_value

        self.lookahead_dist = self.get_parameter('lookahead_dist').get_parameter_value().double_value

        self.linear_pid = PID(kp_l, ki_l, kd_l, 0.0, max_l)
        self.angular_pid = PID(kp_a, ki_a, kd_a, -max_a, max_a)

        self.path_points: List[tuple] = []
        self.robot_pose: Optional[tuple] = None

        self.sub_path = self.create_subscription(Path, '/plan', self.path_callback, 10)
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)

        self.timer = self.create_timer(0.05, self.control_loop)

    def path_callback(self, msg: Path):
        self.path_points = [
            (ps.pose.position.x, ps.pose.position.y)
            for ps in msg.poses
        ]

    def odom_callback(self, msg: Odometry):
        px = msg.pose.pose.position.x
        py = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        self.robot_pose = (px, py, yaw)

    def control_loop(self):
        if not self.path_points or self.robot_pose is None:
            return

        rx, ry, ryaw = self.robot_pose

        target_pt = None
        for pt in self.path_points:
            dist = math.hypot(pt[0] - rx, pt[1] - ry)
            if dist >= self.lookahead_dist:
                target_pt = pt
                break

        if target_pt is None:
            target_pt = self.path_points[-1]

        dist_to_goal = math.hypot(self.path_points[-1][0] - rx, self.path_points[-1][1] - ry)
        if dist_to_goal < 0.15:
            self.stop_robot()
            self.path_points = []
            return

        dx = target_pt[0] - rx
        dy = target_pt[1] - ry
        target_yaw = math.atan2(dy, dx)
        yaw_err = math.atan2(math.sin(target_yaw - ryaw), math.cos(target_yaw - ryaw))

        now = time.monotonic()
        linear_cmd = self.linear_pid.update(dist_to_goal, now)
        angular_cmd = self.angular_pid.update(yaw_err, now)

        if abs(yaw_err) > 0.8:
            linear_cmd = 0.05

        cmd = Twist()
        cmd.linear.x = float(linear_cmd)
        cmd.angular.z = float(angular_cmd)
        self.pub_cmd_vel.publish(cmd)

    def stop_robot(self):
        cmd = Twist()
        self.pub_cmd_vel.publish(cmd)
        self.linear_pid.reset()
        self.angular_pid.reset()


def main(args=None):
    rclpy.init(args=args)
    node = PidControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
