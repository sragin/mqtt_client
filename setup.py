from setuptools import find_packages, setup

package_name = 'mqtt_client'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'paho-mqtt'],
    zip_safe=True,
    maintainer='Jongpil Kim',
    maintainer_email='jpkim@koceti.re.kr',
    description='ROS2 Python MQTT Client for Scop(Hanyang University) via Withpoints broker',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mqtt_scop = mqtt_client.scop_via_withpoints:main',
            'mqtt_client_test = mqtt_client.mqtt_client_node:main',
        ],
    },
)
