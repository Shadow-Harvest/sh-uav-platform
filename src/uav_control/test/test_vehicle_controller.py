"""Tests for VehicleController."""

import time
import pytest
import rclpy
from unittest.mock import MagicMock, patch
from geometry_msgs.msg import PoseStamped
from uav_control.vehicle_controller import VehicleController


@pytest.fixture(scope="module")
def rclpy_init():
    """Initialize rclpy once for all tests."""
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node(rclpy_init):
    """Create a fresh node for each test."""
    node = VehicleController()
    yield node
    node.destroy_node()


# TODO: Test that node constantly publishes setpoints when armed and in GUIDED mode.

class TestTakeoffSetpointPublishing:
    def test_publish_setpoint_sets_current_timestamp(self, node):
        """Published setpoint must have current timestamp."""
        node.setpoint_pub = MagicMock()
        node.target_pose = PoseStamped()
        
        before = node.get_clock().now()
        node._publish_setpoint()
        after = node.get_clock().now()
        
        published_msg = node.setpoint_pub.publish.call_args[0][0]
        stamp = published_msg.header.stamp
        # Verify timestamp is between before and after
        msg_time = stamp.sec + stamp.nanosec / 1e9
        before_time = before.nanoseconds / 1e9
        after_time = after.nanoseconds / 1e9
        
        assert before_time <= msg_time <= after_time

    def test_publish_setpoint_publishes_stamped_pose(self, node):
        """Publish setpoint must publish a PoseStamped message."""
        node.setpoint_pub = MagicMock()
        node.target_pose = PoseStamped()
        
        node._publish_setpoint()
        
        assert node.setpoint_pub.publish.called, (
            "Publish setpoint must call publisher's publish() method"
        )
        published_msg = node.setpoint_pub.publish.call_args[0][0]
        assert isinstance(published_msg, PoseStamped), (
            "Published message must be of type PoseStamped"
        )

class TestTakeoffCallbackProcessing:
    """Test callback processing during takeoff."""

    def test_takeoff_loop_calls_spin_once(self, node):
        """Loop must call spin_once() to process pose callbacks."""
        node.on_configure(MagicMock())
        
        node._set_mode = MagicMock(return_value=True)
        node._arm_vehicle = MagicMock(return_value=True)
        node._mavros_takeoff = MagicMock(return_value=True)
        
        goal_handle = MagicMock()
        goal_handle.request.target_altitude_m = 5.0
        goal_handle.request.timeout_sec = 0.2

        with patch('uav_control.vehicle_controller.rclpy.spin_once') as mock_spin:
            mock_spin.side_effect = lambda n, timeout_sec=0.1: time.sleep(timeout_sec)
            node._execute_takeoff(goal_handle)
        
        assert mock_spin.called, (
            "Loop must call spin_once() to process callbacks, not time.sleep()"
        )
