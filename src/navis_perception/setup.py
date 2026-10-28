from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'navis_perception'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='NAVIS Team',
    maintainer_email='navis@trishul.local',
    description='AI Perception package for NAVIS warehouse robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'yolo_detector_node = navis_perception.yolo_detector_node:main',
            'depth_estimator = navis_perception.depth_estimator:main',
        ],
    },
)
