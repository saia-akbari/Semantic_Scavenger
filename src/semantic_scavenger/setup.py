from setuptools import setup

package_name = 'semantic_scavenger'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='akbaris',
    maintainer_email='akbaris@ufl.edu',
    description='VLA Bridge for Semantic Scavenger',
    license='MIT',
    entry_points={
        'console_scripts': [
            'vla_bridge = semantic_scavenger.vla_bridge:main',
	    'robot_controller = semantic_scavenger.robot_controller:main',
        ],
    },
)
