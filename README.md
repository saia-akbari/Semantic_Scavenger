# Semantic Scavenger
⚠️ **Work in progress.** This project is actively being developed and is not complete. The pipeline runs end-to-end, but grasping is still being implemented.
A vision-language-action (VLA) pipeline that lets a simulated robot arm pick up objects based on natural language instructions like "pick up the red block."
## What it does
A camera on the robot's wrist streams images to a remote VLA model (OpenVLA-7B), which interprets the scene plus a language instruction and outputs end-effector deltas. Those get converted to joint commands via inverse kinematics and executed in Gazebo.
