from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'navis_training'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'data'), glob('data/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='NAVIS Team',
    maintainer_email='navis@trishul.local',
    description='Offline dataset generation and YOLO training pipeline for NAVIS',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'generate_dataset = navis_training.generate_dataset:main',
            'train_yolo = navis_training.train_yolo:main',
            'validate_model = navis_training.validate_model:main',
            'export_model = navis_training.export_model:main',
        ],
    },
)
