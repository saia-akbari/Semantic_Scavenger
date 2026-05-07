import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import requests, base64, json
import cv2
from cv_bridge import CvBridge

class VLABridgeNode(Node):
    def __init__(self):
        super().__init__('vla_bridge')
        self.bridge = CvBridge()
        self.instruction = "pick up the red object"
        
        # Subscribe to camera
        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        
        # Publish action
        self.pub = self.create_publisher(String, '/vla_action', 10)
        self.get_logger().info('VLA Bridge Node started!')

    def image_callback(self, msg):
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Encode to base64
            _, buf = cv2.imencode('.jpg', cv_image)
            b64 = base64.b64encode(buf).decode()
            
            # Send to HiPerGator OpenVLA server
            response = requests.post(
                "https://catchy-gallstone-outthink.ngrok-free.dev/predict",
                json={"image_b64": b64, "instruction": self.instruction},
                timeout=30.0,
		headers={"ngrok-skip-browser-warning": "true"},
            )
            
            action = response.json()["action"]
            self.get_logger().info(f'Action received: {action}')
            
            # Publish action
            msg_out = String()
            msg_out.data = json.dumps(action)
            self.pub.publish(msg_out)
            
        except Exception as e:
            self.get_logger().warn(f'VLA call failed: {e}')

def main():
    rclpy.init()
    node = VLABridgeNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
