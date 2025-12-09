"""
Vehicle State Node - Lifecycle node managing vehicle state and FSM.
"""

from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn
from mavros_msgs.msg import State as MavrosState
from uav_control.vehicle_fsm import VehicleFSM


class VehicleStateNode(LifecycleNode):
    """Lifecycle node managing vehicle state and FSM."""

    def __init__(self):
        super().__init__('vehicle_state')
        self.get_logger().info('VehicleStateNode created (unconfigured)')
        
        # Will be initialized in on_configure
        self.fsm = None
        
        # MAVROS
        self.mavros_stat_sub = None
        self.is_connected = False
        self.is_armed = False
        self.is_guided = False
        
        
    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Configure the node and initialize the FSM."""
        self.get_logger().info('Configuring VehicleStateNode...')
        
        # Initialize the FSM
        self.fsm = VehicleFSM(self)
        self.get_logger().info('Vehicle FSM initialized.')
        
        #MAVROS
        self.mavros_stat_sub = self.create_subscription(
            MavrosState,
            '/mavros/state',
            self.mavros_state_callback,
            10
        )
        self.get_logger().info('Subscribed to /mavros/state topic.')
        
        self.get_logger().info('Configuration complete!')
        return TransitionCallbackReturn.SUCCESS
    
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Activate the node."""
        self.get_logger().info('Activating VehicleStateNode...')
        self.get_logger().info('VehicleStateNode activated!')
        return TransitionCallbackReturn.SUCCESS
    
    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Deactivate the node."""
        self.get_logger().info('Deactivating VehicleStateNode...')
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