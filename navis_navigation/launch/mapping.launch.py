from pathlib import Path

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    navigation_dir = Path(get_package_share_directory('navis_navigation'))
    slam_params = str(navigation_dir / 'config' / 'slam_params.yaml')
    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[slam_params, {'use_sim_time': True}],
        ),
    ])