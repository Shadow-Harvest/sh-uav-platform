"""
Vehicle Controller - Lifecycle node for UAV control.

Responsibilities:
- 20Hz setpoint streaming (keeps GUIDED mode alive)
- Position/velocity command interface
- Action servers for Takeoff, Land, HoldPosition (future)
"""

from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn
from geometry_msgs.msg import PoseStamped


class VehicleController(LifecycleNode):
    """Lifecycle node for UAV control."""

    def __init__(self):
        super().__init__('vehicle_controller')
        self.get_logger().info('VehicleController created (unconfigured)')
        
        # Current state (from MAVROS)
        self.current_pose = None
        
        # Target state
        self.target_pose = None
        
        # Pulishers
        self.setpoint_pub = None
        
        # Subscribers
        self.pose_sub = None
        
        # Timer
        self.setpoint_timer = None
        
    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Configure subscribers and publishers."""
        self.get_logger().info('Configuring VehicleController...')

        # Subscribe to current position from MAVROS
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/mavros/local_position/pose',
            self._pose_callback,
            10
        )
        
        # Publisher for setpoints
        self.setpoint_pub = self.create_publisher(
            PoseStamped,
            '/mavros/setpoint_position/local',
            10
        )
        
        # Initialize target to origin
        self.target_pose = PoseStamped()
        self.target_pose.header.frame_id = 'map'
        self.target_pose.pose.position.z = 0.0
        
        self.get_logger().info('VehicleController configured.')
        return TransitionCallbackReturn.SUCCESS
        
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Activate publishers and start setpoint timer."""
        self.get_logger().info('Activating VehicleController...')
        
        # Start timer for 20Hz setpoint publishing
        self.setpoint_timer = self.create_timer(0.05, self._publish_setpoint)
        
        self.get_logger().info('Setpoint streaming started at 20Hz.')
        return TransitionCallbackReturn.SUCCESS
    
    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Deactivate publishers and stop setpoint timer."""
        self.get_logger().info('Deactivating VehicleController...')
        
        # Stop the timer
        if self.setpoint_timer is not None:
            self.setpoint_timer.cancel()
            self.setpoint_timer = None
        
        self.get_logger().info('Setpoint streaming stopped.')
        return TransitionCallbackReturn.SUCCESS
    
    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Cleanup resources."""
        self.get_logger().info('Cleaning up VehicleController...')
        
        self.current_pose = None
        return TransitionCallbackReturn.SUCCESS
    
    def _pose_callback(self, msg: PoseStamped):
        """Callback to update current pose."""
        self.current_pose = msg
        
    def _publish_setpoint(self):
        """Publish the current target pose as setpoint."""
        if self.setpoint_pub is not None and self.target_pose is not None:
            self.target_pose.header.stamp = self.get_clock().now().to_msg()
            self.setpoint_pub.publish(self.target_pose)
        
def main(args=None):
    import rclpy
    rclpy.init(args=args)
    node = VehicleController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        


if __name__ == '__main__':
    main()
