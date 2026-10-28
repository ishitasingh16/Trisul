import math
from typing import Optional
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from std_msgs.msg import String


class GoalManagerNode(Node):

    def __init__(self):
        super().__init__('goal_manager_node')

        self.declare_parameter('tolerance_m', 0.3)
        self.tolerance = self.get_parameter('tolerance_m').get_parameter_value().double_value

        self.active_goal: Optional[PoseStamped] = None
        self.current_pose: Optional[tuple] = None

        self.sub_goal = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_callback,
            10
        )

        self.sub_amcl = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_callback,
            10
        )

        self.pub_status = self.create_publisher(String, '/navigation/goal_status', 10)
        self.timer = self.create_timer(0.2, self.check_goal_progress)

    def goal_callback(self, msg: PoseStamped):
        self.active_goal = msg
        status_msg = String()
        status_msg.data = f"NEW_GOAL: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})"
        self.pub_status.publish(status_msg)

    def amcl_callback(self, msg: PoseWithCovarianceStamped):
        pos = msg.pose.pose.position
        self.current_pose = (pos.x, pos.y)

    def check_goal_progress(self):
        if self.active_goal is None or self.current_pose is None:
            return

        target_x = self.active_goal.pose.position.x
        target_y = self.active_goal.pose.position.y
        dist = math.hypot(target_x - self.current_pose[0], target_y - self.current_pose[1])

        if dist <= self.tolerance:
            status_msg = String()
            status_msg.data = f"SUCCEEDED: ({target_x:.2f}, {target_y:.2f})"
            self.pub_status.publish(status_msg)
            self.active_goal = None


def main(args=None):
    rclpy.init(args=args)
    node = GoalManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
