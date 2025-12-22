"""Tests for VehicleController."""

import time
import pytest
import rclpy
from unittest.mock import MagicMock, patch

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
