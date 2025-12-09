"""
Vehicle State Node - Lifecycle node managing vehicle state and FSM.
"""

from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn
from mavros_msgs.msg import State as MavrosState
from uav_control.vehicle_fsm import VehicleFSM
from uav_msgs.msg import VehicleState


class VehicleStateNode(LifecycleNode):
    """Lifecycle node managing vehicle state and FSM."""

    def __init__(self):
        super().__init__('vehicle_state')
        self.get_logger().info('VehicleStateNode created (unconfigured)')
        
        # Will be initialized in on_configure
        self.fsm = None
        
        # MAVROS
        self.mavros_state_sub = None
        self.is_connected = False
        self.is_armed = False
        self.is_guided = False
        
        # Vehicle State Publisher
        self.state_pub = None
        self.state_timer = None
        
        
    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Configure the node and initialize the FSM."""
        self.get_logger().info('Configuring VehicleStateNode...')
        
        # Initialize the FSM
        self.fsm = VehicleFSM(self)
        self.get_logger().info('Vehicle FSM initialized.')
        
        #MAVROS
        self.mavros_state_sub = self.create_subscription(
            MavrosState,
            '/mavros/state',
            self._mavros_state_callback,
            10
        )
        self.get_logger().info('Subscribed to /mavros/state topic.')
        
        # Vehicle State Publisher
        self.state_pub = self.create_publisher(VehicleState, 'vehicle/state', 10)
        self.get_logger().info('Vehicle state publisher created on vehicle/state topic.')
        
        self.get_logger().info('Configuration complete!')
        return TransitionCallbackReturn.SUCCESS
    
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Activate the node."""
        self.get_logger().info('Activating VehicleStateNode...')
        
        self.state_timer = self.create_timer(0.1, self._publish_state)  # 10 Hz update rate
        self.get_logger().info('Vehicle state publisher activated. (10 Hz)')
        
        self.get_logger().info('VehicleStateNode activated!')
        return TransitionCallbackReturn.SUCCESS
    
    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Deactivate the node."""
        self.get_logger().info('Deactivating VehicleStateNode...')
        
        if self.state_timer:
            self.state_timer.cancel()
            self.state_timer = None
        self.get_logger().info('Vehicle state publisher deactivated.')
        
        self.get_logger().info('VehicleStateNode deactivated!')
        return TransitionCallbackReturn.SUCCESS
    
    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Cleanup the node and FSM."""
        self.get_logger().info('Cleaning up VehicleStateNode...')
        
        self.fsm = None
        
        self.get_logger().info('Cleanup complete!')
        return TransitionCallbackReturn.SUCCESS
    
    def _mavros_state_callback(self, msg: MavrosState):
        """Handle incoming MAVROS state messages."""
        self.is_connected = msg.connected
        self.is_armed = msg.armed
        self.is_guided = (msg.mode == 'GUIDED')
        
        self.get_logger().debug(
            f'MAVROS State - Connected: {self.is_connected}, Armed: {self.is_armed}, Guided: {self.is_guided}'
        )
        
    def _publish_state(self):
        """Publish the current vehicle state."""
        if not self.state_pub:
            return
        
        vehicle_state_msg = VehicleState()
        vehicle_state_msg.header.stamp = self.get_clock().now().to_msg()
        vehicle_state_msg.header.frame_id = 'base_link'
        
        vehicle_state_msg.fsm_state = self._fsm_state_to_msg()
        
        vehicle_state_msg.is_armed = self.is_armed
        vehicle_state_msg.is_guided = self.is_guided
        
        self.state_pub.publish(vehicle_state_msg)
        self.get_logger().debug('Published vehicle state message.')
        
    def _fsm_state_to_msg(self) -> int:
        """Convert FSM state to VehicleState message enum."""
        
        if self.fsm is None:
            return VehicleState.STATE_UNINITIALIZED
        
        state_map = {
            'disarmed': VehicleState.STATE_DISARMED,
            'armed': VehicleState.STATE_ARMED,
            'taking_off': VehicleState.STATE_TAKING_OFF,
            'hovering': VehicleState.STATE_FLYING,  # hovering is a type of flying
            'flying': VehicleState.STATE_FLYING,
            'landing': VehicleState.STATE_LANDING,
            'emergency': VehicleState.STATE_EMERGENCY,
        }
        
        return state_map.get(self.fsm.current_state.id, VehicleState.STATE_UNINITIALIZED)
    
    
def main(args=None):
    import rclpy
    
    rclpy.init(args=args)
    
    vehicle_state_node = VehicleStateNode()
    
    try:
        rclpy.spin(vehicle_state_node)
    except KeyboardInterrupt:
        pass
    finally:
        vehicle_state_node.destroy_node()
        rclpy.shutdown()
        
if __name__ == '__main__':
    main()