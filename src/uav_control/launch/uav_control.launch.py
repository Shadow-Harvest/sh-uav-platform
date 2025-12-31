"""
Launch file for uav_control package.

Launches VehicleStateNode and VehicleController as lifecycle nodes,
then automatically configures and activates them.
"""

from launch import LaunchDescription
from launch_ros.actions import LifecycleNode
from launch_ros.events.lifecycle import ChangeState
from launch.actions import EmitEvent, RegisterEventHandler, LogInfo
from launch.event_handlers import OnProcessStart
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    """Generate launch description for uav_control nodes."""

    # Vehicle State Node (lifecycle)
    vehicle_state_node = LifecycleNode(
        package='uav_control',
        executable='vehicle_state_node',
        name='vehicle_state',
        namespace='',
        output='screen',
    )

    # Vehicle Controller Node (lifecycle)
    vehicle_controller_node = LifecycleNode(
        package='uav_control',
        executable='vehicle_controller',
        name='vehicle_controller',
        namespace='',
        output='screen',
    )

    # Auto-configure vehicle_state after it starts
    configure_vehicle_state = RegisterEventHandler(
        OnProcessStart(
            target_action=vehicle_state_node,
            on_start=[
                LogInfo(msg='vehicle_state started, configuring...'),
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=lambda node: node == vehicle_state_node,
                        transition_id=Transition.TRANSITION_CONFIGURE,
                    )
                ),
            ],
        )
    )

    # Auto-configure vehicle_controller after it starts
    configure_vehicle_controller = RegisterEventHandler(
        OnProcessStart(
            target_action=vehicle_controller_node,
            on_start=[
                LogInfo(msg='vehicle_controller started, configuring...'),
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=lambda node: node == vehicle_controller_node,
                        transition_id=Transition.TRANSITION_CONFIGURE,
                    )
                ),
            ],
        )
    )

    return LaunchDescription([
        vehicle_state_node,
        vehicle_controller_node,
        configure_vehicle_state,
        configure_vehicle_controller,
    ])
