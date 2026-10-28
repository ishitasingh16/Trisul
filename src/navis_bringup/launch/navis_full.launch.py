import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    bringup_share = get_package_share_directory('navis_bringup')
    perception_share = get_package_share_directory('navis_perception')
    world_model_share = get_package_share_directory('navis_world_model')

    sim_launch = os.path.join(bringup_share, 'launch', 'navis_sim.launch.py')
    perception_launch = os.path.join(perception_share, 'launch', 'perception.launch.py')
    world_model_launch = os.path.join(world_model_share, 'launch', 'world_model.launch.py')

    metrics_node = Node(
        package='navis_bringup',
        executable='metrics_collector',
        name='metrics_collector_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(sim_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(perception_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(world_model_launch)),
        metrics_node,
    ])
