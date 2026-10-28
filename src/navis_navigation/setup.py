from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'navis_navigation'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*.*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='NAVIS Team',
    maintainer_email='navis@trishul.local',
    description='Navigation logic, goal manager, and costmap updater for NAVIS',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'goal_manager = navis_navigation.goal_manager_node:main',
            'costmap_updater = navis_navigation.costmap_updater_node:main',
        ],
    },
)
