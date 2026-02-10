import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_pose


class TFTransform(Node):

    def __init__(self):
        super().__init__('tf_transform_node')

        # TF buffer + listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Subscriber → object pose in camera frame
        self.sub = self.create_subscription(
            PoseStamped,
            '/object_pose_camera',
            self.pose_callback,
            10
        )

        # Publisher → pose in base frame
        self.pub = self.create_publisher(
            PoseStamped,
            '/object_pose_base',
            10
        )

    def pose_callback(self, msg):

        try:
            # Get transform camera → base
            transform = self.tf_buffer.lookup_transform(
                'base_link',
                'camera_link',
                rclpy.time.Time()
            )

            # Transform pose
            pose_base = do_transform_pose(msg, transform)

            self.pub.publish(pose_base)

            self.get_logger().info(
                'Pose transformed to base frame'
            )

        except Exception as e:
            self.get_logger().warn(str(e))


def main():
    rclpy.init()
    node = TFTransform()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
