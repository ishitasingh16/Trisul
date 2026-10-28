import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('navis_control')
    params_file = os.path.join(pkg_share, 'config', 'control_params.yaml')

    params_arg = DeclareLaunchArgument(
        'params_file',
        default_value=params_file,
    )

    pid_node = Node(
        package='navis_control',
        executable='pid_controller',
        name='pid_controller_node',
        output='screen',
        parameters=[LaunchConfiguration('params_file')],
    )

    return LaunchDescription([
        params_arg,
        pid_node,
    ])
