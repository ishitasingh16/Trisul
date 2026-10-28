import struct
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header

try:
    from navis_msgs.msg import WorldObjectArray
    HAS_NAVIS_MSGS = True
except ImportError:
    HAS_NAVIS_MSGS = False


class CostmapUpdaterNode(Node):

    def __init__(self):
        super().__init__('costmap_updater_node')

        self.declare_parameter('obstacle_frame', 'map')
        self.frame_id = self.get_parameter('obstacle_frame').get_parameter_value().string_value

        self.pub_cloud = self.create_publisher(PointCloud2, '/world_model/obstacle_cloud', 10)

        if HAS_NAVIS_MSGS:
            self.sub_objects = self.create_subscription(
                WorldObjectArray,
                '/world_model/objects',
                self.objects_callback,
                10
            )

    def objects_callback(self, msg):
        if not msg.objects:
            return

        points_bytes = bytearray()
        point_count = 0

        for obj in msg.objects:
            ox = obj.position.x
            oy = obj.position.y
            oz = obj.position.z

            for dx in (-0.15, 0.0, 0.15):
                for dy in (-0.15, 0.0, 0.15):
                    points_bytes.extend(struct.pack('fff', ox + dx, oy + dy, oz))
                    point_count += 1

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]

        cloud = PointCloud2()
        cloud.header = Header(stamp=self.get_clock().now().to_msg(), frame_id=self.frame_id)
        cloud.height = 1
        cloud.width = point_count
        cloud.fields = fields
        cloud.is_bigendian = False
        cloud.point_step = 12
        cloud.row_step = 12 * point_count
        cloud.data = bytes(points_bytes)
        cloud.is_dense = True

        self.pub_cloud.publish(cloud)


def main(args=None):
    rclpy.init(args=args)
    node = CostmapUpdaterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
