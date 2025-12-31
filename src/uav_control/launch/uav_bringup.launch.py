"""
Bringup launch file for uav_control package.

Launches VehicleStateNode and VehicleController, then automatically
configures AND activates them for immediate use.

Usage:
  ros2 launch uav_control uav_bringup.launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import LifecycleNode
from launch_ros.events.lifecycle import ChangeState
from launch.actions import EmitEvent, RegisterEventHandler, LogInfo, TimerAction
from launch.event_handlers import OnProcessStart
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    """Generate launch description with full lifecycle bringup."""

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

    # Auto-configure and activate vehicle_state after it starts
    bringup_vehicle_state = RegisterEventHandler(
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
                # Delay activation to allow configure to complete
                TimerAction(
                    period=1.0,
                    actions=[
                        LogInfo(msg='Activating vehicle_state...'),
                        EmitEvent(
                            event=ChangeState(
                                lifecycle_node_matcher=lambda node: node == vehicle_state_node,
                                transition_id=Transition.TRANSITION_ACTIVATE,
                            )
                        ),
                    ],
                ),
            ],
        )
    )

    # Auto-configure and activate vehicle_controller after it starts
    bringup_vehicle_controller = RegisterEventHandler(
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
                # Delay activation to allow configure to complete
                TimerAction(
                    period=1.0,
                    actions=[
                        LogInfo(msg='Activating vehicle_controller...'),
                        EmitEvent(
                            event=ChangeState(
                                lifecycle_node_matcher=lambda node: node == vehicle_controller_node,
                                transition_id=Transition.TRANSITION_ACTIVATE,
                            )
                        ),
                    ],
                ),
            ],
        )
    )

    return LaunchDescription([
        vehicle_state_node,
        vehicle_controller_node,
        bringup_vehicle_state,
        bringup_vehicle_controller,
    ])
