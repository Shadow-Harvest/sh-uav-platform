"""
Vehicle Controller - Lifecycle node for UAV control.

Responsibilities:
- 20Hz setpoint streaming (keeps GUIDED mode alive)
- Position/velocity command interface
- Action servers for Takeoff, Land, HoldPosition (future)
"""

import time
import rclpy

from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from uav_msgs.action import Takeoff


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

        # Create QOS profile matching MAVROS
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Subscribe to current position from MAVROS
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/mavros/local_position/pose',
            self._pose_callback,
            sensor_qos
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
        
        # MAVROS service clients
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')
        self.takeoff_client = self.create_client(CommandTOL, '/mavros/cmd/takeoff')
        
        # Takeoff action server
        self.takeoff_server = ActionServer(
            self,
            Takeoff,
            'vehicle/takeoff',
            execute_callback=self._execute_takeoff
        )
        self.get_logger().info('Takeoff action server initialized.')
        
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
    
    def set_target_position(self, x: float, y: float, z: float):
        """Set the target position for the vehicle."""
        if self.target_pose is None:
           return
        
        self.target_pose.pose.position.x = x
        self.target_pose.pose.position.y = y
        self.target_pose.pose.position.z = z
    
    def _pose_callback(self, msg: PoseStamped):
        """Callback to update current pose."""
        self.current_pose = msg
        
    def _publish_setpoint(self):
        """Publish the current target pose as setpoint."""
        if self.setpoint_pub is not None and self.target_pose is not None:
            self.target_pose.header.stamp = self.get_clock().now().to_msg()
            self.setpoint_pub.publish(self.target_pose)
            
    def _execute_takeoff(self, goal_handle: ServerGoalHandle):
        """Execute takeoff action."""
        self.get_logger().info('Takeoff action requested.')
        
        target_altitude = goal_handle.request.target_altitude_m
        timeout = goal_handle.request.timeout_sec
        
        self.get_logger().info(f'Taking off to altitude: {target_altitude} meters. Timeout: {timeout} seconds.')
        
        # Step 1: Set GUIDED mode
        if not self._set_mode('GUIDED'):
            goal_handle.abort()
            return Takeoff.Result(success=False, message='Failed to set GUIDED mode.')
        
        # Step 2: Set target altitude (keeping current x,y)
        current_x = 0.0
        current_y = 0.0
        if self.current_pose is not None:
            current_x = self.current_pose.pose.position.x
            current_y = self.current_pose.pose.position.y
            
        self.set_target_position(current_x, current_y, target_altitude)
        
        # Step 3: Arm the vehicle
        if not self._arm_vehicle(True):
            goal_handle.abort()
            return Takeoff.Result(success=False, message='Failed to arm vehicle.')
        
        # Step 4: Monitor altitude until reached or timeout
        feedback = Takeoff.Feedback()
        start_time = self.get_clock().now()
        
        while rclpy.ok():
            # Get current altitude
            current_alt = 0.0
            if self.current_pose is not None:
                current_alt = self.current_pose.pose.position.z
                
            # Publish feedback
            feedback.current_altitude_m = current_alt
            feedback.progress_percent = min(100.0, (current_alt / target_altitude) * 100.0)
            goal_handle.publish_feedback(feedback)
            
            # Check if target altitude reached (within 0.2m tolerance)
            if current_alt >= target_altitude - 0.2:
                self.get_logger().info('Target altitude reached.')
                goal_handle.succeed()
                return Takeoff.Result(success=True, message='Takeoff successful.', final_altitude_m=current_alt)
            
            # Check for timeout
            elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
            if timeout > 0 and elapsed > timeout:
                self.get_logger().info('Takeoff timed out.')
                goal_handle.abort()
                return Takeoff.Result(success=False, message='Takeoff timed out.', final_altitude_m=current_alt)
            
            rclpy.spin_once(self, timeout_sec=0.1)

    def _set_mode(self, mode: str) -> bool:
        """Set the vehicle mode via MAVROS."""
        if not self.mode_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('Mode service not available.')
            return False

        request = SetMode.Request()
        request.custom_mode = mode
        
        future = self.mode_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if future.result() is not None:
            success = future.result().mode_sent
            self.get_logger().info(f'Mode set to {mode}: {success}')
            return success
        
        self.get_logger().error('Failed to call mode service.')
        return False
    
    def _arm_vehicle(self, arm: bool) -> bool:
        """Arm the vehicle via MAVROS."""
        if not self.arm_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('Arming service not available.')
            return False

        request = CommandBool.Request()
        request.value = arm
        
        future = self.arm_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if future.result() is not None:
            success = future.result().success
            action = 'Armed' if arm else 'Disarmed'
            self.get_logger().info(f'Vehicle {action}: {success}')
            return success
        
        self.get_logger().error('Arming service call failed.')
        return False
    
        
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
