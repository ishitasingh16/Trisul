from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    server_node = Node(
        package='navis_dashboard',
        executable='dashboard_server',
        name='dashboard_server',
        output='screen',
        parameters=[{'port': 8080}],
    )

    rosbridge_node = Node(
        package='rosbridge_server',
        executable='rosbridge_websocket',
        name='rosbridge_websocket',
        output='screen',
        parameters=[{'port': 9090}],
    )

    return LaunchDescription([
        server_node,
        rosbridge_node,
    ])
