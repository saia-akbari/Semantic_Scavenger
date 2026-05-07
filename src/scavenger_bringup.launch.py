from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
import os

def generate_launch_description():

    # Launch Gazebo + UR5e with RViz
    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare("ur_simulation_gz"), "launch", "ur_sim_control.launch.py"])
        ]),
        launch_arguments={
            "ur_type": "ur5e",
            "description_file": os.path.expanduser("~/Semantic_Scavenger_ws/src/scavenger_robot.urdf.xacro"),
            "launch_rviz": "true",
        }.items()
    )

    # Camera bridge (delayed 5s to let Gazebo start first)
    bridge = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                arguments=["/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image"],
                output="screen"
            )
        ]
    )

    # rqt_image_view (delayed 6s to let bridge start first)
    image_view = TimerAction(
        period=6.0,
        actions=[
            Node(
                package="rqt_image_view",
                executable="rqt_image_view",
                arguments=["/camera/image_raw"],
                output="screen"
            )
        ]
    )

    return LaunchDescription([
        sim,
        bridge,
        image_view,
    ])
