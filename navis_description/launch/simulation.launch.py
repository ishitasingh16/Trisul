from pathlib import Path

from launch import LaunchDescription
from launch_ros.actions import Node
from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.webots_launcher import WebotsLauncher


def generate_launch_description():
    package_dir = Path(__file__).resolve().parents[1]
    world = package_dir / 'worlds' / 'warehouse_simple.wbt'
    urdf = package_dir / 'urdf' / 'navis_robot.urdf'
    robot_description = urdf.read_text(encoding='utf-8')

    webots = WebotsLauncher(
        world=str(world),
        mode='realtime',
        ros2_supervisor=True,
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True},
        ],
    )

    controller = WebotsController(
        robot_name='navis_robot',
        parameters=[
            {'robot_description': str(urdf)},
            {'use_sim_time': True},
        ],
        respawn=True,
    )

    return LaunchDescription([
        webots,
        robot_state_publisher,
        controller,
    ])
