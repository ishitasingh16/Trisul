from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    navigation_dir = Path(get_package_share_directory('navis_navigation'))
    params = str(navigation_dir / 'config' / 'nav2_params.yaml')
    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=''),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(Path(get_package_share_directory('nav2_bringup')) / 'launch' / 'navigation_launch.py')
            ),
            launch_arguments={
                'params_file': params,
                'map': LaunchConfiguration('map'),
                'use_sim_time': 'true',
            }.items(),
        ),
    ])
