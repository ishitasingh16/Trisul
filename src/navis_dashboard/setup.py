from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'navis_dashboard'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'www'), glob('www/*.*')),
        (os.path.join('share', package_name, 'www', 'css'), glob('www/css/*.*')),
        (os.path.join('share', package_name, 'www', 'js'), glob('www/js/*.*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='NAVIS Team',
    maintainer_email='navis@trishul.local',
    description='Real-time web telemetry and mission control dashboard for NAVIS',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dashboard_server = navis_dashboard.server:main',
        ],
    },
)
