import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import numpy as np
import ast
import time
import ikpy.chain

JOINT_NAMES = [
    'shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
    'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint'
]

JOINT_LIMITS = [
    (-2*np.pi, 2*np.pi),
    (-np.pi, 0),
    (-np.pi, np.pi),
    (-np.pi, np.pi),
    (-np.pi, np.pi),
    (-np.pi, np.pi),
]

HOME_POSITION = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]

# Wrist points straight down (gripper fingers facing -Z)
TARGET_ORIENTATION = np.array([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, -1]
])

MAX_JOINT_STEP = 0.1

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        self.chain = ikpy.chain.Chain.from_urdf_file(
            '/tmp/robot.urdf',
            base_elements=['base_link'],
            active_links_mask=[False, False, True, True, True, True, True, True, False]
        )
        self.current_joints = [0.0] * 6
        self.pub = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.create_subscription(JointState, '/joint_states', self.joint_cb, 10)
        self.create_subscription(String, '/vla_action', self.action_cb, 10)
        self.get_logger().info('Robot controller started')
        time.sleep(2.0)
        self.go_home()

    def go_home(self):
        traj = JointTrajectory()
        traj.joint_names = JOINT_NAMES
        point = JointTrajectoryPoint()
        point.positions = HOME_POSITION
        point.time_from_start.sec = 3
        traj.points = [point]
        self.pub.publish(traj)
        self.get_logger().info('Moving to home position')

    def joint_cb(self, msg):
        for i, name in enumerate(JOINT_NAMES):
            if name in msg.name:
                idx = msg.name.index(name)
                self.current_joints[i] = msg.position[idx]

    def action_cb(self, msg):
        action = ast.literal_eval(msg.data)
        dx, dy, dz = action[0], action[1], action[2]

        full_joints = [0.0, 0.0] + self.current_joints + [0.0]
        current_matrix = self.chain.forward_kinematics(full_joints)
        current_pos = current_matrix[:3, 3]

        target_pos = current_pos + np.array([dx, dy, dz])

        new_joints = self.chain.inverse_kinematics(
            target_pos,
            target_orientation=TARGET_ORIENTATION,
            orientation_mode="all",
            initial_position=full_joints
        )

        clamped = list(new_joints[1:7])
        for i in range(6):
            delta = clamped[i] - self.current_joints[i]
            delta = float(np.clip(delta, -MAX_JOINT_STEP, MAX_JOINT_STEP))
            clamped[i] = self.current_joints[i] + delta

        for i, (low, high) in enumerate(JOINT_LIMITS):
            clamped[i] = float(np.clip(clamped[i], low, high))

        traj = JointTrajectory()
        traj.joint_names = JOINT_NAMES
        point = JointTrajectoryPoint()
        point.positions = clamped
        point.time_from_start.sec = 2
        point.time_from_start.nanosec = 0
        traj.points = [point]
        self.pub.publish(traj)

def main(args=None):
    rclpy.init(args=args)
    node = RobotController()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
