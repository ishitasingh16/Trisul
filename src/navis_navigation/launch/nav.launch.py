import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_share = get_package_share_directory('navis_navigation')
    map_yaml_file = os.path.join(nav_share, 'maps', 'warehouse_simple.yaml')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=map_yaml_file,
    )

    costmap_updater_node = Node(
        package='navis_navigation',
        executable='costmap_updater',
        name='costmap_updater_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    goal_manager_node = Node(
        package='navis_navigation',
        executable='goal_manager',
        name='goal_manager_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        map_arg,
        costmap_updater_node,
        goal_manager_node,
    ])
